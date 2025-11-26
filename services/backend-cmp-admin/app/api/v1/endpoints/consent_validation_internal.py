from fastapi import APIRouter, File, Request, Depends, Query, UploadFile
from typing import Literal, Optional, List


from app.api.v1.deps import get_consent_validation_service, get_current_user
from app.db.session import get_s3_client
from app.schemas.consent_validation_schema import VerificationRequest
from app.services.consent_validation_service import ConsentValidationService
from datetime import datetime


router = APIRouter()


@router.post("/verify-consent-internal")
async def verify_consent_internal(
    request: Request,
    payload: VerificationRequest,
    current_user: dict = Depends(get_current_user),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.verify_consent_internal(payload, current_user)


@router.get("/get-all-verification-logs")
async def get_all_verification_logs(
    request: Request,
    page: int = 1,
    limit: int = 10,
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None,
    internal_external: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    purpose_hashes: Optional[List[str]] = Query(None),
    data_element_hashes: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.get_all_verification_logs(
        page,
        limit,
        sort_order,
        search,
        internal_external,
        status,
        from_date,
        to_date,
        purpose_hashes,
        data_element_hashes,
        current_user,
    )


@router.get("/download-verification-logs")
async def download_verification_logs(
    request: Request,
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None,
    internal_external: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    purpose_hashes: Optional[List[str]] = Query(None),
    data_element_hashes: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.download_verification_logs(
        sort_order,
        search,
        internal_external,
        status,
        from_date,
        to_date,
        purpose_hashes,
        data_element_hashes,
        current_user,
    )


@router.post("/bulk-verify-consent-internal")
async def bulk_verify_consent_internal(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    s3_client=Depends(get_s3_client),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.bulk_verify_consent_internal(file, current_user, s3_client)


@router.get("/get-all-uploaded-verification-files")
async def get_all_uploaded_verification_files(
    current_user: dict = Depends(get_current_user),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.get_all_uploaded_verification_files(current_user)


@router.get("/download-verified-file")
async def download_verified_file(
    file_name: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    download_type: Optional[Literal["csv", "json"]] = Query("csv", regex="^(csv|json)$"),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.download_verified_file(file_name, current_user, download_type)


@router.get("/get-one-verification-log")
async def get_one_verification_log(
    request_id: str, current_user: dict = Depends(get_current_user), service: ConsentValidationService = Depends(get_consent_validation_service)
):
    return await service.get_one_verification_log(request_id, current_user)


@router.get("/verification-dashboard-stats")
async def get_verification_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    service: ConsentValidationService = Depends(get_consent_validation_service),
):
    return await service.get_verification_dashboard_stats(current_user)
