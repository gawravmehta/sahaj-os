from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    """
    Centralized application settings.
    All sensitive values must come from environment variables (.env).
    """

    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-customer-portal"

    FRONTEND_CUSTOMER_PORTAL: str
    BACKEND_CMP_ADMIN_URL: str
    POSTGRES_DATABASE_URL: str

    SECRET_KEY: str

    REDIS_STARTUP_NODES: List[Dict[str, Any]]
    REDIS_PASSWORD: str
    REDIS_USERNAME: str
    REDIS_MAX_CONNECTIONS: int = 200
    REDIS_MAX_CONNECTIONS_PER_NODE: int = 50

    MONGO_MASTER_URI: str
    MONGO_MASTER_DB_NAME: str

    DB_NAME_CONCUR_LOGS: str

    JWT_SECRET_KEY: str
    JWT_EXPIRY_MINUTES: int = 1440
    OTP_EXPIRY_SECONDS: int = 300

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_SECURE: bool = False

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_MANAGEMENT_PORT: int = 15672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST_NAME: str
    RABBITMQ_POOL_SIZE: int = 5

    KYC_DOCUMENTS_BUCKET: str

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
