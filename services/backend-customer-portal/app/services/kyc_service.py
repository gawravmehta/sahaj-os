from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, UploadFile
from app.utils.s3_utils import upload_file_to_s3
from app.schemas.kyc_schema import KYCUploadResponse
from minio import Minio
from app.core.logger import app_logger


async def handle_kyc_upload(
    request_id: str,
    kyc_front: UploadFile,
    kyc_back: UploadFile,
    upload_pdfs: Optional[List[UploadFile]],
    current_user: dict,
    collection,
    s3_client: Minio,
) -> KYCUploadResponse:
    app_logger.info(f"Handling KYC upload for request_id: {request_id}, user: {current_user.get('dp_id')}")
    user_request = await collection.find_one({"_id": ObjectId(request_id)})

    if not user_request:
        app_logger.warning(f"KYC upload failed for request_id {request_id}: Request not found.")
        raise HTTPException(status_code=404, detail="Request not found")

    kyc_front_url = upload_file_to_s3(kyc_front, s3_client)
    kyc_back_url = upload_file_to_s3(kyc_back, s3_client)

    update_data = {
        "kyc_front": kyc_front_url,
        "kyc_back": kyc_back_url,
    }

    if upload_pdfs:
        attachment_urls = []
        for pdf in upload_pdfs:
            pdf_url = upload_file_to_s3(pdf, s3_client)
            attachment_urls.append(pdf_url)
        update_data["request_attachments"] = attachment_urls
        app_logger.debug(f"Uploaded {len(attachment_urls)} additional PDF attachments for request {request_id}")

    await collection.update_one(
        {"_id": ObjectId(request_id), "requested_by": str(current_user.get("dp_id"))},
        {"$set": update_data},
    )
    app_logger.info(f"KYC documents successfully updated for request_id: {request_id}")

    return KYCUploadResponse(
        message="KYC documents uploaded successfully",
        kyc_front_url=kyc_front_url,
        kyc_back_url=kyc_back_url,
        request_attachment_urls=update_data.get("request_attachments"),
    )
