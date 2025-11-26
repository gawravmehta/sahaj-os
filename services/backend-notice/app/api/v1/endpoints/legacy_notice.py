from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks

from app.db.session import (
    get_mongo_master_db,
    get_postgres_pool,
    get_redis,
    get_s3_client,
)
from app.schemas.consent_schema import TokenModel
from app.services.legacy_notice_service import (
    get_legacy_notice_management,
    get_rendered_notice,
    handle_legacy_consent_submission,
)
from app.core.config import settings

router = APIRouter()

sender_id = settings.SMS_SENDER_ID


@router.get(f"/{sender_id}", tags=["Legacy Notice"])
async def get_legacy_notice(
    request: Request,
    redis_client=Depends(get_redis),
    s3_client=Depends(get_s3_client),
):
    raw_query = request.scope.get("query_string", b"").decode("utf-8")
    if not raw_query:
        raise HTTPException(status_code=400, detail="Invalid or missing token in query string")

    return await get_rendered_notice(token=raw_query, redis_client=redis_client, s3_client=s3_client)


@router.post("/submit-legacy-consent", tags=["Legacy Consent"])
async def submit_legacy_consent(
    request: Request,
    token_model: TokenModel,
    background_tasks: BackgroundTasks,
    redis_client=Depends(get_redis),
    gdb=Depends(get_mongo_master_db),
    pool=Depends(get_postgres_pool),
):
    return await handle_legacy_consent_submission(
        request=request,
        token_model=token_model,
        background_tasks=background_tasks,
        pool=pool,
        redis_client=redis_client,
        gdb=gdb,
    )


@router.get("/mln/{token}", tags=["Legacy Notice"])
async def manage_legacy_notice(
    request: Request,
    token: str,
    redis_client=Depends(get_redis),
    s3_client=Depends(get_s3_client),
    language: str = "eng",
):
    """Retrieve the legacy notice management"""
    return await get_legacy_notice_management(token, redis_client, s3_client, language)
