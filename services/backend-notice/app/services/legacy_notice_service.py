from datetime import UTC, datetime
import json
import uuid
from bson import ObjectId
from fastapi import BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.db.rabbitmq import publish_message
from app.services.postgres_service import (
    delete_token_information,
    get_token_information,
)
from app.services.consent_artifact_service import (
    consent_artifact_creation,
    data_element_consent_creation,
    get_dp_info_from_postgres,
    hash_headers,
)
from app.services.notice_service import S3_BUCKET
from app.utils.common import run_in_thread
from app.utils.html_utils import inject_legacy_hooks
from app.utils.request_utils import get_client_ip
from app.utils.s3_utils import fetch_object_from_s3
from app.core.logger import get_logger


logger = get_logger("service.legacy_notice_service")


async def get_rendered_notice(token, redis_client, s3_client):
    try:

        dpar_token = str(uuid.uuid4())

        token_info = await get_token_information(token, dpar_token, redis_client)
        if not token_info:
            return HTMLResponse(
                "<p>Invalid or expired token.</p>",
                headers={"Cache-Control": "no-store"},
            )

        df_id = token_info["df_id"]
        cp_id = token_info["cp_id"]
        notification_id = str(token_info["notification_id"])

        logger.info(
            f"Fetching notice for df_id: {df_id}, cp_id: {cp_id}, notification_id: {notification_id}",
            extra={"df_id": df_id, "cp_id": cp_id, "notification_id": notification_id},
        )

        cache_key = f"notice:{token}"
        cached_notice = await redis_client.get(cache_key)
        if cached_notice:
            logger.info(f"Notice served from Redis cache: {cache_key}", extra={"cache_key": cache_key})
            return HTMLResponse(cached_notice, headers={"Cache-Control": "no-store"})

        s3_key = f"legacy_notices/{df_id}/{cp_id}_{notification_id}.html"
        rendered_html = await fetch_object_from_s3(s3_client, S3_BUCKET, s3_key)

        await redis_client.setex(cache_key, 3600, rendered_html)

        return HTMLResponse(rendered_html, headers={"Cache-Control": "no-store"})

    except Exception as e:
        logger.error(f"Error retrieving rendered notice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_legacy_consent_submission(
    request: Request,
    token_model,
    background_tasks: BackgroundTasks,
    pool,
    redis_client,
    gdb,
):
    cached_info_row = await redis_client.get(f"token:{token_model.token}")
    if not cached_info_row:
        raise HTTPException(status_code=404, detail="Token information not found in cache")

    cached_info = json.loads(cached_info_row)
    dp_id = cached_info["dp_id"]
    df_id = cached_info["df_id"]
    collection_point_id = cached_info["cp_id"]
    dpar_token = cached_info["dpar_token"]

    agreement_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    data_principal = await get_dp_info_from_postgres(dp_id)
    data_elements_consents = await data_element_consent_creation(token_model, df_id, collection_point_id, gdb)

    collection_point = await gdb.cp_master.find_one({"_id": ObjectId(collection_point_id), "df_id": df_id})
    collection_point_name = collection_point.get("cp_name", "Unknown CP")

    binded_ip = get_client_ip(request)
    request_headers_hash = await hash_headers(request.headers)

    consent_artifact = await consent_artifact_creation(
        collection_point_name,
        collection_point_id,
        binded_ip,
        request_headers_hash,
        dict(request.headers),
        data_principal,
        df_id,
        data_elements_consents,
        True,
        agreement_id,
    )

    purposes_list = []
    seen = set()

    for element in data_elements_consents:
        de_base = {
            "de_id": element.get("de_id"),
            "de_hash_id": element.get("de_hash_id"),
            "title": element.get("title"),
            "data_retention_period": element.get("data_retention_period"),
        }
        for consent in element.get("consents", []):
            unique_key = f"{de_base['de_id']}_{consent.get('purpose_id')}"
            if unique_key in seen:
                continue
            seen.add(unique_key)
            flattened = {**de_base, **consent}
            purposes_list.append(flattened)

    message_to_publish = {
        "dp_id": dp_id,
        "df_id": df_id,
        "cp_name": collection_point_name,
        "event_type": "consent_granted",
        "timestamp": str(datetime.now(UTC)),
        "purposes": purposes_list,
    }

    await publish_message("consent_events_q", json.dumps(message_to_publish))

    await run_in_thread(gdb.consent_artifacts.insert_one, consent_artifact)

    background_tasks.add_task(
        delete_token_information,
        token_model.token,
        df_id,
        dp_id,
        redis_client,
    )

    return {
        "message": "Consent submitted successfully!",
        "dp_id": dp_id,
        "dpar_token": dpar_token,
        "agreement_id": agreement_id,
    }


async def get_legacy_notice_management(token: str, redis_client, s3_client, language: str):
    try:
        payload = await redis_client.get(f"token:{token}")
        if not payload:
            payload = await get_token_information(token, None, redis_client)

        if not payload:
            not_found_html = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0
                ">
                    <title>Notice Not Found</title>
                </head>
                <body>
                    <h1>Notice Not Found</h1>
                    <p>The requested notice could not be found - either the token is invalid or the consent has already been given.</p>
                </body>
                </html>"""

            return HTMLResponse(
                content=not_found_html,
                headers={"Cache-Control": "no-store"},
            )

        cached_info = json.loads(payload)
        collection_point_id = cached_info.get("cp_id")
        df_id = cached_info.get("df_id")

        if not collection_point_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        cache_key = f"legacy_notice:{df_id}:{collection_point_id}"
        cached_notice = await redis_client.get(cache_key)

        if cached_notice:
            logger.info(f"Notice served from Redis cache: {cache_key}", extra={"cache_key": cache_key})
            modified_html = inject_legacy_hooks(cached_notice)
            return HTMLResponse(
                content=modified_html,
                headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
            )

        s3_object_name = f"notices/{collection_point_id}.html"
        rendered_html = await fetch_object_from_s3(s3_client, S3_BUCKET, s3_object_name)

        await redis_client.setex(cache_key, 3600, rendered_html)

        modified_html = inject_legacy_hooks(rendered_html)
        return HTMLResponse(
            content=modified_html,
            headers={"Cache-Control": "no-store"},
        )

    except HTTPException as http_exc:
        logger.warning(f"HTTPException in get_legacy_notice_management: {http_exc.detail}", exc_info=True)
        raise http_exc
    except Exception as e:
        logger.error(f"Error retrieving notice in get_legacy_notice_management: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving notice: {str(e)}")
