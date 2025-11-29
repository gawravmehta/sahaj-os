from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-notice"

    SECRET_KEY: str
    NOTICE_ACCESS_TOKEN_EXPIRE_HOURS: int = 1

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USERNAME: str = "default"
    REDIS_MAX_CONNECTIONS: int = 200
    REDIS_MAX_CONNECTIONS_PER_NODE: int = 50

    MONGO_URI: str
    DB_NAME_CONCUR_MASTER: str = "concur_master_test"

    POSTGRES_DATABASE_URL: str

    S3_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    NOTICE_WORKER_BUCKET: str = "notice-worker-dev"
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
