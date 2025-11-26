from datetime import UTC, datetime
from typing import Any, Dict
import asyncpg
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from starlette.responses import RedirectResponse
from pymongo.database import Database

from app.api.v1.deps import get_validated_df
from app.schemas.authentication import AuthRequestSchema
from app.services.auth_service import AuthenticationService
from app.db.session import (
    get_mongo_master_db,
    get_postgres_pool,
    get_redis,
    get_tracer,
)
from app.utils.request_utils import get_client_ip
from app.utils.verification_utils import OTP_TTL_SECONDS, session_key
from app.core.config import settings
from jose import jwt


router = APIRouter()


@router.get("/authenticate", response_class=RedirectResponse)
async def authenticate(
    request: Request,
    background_tasks: BackgroundTasks,
    auth_params: AuthRequestSchema = Depends(),
    validated_df: Dict[str, Any] = Depends(get_validated_df),
    db: Database = Depends(get_mongo_master_db),
    redis_client=Depends(get_redis),
    tracer=Depends(get_tracer),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
) -> RedirectResponse:
    """
    Authenticates a user and redirects them to the consent notice with a JWT.
    """
    auth_service = AuthenticationService(
        db=db,
        redis_client=redis_client,
        tracer=tracer,
        pool=pool,
    )
    client_ip = get_client_ip(request)

    token = await auth_service.authenticate_user_and_get_token(
        auth_params=auth_params,
        df_id=validated_df["df_id"],
        client_ip=client_ip,
        background_tasks=background_tasks,
    )

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    await redis_client.setex(session_key(payload), OTP_TTL_SECONDS * 3, token)

    return RedirectResponse(url=f"/api/v1/n/get-notice/{token}", status_code=303)
