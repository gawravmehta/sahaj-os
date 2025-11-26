from fastapi import APIRouter, Request, Depends, HTTPException, Query, Body
from typing import Optional, List

from app.api.v1.deps import get_current_user, get_vendor_service
from app.schemas.vendor_schema import CreateMyVendor, DataProcessingActivity

from app.services.vendor_service import VendorService

router = APIRouter()


@router.post("/create-or-update-vendor")
async def create_or_update_vendor(
    request: Request,
    vendor_id: Optional[str] = Query(None),
    add_vendor: CreateMyVendor = Body(...),
    current_user: dict = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service),
):
    genie_user = current_user.get("_id")
    df_id = current_user.get("df_id")
    if not genie_user or not df_id:
        raise HTTPException(status_code=400, detail="User not found")

    result = await service.create_or_update_vendor(
        vendor_id,
        add_vendor,
        current_user,
    )
    return result


@router.patch("/edit-data-processing-activities/{dpr_id}")
async def edit_data_processing_activities(
    dpr_id: str,
    data_processing_activities: List[DataProcessingActivity] = Body(...),
    current_user: dict = Depends(get_current_user),
    service: VendorService = Depends(get_vendor_service),
):
    genie_user = current_user.get("_id")
    df_id = current_user.get("df_id")
    if not genie_user or not df_id:
        raise HTTPException(status_code=400, detail="User not found")

    result = await service.edit_data_processing_activities(
        dpr_id,
        data_processing_activities,
        current_user,
    )
    return result


@router.get("/get-all-vendors")
async def get_all_vendors(
    current_user: dict = Depends(get_current_user),
    dpr_country: Optional[str] = Query(None),
    dpr_country_risk: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    processing_category: Optional[List[str]] = Query(None),
    cross_border: Optional[bool] = Query(None),
    sub_processor: Optional[bool] = Query(None),
    audit_result: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or industry"),
    sort_order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    service: VendorService = Depends(get_vendor_service),
):
    genie_user = current_user.get("_id")
    df_id = current_user.get("df_id")
    if not genie_user or not df_id:
        raise HTTPException(status_code=400, detail="User not found")

    result = await service.get_all_my_vendors(
        current_user,
        dpr_country,
        dpr_country_risk,
        industry,
        processing_category,
        cross_border,
        sub_processor,
        audit_result,
        search,
        sort_order,
        page,
        page_size,
    )
    return result


@router.get("/get-one-vendor")
async def get_one_vendor(vendor_id: str, current_user: dict = Depends(get_current_user), service: VendorService = Depends(get_vendor_service)):
    genie_user = current_user.get("_id")
    df_id = current_user.get("df_id")
    if not genie_user or not df_id:
        raise HTTPException(status_code=400, detail="User not found")

    if not vendor_id:
        raise HTTPException(status_code=400, detail="Vendor ID is required")

    result = await service.get_one_vendor(vendor_id, current_user)
    return result


@router.delete("/delete-my-vendor/{dpr_id}")
async def delete_vendor(
    dpr_id: str, request: Request, current_user: dict = Depends(get_current_user), service: VendorService = Depends(get_vendor_service)
):
    genie_user = current_user.get("_id")
    df_id = current_user.get("df_id")
    if not genie_user or not df_id:
        raise HTTPException(status_code=400, detail="User not found")

    result = await service.delete_vendor(dpr_id, current_user)

    return result


@router.post("/make-it-publish/{dpr_id}")
async def make_it_publish(
    dpr_id: str, request: Request, current_user: dict = Depends(get_current_user), service: VendorService = Depends(get_vendor_service)
):
    result = await service.make_it_publish(dpr_id, current_user)
    return result
