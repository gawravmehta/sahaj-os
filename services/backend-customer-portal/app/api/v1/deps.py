from fastapi import Depends, HTTPException
from app.core.security import verify_jwt_token
from app.db.dependencies import (
    get_concur_master_db,
    get_dpar_requests_collection,
    get_consent_artifact_collection,
)
from app.services.dpar_request_service import DPARRequestService
from motor.motor_asyncio import AsyncIOMotorCollection

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_dpar_request_service(
    db: AsyncIOMotorCollection = Depends(get_concur_master_db),
    dpa_requests_collection: AsyncIOMotorCollection = Depends(get_dpar_requests_collection),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
) -> DPARRequestService:

    return DPARRequestService(dpa_requests_collection, consent_artifact_collection)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    try:
        return verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
