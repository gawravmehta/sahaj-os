from bson import ObjectId
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Path, Query, status
from typing import List, Optional
from app.api.v1.deps import get_current_user, get_grievance_service
from app.db.dependencies import get_grievance_collection
from app.services.grievance_service import GrievanceService

router = APIRouter()


@router.get("/view-all-grievances")
async def get_all_grievances(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    current_user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service),
):
    return await grievance_service.get_all_grievances(page=page, page_size=page_size, current_user=current_user)


@router.get("/view-grievance/{grievance_id}")
async def get_grievance_by_id(
    grievance_id: str = Path(..., description="Grievance ID"),
    current_user: dict = Depends(get_current_user),
    grievance_service: GrievanceService = Depends(get_grievance_service),
):
    return await grievance_service.view_grievance(grievance_id, current_user=current_user)
