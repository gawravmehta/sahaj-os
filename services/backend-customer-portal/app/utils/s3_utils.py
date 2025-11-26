import uuid
from fastapi import HTTPException, UploadFile
from minio import Minio, S3Error
from app.core.config import settings
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
from app.core.logger import app_logger


def set_bucket_expiry(s3_client: Minio, bucket_name: str, days: int = 60):
    config = LifecycleConfig(
        [
            Rule(
                rule_filter={"prefix": ""},
                rule_id="auto-delete-60-days",
                status="Enabled",
                expiration=Expiration(days=days),
            )
        ]
    )
    s3_client.set_bucket_lifecycle(bucket_name, config)


def make_s3_bucket(bucket_names: list[str], s3_client: Minio):
    for bucket_name in bucket_names:
        if not s3_client.bucket_exists(bucket_name):
            s3_client.make_bucket(bucket_name)
            app_logger.info(f"✅ Bucket {bucket_name} created successfully")

            set_bucket_expiry(s3_client, bucket_name, days=60)


def upload_file_to_s3(file: UploadFile, s3_client: Minio) -> str:
    try:

        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        s3_client.put_object(
            settings.KYC_DOCUMENTS_BUCKET,
            unique_filename,
            file.file,
            file_size,
            content_type=file.content_type,
        )

        file_url = f"http://{settings.S3_ENDPOINT}/{settings.KYC_DOCUMENTS_BUCKET}/{unique_filename}"
        return file_url

    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
