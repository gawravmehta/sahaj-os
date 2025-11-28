from fastapi import Depends, Request
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from app.core.config import settings


async def get_db_client(request: Request) -> AsyncIOMotorClient:
    client = getattr(request.app.state, "motor_client", None)
    if client is None:
        raise RuntimeError("MongoDB client is not initialized.")
    return client


async def get_concur_master_db(
    client: AsyncIOMotorClient = Depends(get_db_client),
) -> AsyncIOMotorDatabase:
    return client[settings.DB_NAME_CONCUR_MASTER]


def get_concur_master_db_direct(app) -> AsyncIOMotorDatabase:
    client: AsyncIOMotorClient = getattr(app.state, "motor_client", None)
    if client is None:
        raise RuntimeError("MongoDB client is not initialized.")
    return client[settings.DB_NAME_CONCUR_MASTER]


async def get_dpar_requests_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    return concur_master_db["dpar"]


async def get_dpar_rules_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'dpar_rules' collection."""
    return concur_master_db["dpar_rules"]


async def get_grievance_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'grievances' collection."""
    return concur_master_db["grievances"]


async def get_consent_artifact_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'consent_artifacts' collection."""
    return concur_master_db["consent_latest_artifacts"]


async def get_purpose_master_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'purpose_master' collection."""
    return concur_master_db["purpose_master"]


async def get_notifications_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'customer_notifications' collection."""
    return concur_master_db["customer_notifications"]


async def get_df_register_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'df_register' collection."""
    return concur_master_db["df_register"]


async def get_data_processors_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'vendor_master' collection."""
    return concur_master_db["vendor_master"]


async def get_renewal_collection(
    concur_master_db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> AsyncIOMotorCollection:
    """Provides the 'renewal_collection' collection."""
    return concur_master_db["renewal_notification"]


def get_consent_artifact_collection_direct(app) -> AsyncIOMotorCollection:
    return get_concur_master_db_direct(app)["consent_latest_artifacts"]


def get_notifications_collection_direct(app) -> AsyncIOMotorCollection:
    return get_concur_master_db_direct(app)["customer_notifications"]


def get_renewal_collection_direct(app) -> AsyncIOMotorCollection:
    return get_concur_master_db_direct(app)["renewal_notification"]


async def get_concur_logs_db(
    client: AsyncIOMotorClient = Depends(get_db_client),
) -> AsyncIOMotorDatabase:
    """Provides the 'concur_logs' database instance."""
    return client[settings.DB_NAME_CONCUR_LOGS]


async def get_business_logs_collection(db: AsyncIOMotorDatabase = Depends(get_concur_logs_db)) -> AsyncIOMotorCollection:
    return db["business_logs"]
