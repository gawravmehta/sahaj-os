from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    """
    Centralized application settings.
    All sensitive values must come from environment variables (.env).
    """

    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-customer-portal"

    CUSTOMER_PORTAL_FRONTEND_URL: str
    CMP_ADMIN_BACKEND_URL: str

    POSTGRES_DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USERNAME: str
    REDIS_MAX_CONNECTIONS: int = 200
    REDIS_MAX_CONNECTIONS_PER_NODE: int = 50

    MONGO_URI: str
    DB_NAME_CONCUR_MASTER: str
    DB_NAME_CONCUR_LOGS: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    OTP_EXPIRY_SECONDS: int = 300

    S3_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    S3_SECURE: bool = False
    MINIO_BROWSER_URL: str
    CUSTOMER_PORTAL_BUCKET: str
    KYC_DOCUMENTS_BUCKET: str

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_MANAGEMENT_PORT: int = 15672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST_NAME: str
    RABBITMQ_POOL_SIZE: int = 5

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
