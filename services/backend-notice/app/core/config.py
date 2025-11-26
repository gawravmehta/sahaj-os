from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-notice"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1

    REDIS_STARTUP_NODES: List[Dict[str, Any]]
    REDIS_PASSWORD: str
    REDIS_USERNAME: str = "default"
    REDIS_MAX_CONNECTIONS: int = 200
    REDIS_MAX_CONNECTIONS_PER_NODE: int = 50

    MONGO_MASTER_URI: str
    MONGO_MASTER_DB_NAME: str = "concur_master_test"

    POSTGRESS_URL: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str = "notice-worker-dev"
    S3_SECURE: bool = False

    SMS_SENDER_ID: str = "CONCUR"

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_MANAGEMENT_PORT: int = 15672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST_NAME: str
    RABBITMQ_POOL_SIZE: int = 5

    PUBLIC_KEY_PEM: str
    PRIVATE_KEY_PEM: str
    SIGNING_KEY_ID: str = "cm-key-2025-01"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
