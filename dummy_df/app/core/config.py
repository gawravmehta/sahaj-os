import os
from dotenv import load_dotenv
from datetime import UTC

load_dotenv()


class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    DPR1_WEBHOOK_SECRET = os.getenv("DPR1_WEBHOOK_SECRET")
    DPR2_WEBHOOK_SECRET = os.getenv("DPR2_WEBHOOK_SECRET")
    WEBHOOK_AUTH_HEADER = "X-Consent-Signature"
    SERVICE_NAME = os.getenv("SERVICE_NAME", "concur-service")
    CMP_WEBHOOK_SECRET = os.getenv("CMP_WEBHOOK_SECRET", "cmp_webhook_secret")
    CMS_ACK_URL = os.getenv("CMS_ACK_URL", "http://127.0.0.1:8001/api/v1/consent-artifact/consent-ack")
    VERIFICATION_ACK_URL = os.getenv("VERIFICATION_ACK_URL", "http://127.0.0.1:8001/api/v1/n/dp-verification-ack")
    DB_NAME = os.getenv("DB_NAME")
    DATETIME_UTC = UTC


settings = Settings()
