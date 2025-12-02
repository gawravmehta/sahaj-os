from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging_config import logger

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
dummy_df = db["events"]

logger.info("MongoDB connection established and dummy_df collection initialized.")
