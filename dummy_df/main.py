# Standard library imports
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, UTC, timedelta
from typing import Optional

# Third-party imports
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configuration and Initialization ---
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["concur_master_test"]
dummy_df = db["dummy_df"]

# --- Global Variables ---
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_AUTH_HEADER = "X-Consent-Signature"
SERVICE_NAME = os.getenv("SERVICE_NAME")
CMS_ACK_URL = os.getenv("CMS_ACK_URL", "http://127.0.0.1:8001/api/v1/consent-artifact/consent-ack")
CMP_WEBHOOK_SECRET = os.getenv("CMP_WEBHOOK_SECRET", "cmp_webhook_secret")
VERIFICATION_ACK_URL = os.getenv("VERIFICATION_ACK_URL", "http://127.0.0.1:8001/api/v1/n/dp-verification-ack")


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Global request counter for failure simulation
REQUEST_COUNTER = 0

# --- FastAPI App Initialization ---
app = FastAPI()
scheduler = AsyncIOScheduler()

# --- Helper Functions ---
def verify_signature(payload: dict, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from headers."""
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    computed_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    logger.debug(f"Computed signature: {computed_sig}")
    return hmac.compare_digest(computed_sig, signature)


def generate_signature(payload: dict) -> str:
    """Generates HMAC-SHA256 signature for the payload."""
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hmac.new(
        CMP_WEBHOOK_SECRET.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_request(payload: dict, signature: str, timestamp_str: str) -> bool:
    """Verifies signature and checks for replay attacks (timestamp)."""
    if not signature:
        logger.warning("Missing signature for request verification.")
        return False

    try:
        req_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        if datetime.now(UTC) - req_time > timedelta(minutes=5):
            logger.warning("Request timestamp expired, possible replay attack.")
            return False
    except ValueError:
        logger.warning("Invalid timestamp format for request verification.")
        return False

    expected_sig = generate_signature(payload)
    return hmac.compare_digest(expected_sig, signature)


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"service_name": SERVICE_NAME, "webhook_secret": WEBHOOK_SECRET}


@app.post("/webhook")
async def receive_webhook(request: Request, x_consent_signature: Optional[str] = Header(None)):
    global REQUEST_COUNTER
    REQUEST_COUNTER += 1

    if REQUEST_COUNTER % 3 == 0:
        logger.error(f"FAILURE SIMULATION: Request #{REQUEST_COUNTER} is failing with 503 Service Unavailable.")
        raise HTTPException(
            status_code=503, detail=f"Simulated intermittent service failure on request #{REQUEST_COUNTER}. Please implement retry logic."
        )

    logger.info(f"SUCCESS: Processing Request #{REQUEST_COUNTER}")
    payload = await request.json()
    logger.info(f"Received payload: {payload}")

    await dummy_df.insert_one(
        {
            "payload": payload,
            "event": payload.get("event"),
            "timestamp": payload.get("timestamp"),
            "processed": False,
        }
    )
    logger.info("Payload saved to MongoDB dummy_df collection.")
    logger.debug(f"Received signature: {x_consent_signature}")

    if not x_consent_signature:
        raise HTTPException(status_code=401, detail="Missing signature header")

    if not verify_signature(payload, x_consent_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = payload.get("event")
    logger.info(f"Received event type: {event_type}\n")

    response_status = "ok"
    if event_type == "WEBHOOK_TEST":
        pass
    elif event_type == "consent_granted":
        logger.info(f"Consent granted for user {payload.get('dp_id')}\n")
    elif event_type == "consent_withdrawn":
        logger.info(f"Consent revoked for user {payload.get('dp_id')}\n")
    elif event_type == "consent_expired":
        logger.info(f"Consent expired for user {payload.get('dp_id')}\n")
    elif event_type == "data_erasure_retention_triggered":
        logger.info(f"Data erasure retention triggered for user {payload.get('dp_id')}\n")
    else:
        logger.warning(f"Unknown event type: {event_type}\n")
        response_status = "unknown_event_type"

    return {"status": response_status, "request_number": REQUEST_COUNTER}


# --- Scheduler Tasks ---
async def process_and_ack_consents():
    """
    1. Finds unprocessed events.
    2. 'Halts' processing (Logic implementation).
    3. Sends Signed ACK to CMS.
    4. Updates DB on success.
    """
    logger.info("Scheduler: Checking for pending consent events...")

    query = {"processed": False, "event": {"$in": ["consent_expired", "consent_withdrawn"]}}
    count = await dummy_df.count_documents(query)
    logger.info(f"Found {count} pending consent events.")

    cursor = dummy_df.find(query)

    async for doc in cursor:
        dp_id = doc["payload"]["dp_id"]
        event_type = doc["event"]

        logger.info(f"Processing halting for DP ID: {dp_id}, Event: {event_type}")

        for purpose in doc["payload"]["purposes"]:
            de_id = purpose["de_id"]
            purpose_id = purpose["purpose_id"]

            ack_payload = {
                "dp_id": dp_id,
                "original_event_type": event_type,
                "ack_status": "HALTED",
                "ack_timestamp": datetime.now(UTC).isoformat(),
                "message": "Data processing has been stopped for this purpose.",
                "de_id": de_id,
                "purpose_id": purpose_id,
            }

            signature = generate_signature(ack_payload)
            headers = {"X-DF-Signature": signature, "Content-Type": "application/json"}

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(CMS_ACK_URL, json=ack_payload, headers=headers, timeout=10.0)

                if response.status_code == 200:
                    await dummy_df.update_one({"_id": doc["_id"]}, {"$set": {"processed": True, "ack_sent": True, "ack_timestamp": datetime.now()}})
                    logger.info(f"SUCCESS: ACK sent and confirmed for {dp_id}")
                else:
                    logger.error(f"FAILED ACK for {dp_id}: CMS responded {response.status_code} - {response.text}")

            except httpx.RequestError as exc:
                logger.error(f"Network error while sending ACK for {dp_id}: {exc}")


async def process_and_ack_data_erasure():
    """
    1. Finds unprocessed events.
    2. Acks data erasure.
    3. Sends Signed ACK to CMS.
    4. Updates DB on success.
    """
    logger.info("Scheduler: Checking for pending data erasure events...")

    query = {"processed": False, "event": {"$in": ["data_erasure_retention_triggered"]}}
    count = await dummy_df.count_documents(query)
    logger.info(f"Found {count} pending data erasure events.")

    cursor = dummy_df.find(query)

    async for doc in cursor:
        dp_id = doc["payload"]["dp_id"]
        event_type = doc["event"]

        logger.info(f"Processing data erasure for DP ID: {dp_id}, Event: {event_type}")

        for purpose in doc["payload"]["purposes"]:
            de_id = purpose["de_id"]
            purpose_id = purpose["purpose_id"]

            ack_payload = {
                "dp_id": dp_id,
                "original_event_type": event_type,
                "ack_status": "HALTED",
                "ack_timestamp": datetime.now(UTC).isoformat(),
                "message": "Data processing has been deleted.",
                "de_id": de_id,
                "purpose_id": purpose_id,
            }

            signature = generate_signature(ack_payload)
            headers = {"X-DF-Signature": signature, "Content-Type": "application/json"}

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(CMS_ACK_URL, json=ack_payload, headers=headers, timeout=10.0)

                if response.status_code == 200:
                    await dummy_df.update_one({"_id": doc["_id"]}, {"$set": {"processed": True, "ack_sent": True, "ack_timestamp": datetime.now()}})
                    logger.info(f"SUCCESS: ACK sent and confirmed for {dp_id}")
                else:
                    logger.error(f"FAILED ACK for {dp_id}: CMS responded {response.status_code} - {response.text}")

            except httpx.RequestError as exc:
                logger.error(f"Network error while sending ACK for {dp_id}: {exc}")


async def process_and_ack_verification():
    """
    1. Finds unprocessed consent_granted events.
    2. Sends Signed ACK to Backend Notice.
    3. Updates DB on success.
    """
    logger.info("Scheduler: Checking for pending verification events...")

    query = {"verification_sent": {"$ne": True}, "event": "consent_granted"}
    count = await dummy_df.count_documents(query)
    logger.info(f"Found {count} pending verification events.")

    cursor = dummy_df.find(query)

    async for doc in cursor:
        dp_id = doc["payload"]["dp_id"]
        df_id = doc["payload"]["df_id"]
        request_id = doc["payload"]["request_id"]

        logger.info(f"Processing verification for DP ID: {dp_id}")

        ack_payload = {
            "dp_id": dp_id,
            "df_id": df_id,
            "request_id": request_id,
            "ack_timestamp": datetime.now(UTC).isoformat(),
        }

        signature = generate_signature(ack_payload)
        headers = {"X-DF-Signature": signature, "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(VERIFICATION_ACK_URL, json=ack_payload, headers=headers, timeout=10.0)

            if response.status_code == 200:
                await dummy_df.update_one({"_id": doc["_id"]}, {"$set": {"verification_sent": True, "verification_timestamp": datetime.now()}})
                logger.info(f"SUCCESS: Verification ACK sent and confirmed for {dp_id}")
            else:
                logger.error(f"FAILED Verification ACK for {dp_id}: Backend responded {response.status_code} - {response.text}")

        except httpx.RequestError as exc:
            logger.error(f"Network error while sending Verification ACK for {dp_id}: {exc}")


# --- Scheduler Startup ---
@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(process_and_ack_consents, "interval", minutes=1)
    scheduler.add_job(process_and_ack_data_erasure, "interval", minutes=1)
    scheduler.add_job(process_and_ack_verification, "interval", minutes=1)
    scheduler.start()
