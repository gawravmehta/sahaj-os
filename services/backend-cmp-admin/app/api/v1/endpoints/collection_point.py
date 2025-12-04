from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Response
from fastapi.responses import StreamingResponse

from app.api.v1.deps import (
    get_current_user,
    get_cp_service,
)
from app.db.session import get_s3_client
from app.schemas.collection_point_schema import (
    CpCreate,
    CpPaginatedResponse,
    CpResponse,
    CpUpdate,
)
from app.services.collection_point_service import CollectionPointService
from minio import Minio
from app.core.logger import get_logger


router = APIRouter()
logger = get_logger("api.collection_point")


@router.post(
    "/create-collection-point",
    response_model=CpResponse,
    summary="Create a new Collection Point",
)
async def create_collection_point_endpoint(
    cp_data: CpCreate,
    current_user: dict = Depends(get_current_user),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        collection_point = await service.create_collection_point(cp_data.model_dump(), current_user)
        logger.info(f"Collection point '{cp_data.cp_name}' created by user {current_user.get('email')}.")
        return collection_point
    except HTTPException as e:
        logger.error(f"HTTPException while creating collection point for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while creating collection point for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/update-cp/{cp_id}",
    response_model=CpResponse,
    summary="Update an existing CollectionPoint Template",
)
async def update_cp_endpoint(
    cp_id: str,
    update_data: CpUpdate,
    current_user: dict = Depends(get_current_user),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        update_dict = update_data.model_dump(exclude_unset=True, exclude_defaults=True)
        updated_cp = await service.update_collection_point(cp_id, update_dict, current_user)
        if not updated_cp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection Point with id '{cp_id}' not found.",
            )
        logger.info(f"Collection point {cp_id} updated by user {current_user.get('email')}.")
        return updated_cp
    except HTTPException as e:
        logger.error(f"HTTPException while updating collection point {cp_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while updating collection point {cp_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/publish-cp/{cp_id}",
    response_model=CpResponse,
    summary="Publish CollectionPoint Template",
)
async def publish_cp_endpoint(
    cp_id: str,
    current_user: dict = Depends(get_current_user),
    s3_client: Minio = Depends(get_s3_client),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:

        updated_cp = await service.publish_collection_point(cp_id, current_user, s3_client)
        if not updated_cp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection Point with id '{cp_id}' not found.",
            )
        logger.info(f"Collection point {cp_id} published by user {current_user.get('email')}.")
        return updated_cp
    except HTTPException as e:
        logger.error(f"HTTPException while publishing collection point {cp_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while publishing collection point {cp_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get-all-cps", summary="Retrieve a CollectionPoint Template by ID", response_model=CpPaginatedResponse)
async def get_all_cps_endpoint(
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    current_user: dict = Depends(get_current_user),
    is_legacy: Optional[bool] = Query(None, description="Filter by legacy status"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        collection_points = await service.get_all_collection_points(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
            is_legacy=is_legacy,
            is_published=is_published,
        )
        logger.info(f"User {current_user.get('email')} retrieved all collection points. Page: {current_page}, Size: {data_per_page}")
        return collection_points
    except HTTPException as e:
        logger.error(f"HTTPException while retrieving all collection points for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while retrieving all collection points for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-cp/{cp_id}",
    response_model=CpResponse,
    summary="Retrieve a CollectionPoint Template by ID",
)
async def get_cp_endpoint(
    cp_id: str,
    current_user: dict = Depends(get_current_user),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        collection_point = await service.get_collection_point(cp_id, current_user)
        if not collection_point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection Point not found",
            )
        logger.info(f"User {current_user.get('email')} retrieved collection point {cp_id}.")
        return collection_point
    except HTTPException as e:
        logger.error(f"HTTPException while retrieving collection point {cp_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while retrieving collection point {cp_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-cp/{cp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a CollectionPoint Template",
)
async def delete_cp_endpoint(
    cp_id: str,
    current_user: dict = Depends(get_current_user),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        deleted_cp = await service.delete_collection_point(cp_id, current_user)
        if not deleted_cp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection Point not found or already deleted.",
            )
        logger.info(f"Collection point {cp_id} soft-deleted by user {current_user.get('email')}.")
    except HTTPException as e:
        logger.error(f"HTTPException while soft-deleting collection point {cp_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(
            f"Internal Server Error while soft-deleting collection point {cp_id} for user {current_user.get('email')}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/upload-audio",
    summary="Upload audio file for collection point",
    response_model=dict,
)
async def upload_audio_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    s3_client: Minio = Depends(get_s3_client),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:

        if not file.content_type.startswith("audio/"):
            logger.warning(f"Invalid file type uploaded by user {current_user.get('email')}: {file.content_type}")
            raise HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed.")

        file_content = await file.read()
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp3"

        audio_url = await service.upload_audio_to_minio(
            s3_client=s3_client,
            file_content=file_content,
            content_type=file.content_type,
            file_extension=file_extension,
        )
        logger.info(f"Audio file '{file.filename}' uploaded by user {current_user.get('email')}. URL: {audio_url}")
        return {"audio_url": audio_url}
    except HTTPException as e:
        logger.error(f"HTTPException while uploading audio for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while uploading audio for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-audio/{audio_url}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audio file for collection point",
)
async def delete_audio_endpoint(
    audio_url: str,
    current_user: dict = Depends(get_current_user),
    s3_client: Minio = Depends(get_s3_client),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        deleted_audio = await service.delete_audio_from_minio(audio_url, current_user, s3_client)
        if not deleted_audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio not found or already deleted.",
            )
        logger.info(f"Audio file '{audio_url}' deleted by user {current_user.get('email')}.")
        return {"message": "Audio deleted successfully"}
    except HTTPException as e:
        logger.error(f"HTTPException while deleting audio {audio_url} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while deleting audio {audio_url} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-audio/{audio_url}", summary="Get audio file for collection point")
async def get_audio_endpoint(
    audio_url: str,
    s3_client: Minio = Depends(get_s3_client),
    service: CollectionPointService = Depends(get_cp_service),
):
    try:
        audio_stream = await service.get_audio_file(s3_client, audio_url)
        if not audio_stream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio not found.",
            )
        logger.info(f"Retrieved audio file: {audio_url}.")

        def iterfile():
            try:
                for chunk in audio_stream.stream(32 * 1024):
                    yield chunk
            finally:
                audio_stream.close()
                audio_stream.release_conn()

        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    except HTTPException as e:
        logger.error(f"HTTPException while retrieving audio {audio_url}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while retrieving audio {audio_url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
