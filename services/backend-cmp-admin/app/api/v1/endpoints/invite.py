from fastapi import APIRouter, Depends, Query, Request, HTTPException

from app.api.v1.deps import get_current_user, get_invites_service
from app.db.dependencies import (
    get_system_admin_role_id,
)
from app.schemas.invite_schema import InviteModel

from app.services.invite_service import InviteService


router = APIRouter()


@router.post("/new")
async def invite_new_user(
    invite_data: InviteModel,
    current_user: dict = Depends(get_current_user),
    service: InviteService = Depends(get_invites_service),
    system_admin_role_id: str = Depends(get_system_admin_role_id),
):
    try:
        return await service.create_invite(invite_data, current_user, system_admin_role_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accept/{token}")
async def verify_token(
    request: Request,
    token: str,
    service: InviteService = Depends(get_invites_service),
):
    try:
        return await service.verify_token(token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view-all-invites", summary="View All Invites")
async def get_all_invites(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
    ),
    service: InviteService = Depends(get_invites_service),
):
    try:
        return await service.get_all_invites(current_user, page, page_size)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/resend-invitation/{invite_id}")
async def resend_invites(
    request: Request,
    invite_id: str,
    current_user: dict = Depends(get_current_user),
    service: InviteService = Depends(get_invites_service),
):
    try:
        return await service.resend_invites(invite_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel-invite/{invite_id}")
async def cancel_invite(
    request: Request,
    invite_id: str,
    current_user: dict = Depends(get_current_user),
    service: InviteService = Depends(get_invites_service),
):
    try:
        return await service.cancel_invite(invite_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
