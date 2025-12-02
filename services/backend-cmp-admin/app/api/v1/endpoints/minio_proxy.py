import mimetypes
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
from minio.error import S3Error

from app.db.session import get_s3_client

router = APIRouter()


@router.get("/download")
async def download_file_from_minio(
    bucket: str,
    object_name: str,
    s3_client: Minio = Depends(get_s3_client),
):
    """
    Download a file from MinIO storage.

    Args:
        bucket: The MinIO bucket name
        object_name: The file path/key within the bucket
        s3_client: MinIO client instance (injected)

    Returns:
        StreamingResponse with the file content

    Raises:
        HTTPException: 404 if file or bucket not found, 403 if access denied, 500 for other errors
    """
    try:
        # Get the file from MinIO
        response = s3_client.get_object(bucket, object_name)

        # Extract filename from object_name
        filename = object_name.split("/")[-1]

        # Detect content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            # Default to octet-stream if type cannot be determined
            content_type = "application/octet-stream"

        # Return streaming response
        return StreamingResponse(
            response.stream(32 * 1024),  # Stream in 32KB chunks
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": content_type,
            },
        )

    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"File not found: {object_name} in bucket {bucket}")
        elif e.code == "NoSuchBucket":
            raise HTTPException(status_code=404, detail=f"Bucket not found: {bucket}")
        elif e.code == "AccessDenied":
            raise HTTPException(status_code=403, detail=f"Access denied to file: {object_name} in bucket {bucket}")
        else:
            raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
