from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user, get_dashboard_service
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard-details")
async def get_dashboard_details(
    current_user: dict = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_dashboard_detail(current_user)
