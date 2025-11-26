from fastapi import Request, Depends
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from app.core.config import settings
from app.crud.webhook_events_crud import WebhookEventCRUD


async def get_db_client(request: Request) -> AsyncIOMotorClient:
    """Provides the global MotorClient instance."""
    client = getattr(request.app.state, "motor_client", None)
    if client is None:
        raise RuntimeError("MongoDB client is not initialized.")
    return client


async def get_concur_master_db(
    client: AsyncIOMotorClient = Depends(get_db_client),
) -> AsyncIOMotorDatabase:
    """Provides the 'concur_master' database instance."""
    return client[settings.DB_NAME_CONCUR_MASTER]


async def get_de_template_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["de_templates"]


async def get_de_master_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["de_master"]


async def get_data_processors_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["data_processors"]


async def get_consent_purpose_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["purpose_master"]


async def get_purpose_master_translated_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["purpose_master_translated"]


async def get_purpose_template_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["purpose_templates"]


async def get_de_master_translated_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["de_master_translated"]


async def get_cp_master_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["cp_master"]


async def get_asset_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["asset_master"]


async def get_cookie_master(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["cookie_master"]


async def get_user_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["cmp_users"]


async def get_roles_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["roles"]


async def get_departments_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["departments"]


async def get_dp_file_processing_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dp_file_processing"]


async def get_system_admin_role_id(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> str:
    config = await db["app_config"].find_one({"key": "SYSTEM_ADMIN_ROLE_ID"})
    return config["value"] if config else None


async def get_user_invites_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["user_invites"]


async def get_df_register_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["df_register"]


async def get_df_keys_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["df_keys"]


async def get_grievance_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["grievances"]


async def get_webhooks_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["webhooks"]


async def get_batch_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["batch_process"]


async def get_notifications_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["notifications"]


async def get_notice_notification_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["notice_notification"]


async def get_vendor_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["vendor_master"]


async def get_webhook_events_crud(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> WebhookEventCRUD:
    collection = db["webhook_events"]
    return WebhookEventCRUD(collection)


async def get_concur_logs_db(
    client: AsyncIOMotorClient = Depends(get_db_client),
) -> AsyncIOMotorDatabase:
    """Provides the 'concur_logs' database instance."""
    return client[settings.DB_NAME_CONCUR_LOGS]


async def get_business_logs_collection() -> str:
    return "app-logs-business"


async def get_consent_artifact_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["consent_latest_artifacts"]


async def get_consent_audit_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["consent_audit_logs"]


async def get_consent_validation_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["consent_validation"]


async def get_consent_validation_files_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["consent_validation_files"]


async def get_validation_batch_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["validation_batch"]


async def get_dpar_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar"]


async def get_dpar_rules_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar_rules"]


async def get_dpar_settings_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar_settings"]


async def get_dpar_preflight_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar_preflight_checks"]


async def get_dpar_report_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar_reports"]


async def get_dpar_bulk_upload_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["dpar_bulk_upload"]


async def get_incident_management_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["incident_management"]


async def get_df_ack_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["df_ack"]


async def get_customer_notifications_collection(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return db["customer_notifications"]
