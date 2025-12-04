from datetime import datetime

from app.db.mongo import dummy_df
from app.services.ack_service import AckService
from app.core.config import settings
from app.core.logging_config import logger


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

        logger.info(f"Processing verification for DP ID: {dp_id}")

        ack_payload = {
            "dp_id": dp_id,
            "df_id": df_id,
            "ack_timestamp": datetime.now(settings.DATETIME_UTC).isoformat(),
        }

        try:
            response = await AckService.send_ack(url=settings.VERIFICATION_ACK_URL, payload=ack_payload, ack_type="Backend Notice")

            if response.status_code == 200:
                await dummy_df.update_one({"_id": doc["_id"]}, {"$set": {"verification_sent": True, "verification_timestamp": datetime.now()}})
                logger.info(f"SUCCESS: Verification ACK sent and confirmed for {dp_id}")
            else:
                logger.error(f"FAILED Verification ACK for {dp_id}: Backend responded {response.status_code} - {response.text}")

        except Exception as exc:
            logger.error(f"Network error while sending Verification ACK for {dp_id}: {exc}")
