from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorCollection

from app.api.v1.deps import get_current_user
from app.db.dependencies import get_consent_artifact_collection, get_dpar_requests_collection, get_grievance_collection
from app.services.consent_transaction_service import ConsentTransactionService
from app.core.logger import app_logger

router = APIRouter()


@router.get("/get-all-consent-transactions")
async def get_all_consent_transactions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
):
    app_logger.info(f"API Call: /get-all-consent-transactions for dp_id: {current_user.get('dp_id')}")
    service = ConsentTransactionService(consent_artifact_collection)
    return await service.get_all_consent_transactions(
        dp_id=current_user.get("dp_id"),
    )


@router.get("/get-consent-transaction/{agreement_id}")
async def get_consent_transaction(
    request: Request,
    agreement_id: str,
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
):
    app_logger.info(f"API Call: /get-consent-transaction/{agreement_id} for dp_id: {current_user.get('dp_id')}")
    service = ConsentTransactionService(consent_artifact_collection)
    return await service.get_consent_transaction(agreement_id)


@router.get("/data-elements/by-dp")
async def get_data_elements_by_dp(
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
):
    app_logger.info(f"API Call: /data-elements/by-dp for dp_id: {current_user.get('dp_id')}")
    service = ConsentTransactionService(consent_artifact_collection)
    return await service.extract_highest_version_data_elements(
        dp_id=current_user.get("dp_id"),
    )


@router.get("/preference-counts/by-dp")
async def get_preference_counts_by_dp(
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    dpar_collection: AsyncIOMotorCollection = Depends(get_dpar_requests_collection),
    grievance_collection: AsyncIOMotorCollection = Depends(get_grievance_collection),
):
    app_logger.info(f"API Call: /preference-counts/by-dp for dp_id: {current_user.get('dp_id')}")
    service = ConsentTransactionService(consent_artifact_collection, dpar_collection, grievance_collection)
    return await service.get_dashboard_counts(
        dp_id=current_user.get("dp_id"),
    )
