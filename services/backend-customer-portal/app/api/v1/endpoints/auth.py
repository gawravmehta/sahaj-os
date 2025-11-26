from typing import Optional
from fastapi import APIRouter, Depends, Header, Query

from app.api.v1.deps import get_current_user
from app.db.session import get_postgres_pool
from app.db.dependencies import get_df_register_collection
from app.services.auth_service import (
    handle_login,
    handle_otp_verification,
    handle_resend_otp,
)
from app.core.logger import app_logger

router = APIRouter()


@router.post("/login-preference-center")
async def dpar_login(
    email: Optional[str] = Query(None),
    mobile: Optional[str] = Query(None),
    df_id: Optional[str] = Header(None),
    pool=Depends(get_postgres_pool),
    df_register_collection=Depends(get_df_register_collection),
):
    app_logger.info(f"API Call: /login-preference-center for email: {email}, mobile: {mobile}")
    return await handle_login(email=email, mobile=mobile, df_id=df_id, pool=pool, df_register_collection=df_register_collection)


@router.post("/validate-otp")
async def verify_otp(
    email: Optional[str] = Query(None),
    mobile: Optional[str] = Query(None),
    df_id: Optional[str] = Header(None),
    otp: str = Query(...),
):
    app_logger.info(f"API Call: /validate-otp for email: {email}, mobile: {mobile}")
    return await handle_otp_verification(
        email=email,
        mobile=mobile,
        df_id=df_id,
        otp_input=otp,
    )


@router.post("/resend-otp")
async def resend_otp(
    email: Optional[str] = Query(None),
    mobile: Optional[str] = Query(None),
    df_id: Optional[str] = Header(None),
    pool=Depends(get_postgres_pool),
    df_register_collection=Depends(get_df_register_collection),
):
    app_logger.info(f"API Call: /resend-otp for email: {email}, mobile: {mobile}")
    return await handle_resend_otp(email=email, mobile=mobile, df_id=df_id, pool=pool, df_register_collection=df_register_collection)


@router.get("/me")
async def get_profile(user: dict = Depends(get_current_user)):
    app_logger.info("API Call: /me")
    return {"user": user}
