import os
from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-cookie-consent"
    MONGO_URL: str
    DATABASE_NAME: str = "concur_master_test_cookie"
    COLLECTIONS_RECORDS: str = "consent_audit_records"
    COLLECTION_COUNT: str = "user_preferences_current"
    RATE_LIMIT_DEFAULT: str = "5/minute, 60/hour"
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="ignore")


settings = Settings()
