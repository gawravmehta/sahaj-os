from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException

from app.core.config import settings
from app.core.logging_config import logger
from app.services.webhook_processor import WebhookProcessor
from app.db.mongo import dummy_df, dpr_dummy_df, dpr2_dummy_df

router = APIRouter()

# Global request counter for failure simulation
REQUEST_COUNTER = 0


@router.get("/")
async def root():
    return {"service_name": settings.SERVICE_NAME}


async def get_all_events():
    logger.info("Fetching all events from dummy_df collection.")
    events = []
    async for doc in dummy_df.find():
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    logger.info(f"Retrieved {len(events)} events.")
    return events


@router.get("/events/df", response_model=List[Dict[str, Any]])
async def get_df_events():
    """
    Retrieve all events from the dummy_df collection.
    """
    return await get_all_events()


@router.get("/events/dp1", response_model=List[Dict[str, Any]])
async def get_dp1_events():
    """
    Retrieve all events from the dpr_dummy_df collection.
    """
    logger.info("Fetching all events from dpr_dummy_df collection.")
    events = []
    async for doc in dpr_dummy_df.find():
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    logger.info(f"Retrieved {len(events)} events.")
    return events


@router.get("/events/dp2", response_model=List[Dict[str, Any]])
async def get_dp2_events():
    """
    Retrieve all events from the dpr2_dummy_df collection.
    """
    logger.info("Fetching all events from dpr2_dummy_df collection.")
    events = []
    async for doc in dpr2_dummy_df.find():
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    logger.info(f"Retrieved {len(events)} events.")
    return events


@router.post("/webhook")
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

    try:
        response_status = await WebhookProcessor.process_webhook_event(payload, x_consent_signature)
    except ValueError as e:
        raise HTTPException(401, str(e))

    return {"status": response_status, "request_number": REQUEST_COUNTER}
