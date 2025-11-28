from jose import JWTError, jwt
from fastapi import Request, HTTPException
from app.core.config import settings
from app.utils.request_utils import get_client_ip
from app.db.session import get_redis, get_s3_client
from app.utils.common import run_in_thread
from minio.error import S3Error
import os
from app.core.logger import get_logger


logger = get_logger("service.notice_service")


s3_client = get_s3_client()
SECRET_KEY = settings.SECRET_KEY
S3_BUCKET = settings.NOTICE_WORKER_BUCKET


async def retrieve_notice_html(token: str, request: Request):
    redis_client = get_redis()
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        logger.debug(f"Decoded payload: {payload}", extra={"payload": payload})

        request_id = payload.get("request_id")
        binded_ip = get_client_ip(request)

        logger.debug(f"Redis client: {redis_client}")
        logger.debug(f"S3 client: {s3_client}")

        redis_key = f"session:{payload.get('df_id')}:{payload.get('dp_id')}:{request_id}"
        saved_token = await redis_client.get(redis_key)

        if not saved_token:
            raise HTTPException(status_code=401, detail="Session expired or invalid.")

        if saved_token != token:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")

        df_id = payload["df_id"]
        dp_id = payload["dp_id"]
        cp_id = payload.get("cp_id")
        language = payload.get("language", "eng")

        if not cp_id:
            raise HTTPException(status_code=400, detail="Invalid token payload.")

        cache_key = f"notice:{df_id}:{cp_id}"
        cached_notice = await redis_client.get(cache_key)

        language_script = f"""
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                window.prefLanguage = '{language}';
            }});
        </script>
        """

        if cached_notice is not None:
            cached_notice = cached_notice.decode("utf-8") if isinstance(cached_notice, bytes) else cached_notice
            return cached_notice.replace("</head>", f"{language_script}</head>")

        new_file_name = f"{cp_id}.html"
        s3_object_name = f"notices/{new_file_name}"

        try:
            response = await run_in_thread(s3_client.get_object, S3_BUCKET, s3_object_name)
            rendered_html = response.read().decode("utf-8")
        except S3Error as e:
            logger.error(f"S3 error: {str(e)}", exc_info=True)
            if e.code == "NoSuchKey":
                return "Notice not found."
            raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")

        await redis_client.setex(cache_key, 3600, rendered_html)
        return rendered_html.replace("</head>", f"{language_script}</head>")

    except JWTError as e:
        logger.error(f"JWT decode failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token.")
    except Exception as e:

        logger.error("Internal Server Error:", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error.")


async def retrieve_otp_html(token: str, request: Request):
    try:

        html_file_path = os.path.join("app", "constants", "otp_verification.html")
        with open(html_file_path, "r", encoding="utf-8", errors="strict") as html_file:
            rendered_html = html_file.read().replace("{{api_url}}", "http://127.0.0.1:8001")

        return rendered_html

    except Exception as e:
        logger.error("Internal Server Error:", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error.")
