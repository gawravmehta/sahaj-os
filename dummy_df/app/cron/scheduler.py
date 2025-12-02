from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.cron.consent_ack_job import process_and_ack_consents
from app.cron.data_erasure_job import process_and_ack_data_erasure
from app.cron.verification_ack_job import process_and_ack_verification
from app.core.logging_config import logger

scheduler = AsyncIOScheduler()

def init_scheduler():
    scheduler.add_job(process_and_ack_consents, "interval", minutes=1)
    scheduler.add_job(process_and_ack_data_erasure, "interval", minutes=1)
    scheduler.add_job(process_and_ack_verification, "interval", minutes=1)
    scheduler.start()
    logger.info("Scheduler started with jobs for consent, data erasure, and verification acks.")
