from datetime import datetime

from app.db.mongo import dummy_df
from app.services.ack_service import AckService
from app.core.config import settings
from app.core.logging_config import logger

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
                "ack_timestamp": datetime.now(settings.DATETIME_UTC).isoformat(),
                "message": "Data processing has been deleted.",
                "de_id": de_id,
                "purpose_id": purpose_id,
            }

            try:
                response = await AckService.send_ack(
                    url=settings.CMS_ACK_URL,
                    payload=ack_payload,
                    ack_type="CMS"
                )

                if response.status_code == 200:
                    await dummy_df.update_one({"_id": doc["_id"]}, {"$set": {"processed": True, "ack_sent": True, "ack_timestamp": datetime.now()}})
                    logger.info(f"SUCCESS: ACK sent and confirmed for {dp_id}")
                else:
                    logger.error(f"FAILED ACK for {dp_id}: CMS responded {response.status_code} - {response.text}")

            except Exception as exc:
                logger.error(f"Network error while sending ACK for {dp_id}: {exc}")
