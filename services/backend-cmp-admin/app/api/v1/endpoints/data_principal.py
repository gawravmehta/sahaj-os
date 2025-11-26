import json
import re
import uuid

from pydantic import BaseModel
import asyncpg
from fastapi import APIRouter, Query
from fastapi import Depends, HTTPException, Request
from typing import List, Optional

from app.api.v1.deps import get_current_user, get_data_principal_service
from app.db.session import get_postgres_pool
from app.schemas.data_principal_schema import AddDP, UpdateDP
from app.services.data_principal_service import DataPrincipalService
from app.utils.common import hash_shake256
from app.utils.data_principal import mask_email, mask_mobile

from bson import ObjectId

router = APIRouter()


class DPFilter(BaseModel):
    data_elements: Optional[List[str]] = None


class DPSearchRequest(BaseModel):
    filter: DPFilter


@router.post("/search-data-principals")
async def search_data_principals(
    body: DPSearchRequest,
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    data_elements = body.filter.data_elements or []

    result = await service.get_dps_by_data_elements(data_elements, current_user)

    return {"message": "Data Principals fetched successfully", "count": len(result), "data_principals": result}


@router.post("/add-data-principal")
async def add_data_principal(
    dp_data_list: List[AddDP],
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.add_data_principal(dp_data_list, current_user)


@router.get("/view-data-principal/{principal_id}")
async def get_dp(
    principal_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.get_data_principal(principal_id, current_user)


@router.delete("/delete-data-principal/{principal_id}")
async def delete_dp(
    principal_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.delete_data_principal(principal_id, current_user)


@router.get("/get-all-data-principals")
async def get_all_data_principals(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    dp_country: Optional[str] = None,
    dp_preferred_lang: Optional[str] = None,
    is_legacy: Optional[bool] = None,
    consent_status: Optional[str] = None,
    added_with: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.get_all_data_principals(
        page,
        limit,
        dp_country,
        dp_preferred_lang,
        is_legacy,
        consent_status,
        added_with,
        search,
        current_user,
    )


@router.put("/update-data-principal/{principal_id}")
async def update_dp(
    principal_id: str,
    update: UpdateDP,
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.update_data_principal(principal_id, update, current_user)


@router.get("/get-all-dp-tags")
async def get_all_dp_tags(
    current_user: dict = Depends(get_current_user),
    service: DataPrincipalService = Depends(get_data_principal_service),
):

    return await service.get_all_dp_tags(current_user)
