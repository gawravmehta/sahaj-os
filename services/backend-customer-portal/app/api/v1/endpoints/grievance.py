from typing import List
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from minio import Minio, S3Error

from app.api.v1.deps import get_current_user
from app.db.dependencies import get_data_processors_collection, get_df_register_collection, get_grievance_collection
from app.db.session import get_s3_client
from app.schemas.grievance_schema import GrievanceCreateRequest
from app.services.grievance_service import GrievanceService
from app.core.config import settings
from app.utils.common import clean_mongo_doc
from app.core.logger import app_logger

router = APIRouter()


@router.post("/raise-grievance")
async def raise_grievance(
    payload: GrievanceCreateRequest,
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
    current_user=Depends(get_current_user),
):
    app_logger.info(f"API Call: /raise-grievance for user: {current_user.get('dp_id')}")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.create_grievance(payload, current_user)
    return JSONResponse(status_code=201, content=response)


@router.post("/verify")
async def verify_token(
    token: str = Body(..., embed=True),
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
):
    app_logger.info(f"API Call: /verify grievance token: {token[0]}...")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.verify_grievance_token(token)
    return JSONResponse(status_code=200, content=response)


@router.delete("/cancel")
async def cancel_request(
    token: str = Body(..., embed=True),
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
):
    app_logger.info(f"API Call: /cancel grievance token: {token[0]}...")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.cancel_grievance_request(token)
    return JSONResponse(status_code=200, content=response)


@router.get("/get-all-grievances")
async def get_all_grievances(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
    current_user=Depends(get_current_user),
):
    app_logger.info(f"API Call: /get-all-grievances for user: {current_user.get('dp_id')}, skip: {skip}, limit: {limit}")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.get_all_grievances(current_user, skip, limit)
    return JSONResponse(status_code=200, content=response)


@router.get("/get-one-grievance/{grievance_id}")
async def get_one_grievance(
    grievance_id: str,
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /get-one-grievance/{grievance_id}")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.get_one_grievance(grievance_id)
    return JSONResponse(status_code=200, content=response)


@router.patch("/upload-reference-document")
async def upload_reference_document(
    grievance_id: str,
    files: List[UploadFile] = File(...),
    grievance_collection=Depends(get_grievance_collection),
    df_register_collection=Depends(get_df_register_collection),
    s3_client=Depends(get_s3_client),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /upload-reference-document for grievance_id: {grievance_id}")
    service = GrievanceService(grievance_collection, df_register_collection)
    response = await service.upload_reference_document(grievance_id, files, s3_client)
    return JSONResponse(status_code=200, content=response)


@router.get("/files/{object_name}")
async def get_file(
    object_name: str,
    s3_client: Minio = Depends(get_s3_client),
):
    try:

        response = s3_client.get_object(settings.KYC_DOCUMENTS_BUCKET, object_name)

        content_type = "application/octet-stream"
        if object_name.endswith(".png"):
            content_type = "image/png"
        elif object_name.endswith(".jpg") or object_name.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif object_name.endswith(".pdf"):
            content_type = "application/pdf"

        app_logger.info(f"Successfully retrieved file {object_name} from S3.")
        return StreamingResponse(response, media_type=content_type)

    except S3Error as e:
        app_logger.error(f"S3Error fetching file {object_name}: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        app_logger.error(f"Unexpected error fetching file {object_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/get-all-data-processors")
async def get_all_data_processors(
    data_processors_collection=Depends(get_data_processors_collection),
    current_user=Depends(get_current_user),
):
    df_id = current_user.get("df_id")
    app_logger.info(f"API Call: /get-all-data-processors for df_id: {df_id}")
    data_processors = await data_processors_collection.find({"df_id": df_id}).to_list(length=None)
    app_logger.info(f"Found {len(data_processors)} data processors for df_id: {df_id}")
    return JSONResponse(status_code=200, content=clean_mongo_doc(data_processors))


@router.get("/get-all-business-entity")
async def get_all_business_entity(
    df_register_collection=Depends(get_df_register_collection),
    current_user=Depends(get_current_user),
):
    df_id = current_user.get("df_id")
    app_logger.info(f"API Call: /get-all-business-entity for df_id: {df_id}")
    try:

        df_details = await df_register_collection.find_one({"df_id": df_id}, {"sub_df_ids": 1, "_id": 0})
        if not df_details:
            app_logger.warning(f"DF not found for df_id: {df_id} in /get-all-business-entity")
            raise HTTPException(status_code=404, detail="DF not found")

        sub_df_details = []
        for sub_df_id in df_details.get("sub_df_ids", []):
            sub_df_data = await df_register_collection.find_one({"df_id": sub_df_id})
            if sub_df_data:
                sub_df_data["_id"] = str(sub_df_data["_id"])
                sub_df_details.append(sub_df_data)

        if not sub_df_details:
            raise HTTPException(status_code=404, detail="No sub organizations found")

        return {
            "sub_organizations": sub_df_details,
            "message": "Sub organizations fetched successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
