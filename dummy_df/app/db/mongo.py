from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging_config import logger

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
dummy_df = db["events"]
dpr_dummy_df = db["dpr_events"]
dpr2_dummy_df = db["dpr2_events"]

logger.info("MongoDB connection established and dummy_df collection initialized.")
