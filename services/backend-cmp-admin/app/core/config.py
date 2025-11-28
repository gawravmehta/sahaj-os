from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    ENVIRONMENT: str = "dev"
    SERVICE_NAME: str = "backend-cmp-admin"

    CMP_ADMIN_BACKEND_URL: str = "http://127.0.0.1:8000"
    CMP_ADMIN_FRONTEND_URL: str = "http://127.0.0.1:3000"
    CMP_NOTICE_WORKER_URL: str = "http://127.0.0.1:8001"
    COOKIE_CONSENT_URL: str = "http://127.0.0.1:8007"

    MONGO_URI: str
    DB_NAME_CONCUR_MASTER: str = "concur_master_test"
    DB_NAME_COOKIE_MANAGEMENT: str = "cookie_management_test"
    DB_NAME_CONCUR_LOGS: str = "concur_logs_test"

    DATA_VEDA_URL: str = "http://data-veda:8080"

    SUPERADMIN_EMAIL: str
    TEMPORARY_PASSWORD: str
    DF_ID: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    POSTGRES_DATABASE_URL: str

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    S3_URL: str
    S3_SECURE: bool = False

    NOTICE_WORKER_BUCKET: str = "notice-worker-dev"
    PROCESSED_FILES_BUCKET: str = "processed-files-dev-1"
    UNPROCESSED_FILES_BUCKET: str = "unprocessed-files-dev"
    UNPROCESSED_VERIFICATION_FILES_BUCKET: str = "unprocessed-verification-files-dev"
    FAILED_RECORDS_BUCKET: str = "failed-records-dev-1"
    FAILED_RECORDS_BUCKET_EXTERNAL: str = "failed-external"
    TRAINING_NUGGETS_BUCKET: str = "concur-training"
    KYC_DOCUMENTS_BUCKET: str = "kyc-documents-dev"
    DPAR_BULK_UPLOAD_BUCKET: str = "dpar-bulk-upload-dev"
    COOKIE_CONSENT_BUCKET: str = "cookie-consent-scripts"

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_MANAGEMENT_PORT: int = 15672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST_NAME: str
    RABBITMQ_POOL_SIZE: int = 5

    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_RETRY_TTL_MS: int = 10000

    OPENSEARCH_HOST: str
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USERNAME: str

    PUBLIC_KEY_PEM: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
