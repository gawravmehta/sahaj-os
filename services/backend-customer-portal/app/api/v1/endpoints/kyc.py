from typing import List, Optional
from fastapi import APIRouter, Form, UploadFile, File, Depends
from minio import Minio
from app.api.v1.deps import get_current_user
from app.db.dependencies import get_dpar_requests_collection
from app.db.session import get_s3_client
from app.services.kyc_service import handle_kyc_upload
from app.schemas.kyc_schema import KYCUploadResponse
from app.core.logger import app_logger

router = APIRouter()


@router.put("/upload-kyc-documents", response_model=KYCUploadResponse)
async def upload_kyc_documents(
    request_id: str = Form(...),
    kyc_front: UploadFile = File(...),
    kyc_back: UploadFile = File(...),
    upload_pdfs: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user),
    collection=Depends(get_dpar_requests_collection),
    s3_client: Minio = Depends(get_s3_client),
):
    if isinstance(upload_pdfs, str) and upload_pdfs == "":
        upload_pdfs = None
    app_logger.info(f"API Call: /upload-kyc-documents for request_id: {request_id}, user: {current_user.get('dp_id')}")
    return await handle_kyc_upload(request_id, kyc_front, kyc_back, upload_pdfs, current_user, collection, s3_client)
