from app.db.mongo import dummy_df, dpr_dummy_df, dpr2_dummy_df
from app.services.signature_service import verify_signature
from app.core.logging_config import logger


class WebhookProcessor:
    @staticmethod
    async def process_webhook_event(payload: dict, signature: str) -> str:
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
        logger.debug(f"Received signature: {signature}")

        if not signature:
            raise ValueError("Missing signature header")

        if not verify_signature(payload, signature):
            raise ValueError("Invalid signature")

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
        return response_status
