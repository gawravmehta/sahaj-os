from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db.dependencies import get_system_admin_role_id
from app.schemas.role_schema import (
    AddRole,
    UpdateRoleUser,
    UpdateRolePermissions,
    UpdateRole,
    AssignRolesToUser,
)
from app.api.v1.deps import get_current_user, get_role_service

from app.services.role_service import RoleService


router = APIRouter()


@router.post("/add-role")
async def add_role_endpoint(
    role: AddRole,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    try:
        return await service.add_role(role, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.get("/get-all-roles", summary="Fetch all roles with pagination")
async def get_all_roles_endpoint(
    page: int = Query(1, description="Page number, default is 1"),
    limit: int = Query(10, description="Number of items per page, default is 10"),
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    try:
        return await service.get_all_roles(current_user=current_user, page=page, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.get("/get-one-role/{role_id}", summary="Fetch one role by ID")
async def get_role_endpoint(
    role_id: str,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    try:
        return await service.get_one_role(role_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.get("/get-all-role-users")
async def get_all_role_users(
    role_id: str,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    try:
        return await service.get_all_role_users(role_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.patch("/update-role-users/{role_id}")
async def update_role_users_endpoint(
    role_id: str,
    update_data: UpdateRoleUser,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
):
    try:
        return await service.update_role_users(role_id, update_data, current_user, SYSTEM_ADMIN_ROLE_ID)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.patch("/update-role-permissions/{role_id}")
async def update_role_permissions_endpoint(
    role_id: str,
    update_data: UpdateRolePermissions,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
    SYSTEM_ADMIN_ROLE_ID: str = Depends(get_system_admin_role_id),
):
    return await service.update_role_permissions(role_id, update_data, current_user, SYSTEM_ADMIN_ROLE_ID)


@router.get("/search-role")
async def search_role_endpoint(
    role_name: str = Query(..., description="Search role by name"),
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    return await service.search_role(role_name, current_user)


@router.patch("/update-role/{role_id}")
async def update_role_endpoint(
    role_id: str,
    update_data: UpdateRole,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
    system_admin_role_id: str = Depends(get_system_admin_role_id),
):
    return await service.update_role(role_id, update_data, current_user, system_admin_role_id)


@router.delete("/delete-role/{role_id}")
async def delete_role_endpoint(
    role_id: str,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
    system_admin_role_id: str = Depends(get_system_admin_role_id),
):
    return await service.soft_delete_role(role_id, current_user, system_admin_role_id)


@router.patch("/assign-roles-to-user/{user_id}")
async def assign_multiple_roles_to_user(
    user_id: str,
    data: AssignRolesToUser,
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
    system_admin_role_id: str = Depends(get_system_admin_role_id),
):
    return await service.assign_roles_to_user(user_id, data.roles_list, current_user, system_admin_role_id)


@router.get("/get-all-frontend-routes")
async def get_all_frontend_routes(
    current_user: dict = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
):
    return await service.get_all_frontend_routes(current_user)
