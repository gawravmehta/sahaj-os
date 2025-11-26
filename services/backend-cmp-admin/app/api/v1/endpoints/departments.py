from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.api.v1.deps import get_current_user, get_department_service
from app.db.dependencies import (
    get_departments_collection,
    get_roles_collection,
    get_system_admin_role_id,
    get_user_collection,
    get_user_invites_collection,
)
from app.schemas.department_schema import (
    UpdateDepartmentRequest,
    AddDepartment,
    UpdateDepartmentPermission,
    UpdateDepartmentUsers,
)
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime, UTC
from typing import List, Optional

from app.services.department_service import DepartmentService

router = APIRouter()

DEPARTMENT = "department"


@router.post("/add-department")
async def add_department(
    request: Request,
    department: AddDepartment,
    current_user: dict = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.add_department(department, current_user)


@router.patch("/update-department-members/{department_id}")
async def update_department_users(
    request: Request,
    department_id: str,
    update_data: UpdateDepartmentUsers,
    current_user: dict = Depends(get_current_user),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.update_department_users(department_id, update_data, current_user, SYSTEM_ADMIN_ROLE_ID)


@router.patch("/update-department-permissions/{department_id}")
async def update_department_permissions(
    request: Request,
    department_id: str,
    update_data: UpdateDepartmentPermission,
    current_user: dict = Depends(get_current_user),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.update_department_permissions(department_id, update_data, current_user, SYSTEM_ADMIN_ROLE_ID)


@router.get("/search-department")
async def search_department(
    department_name: str, current_user: dict = Depends(get_current_user), service: DepartmentService = Depends(get_department_service)
):
    return await service.search_department(department_name, current_user)


@router.get("/get-all-departments")
async def get_all_departments(
    page: int = Query(1, description="Page number, default is 1"),
    limit: int = Query(10, description="Number of items per page, default is 10"),
    current_user: dict = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.get_all_departments(page, limit, current_user)


@router.get("/get-one-department/{department_id}")
async def get_one_department(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.get_one_department(department_id, current_user)


@router.patch("/update-department/{department_id}")
async def update_department_handler(
    request: Request,
    department_id: str,
    department: UpdateDepartmentRequest,
    current_user: dict = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.update_department(department_id, department, current_user)


@router.delete("/delete-department/{department_id}")
async def soft_delete_department(
    department_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
    service: DepartmentService = Depends(get_department_service),
):
    return await service.soft_delete_department(department_id, current_user, SYSTEM_ADMIN_ROLE_ID)


@router.get("/dashboard")
async def get_department_dashboard(
    current_user: dict = Depends(get_current_user),
    departments_collection=Depends(get_departments_collection),
    user_collection=Depends(get_user_collection),
    genie_user_invites_collection=Depends(get_user_invites_collection),
    roles_collection=Depends(get_roles_collection),
):
    df_id = current_user.get("df_id")

    user_count = await user_collection.count_documents({"df_id": df_id})

    department_count = await departments_collection.count_documents({"df_id": df_id, "is_deleted": False})

    role_count = await roles_collection.count_documents({"df_id": df_id, "is_deleted": False})

    accepted_invites = await genie_user_invites_collection.count_documents({"invited_df": df_id, "invite_status": "accepted"})
    pending_invites = await genie_user_invites_collection.count_documents({"invited_df": df_id, "invite_status": "pending"})

    return {
        "user_count": user_count,
        "department_count": department_count,
        "role_count": role_count,
        "invitations": {
            "accepted": accepted_invites,
            "pending": pending_invites,
        },
    }


@router.delete("/remove-members")
async def remove_department_members(
    request: Request,
    department_id: str,
    admin_ids: List[str] = Query([]),
    user_ids: List[str] = Query([]),
    current_user: dict = Depends(get_current_user),
    service: DepartmentService = Depends(get_department_service),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
):
    return await service.remove_department_members(department_id, admin_ids, user_ids, current_user, SYSTEM_ADMIN_ROLE_ID)
