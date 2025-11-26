from minio import S3Error

from app.utils.common import run_in_thread


async def fetch_object_from_s3(s3_client, bucket: str, key: str) -> str:
    try:
        response = await run_in_thread(s3_client.get_object, bucket, key)
        return response.read().decode("utf-8")
    except S3Error as e:
        if e.code == "NoSuchKey":
            return "<p>Notice file not found.</p>"
        raise e
