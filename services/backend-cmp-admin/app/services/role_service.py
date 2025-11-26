from fastapi import HTTPException
from datetime import datetime, UTC
from app.core.rbac import reset_role_policies
from app.crud.user_crud import UserCRUD
from app.schemas.role_schema import AddRole, UpdateRole, UpdateRolePermissions, UpdateRoleUser
from app.crud.role_crud import RoleCRUD
from app.utils.business_logger import log_business_event
from typing import Any, Dict
from bson import ObjectId


class RoleService:
    def __init__(self, role_crud: RoleCRUD, user_crud: UserCRUD, user_collection=None, business_logs_collection=None):
        self.role_crud = role_crud
        self.user_crud = user_crud
        self.user_collection = user_collection
        self.business_logs_collection = business_logs_collection

    async def add_role(self, role: AddRole, current_user: dict):
        try:
            user_id = str(current_user["_id"])
            df_id = current_user.get("df_id")

            existing_role = await self.role_crud.find_by_name(role.role_name, df_id)
            if existing_role:
                await log_business_event(
                    event_type="ROLE_CREATION_FAILED",
                    user_email=current_user.get("email"),
                    message="Role creation failed: Role already exists",
                    log_level="WARNING",
                    context={"user_id": user_id, "df_id": df_id, "role_name": role.role_name, "reason": "Role with this name already exists"},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=400, detail="Role with this name already exists")

            role_data = {
                "df_id": df_id,
                "role_name": role.role_name,
                "role_description": role.role_description,
                "role_users": [],
                "created_at": datetime.now(UTC),
                "created_by": user_id,
                "modules_accessible": [],
                "routes_accessible": [],
                "apis_accessible": [],
                "is_deleted": False,
            }

            result = await self.role_crud.insert(role_data)
            await log_business_event(
                event_type="ROLE_CREATED",
                user_email=current_user.get("email"),
                message="Role created successfully",
                log_level="INFO",
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "role_name": role.role_name,
                    "role_id": str(result.inserted_id),
                    "reason": "Role added successfully",
                },
                business_logs_collection=self.business_logs_collection,
            )
            return {"message": "Role added successfully", "role_id": str(result.inserted_id)}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding role: {str(e)}")

    async def get_all_roles(self, current_user: dict, page: int, limit: int) -> Dict[str, Any]:
        df_id = current_user.get("df_id")
        if page < 1 or limit < 1:
            raise HTTPException(status_code=400, detail="Page and limit must be positive integers")

        skip = (page - 1) * limit
        roles = await self.role_crud.get_roles_paginated(df_id, skip, limit)
        total_roles = await self.role_crud.count_roles(df_id)

        formatted_roles = [
            {
                "id": str(role["_id"]),
                "role_name": role["role_name"],
                "role_description": role.get("role_description", ""),
                "routes_accessible": role.get("routes_accessible", []),
            }
            for role in roles
        ]

        return {
            "page": page,
            "limit": limit,
            "total_roles": total_roles,
            "total_pages": (total_roles // limit) + (1 if total_roles % limit > 0 else 0),
            "data": formatted_roles,
        }

    async def get_one_role(self, role_id: str, current_user: dict) -> Dict[str, Any]:
        role = await self.role_crud.find_by_id(role_id)

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        role["_id"] = str(role["_id"])

        user_ids = role.get("role_users", [])
        if self.user_collection is not None and user_ids:
            users = await self.user_collection.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}).to_list(length=None)

            for user in users:
                user["_id"] = str(user["_id"])

            role["role_users_data"] = users
        else:
            role["role_users_data"] = []

        return role

    async def get_all_role_users(self, role_id: str, current_user: dict) -> Dict[str, Any]:
        role = await self.role_crud.get_role_users(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        role_users = role.get("role_users", [])
        all_user_ids = [ObjectId(uid) for uid in role_users]

        users = await self.user_collection.find({"_id": {"$in": all_user_ids}}).to_list(length=None)

        def clean_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
            user["_id"] = str(user["_id"])
            return user

        return {
            "role_id": role_id,
            "total_users": len(all_user_ids),
            "users": [clean_user_data(u) for u in users],
        }

    async def update_role_users(
        self,
        role_id: str,
        update_data: UpdateRoleUser,
        current_user: Dict[str, Any],
        system_admin_role_id: str,
    ):

        role = await self.role_crud.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user_roles = current_user.get("user_roles", [])
        df_id = current_user.get("df_id")
        genie_user_id = str(current_user["_id"])

        is_system_admin = system_admin_role_id in user_roles
        is_role_creator = genie_user_id == role["created_by"]
        if not (is_system_admin or is_role_creator):
            await log_business_event(
                event_type="ROLE_USERS_UPDATE_FAILED",
                user_email=current_user.get("email"),
                message="Unauthorized to modify role users",
                log_level="WARNING",
                context={
                    "user_id": genie_user_id,
                    "df_id": df_id,
                    "role_id": role_id,
                    "reason": "Only role creators or system admins can modify role users",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: Only role creators or system admins can modify role users",
            )

        role_df_id = role.get("df_id")

        valid_users = set()
        for user_id in update_data.users_list:
            user = await self.user_crud.get_user_by_id(user_id)
            if not user or user.df_id != role_df_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"User {user_id} not found or does not belong to the same df_id",
                )
            valid_users.add(user_id)

        existing_users = set(role.get("role_users", []))
        new_users = valid_users - existing_users
        if not new_users:
            await log_business_event(
                event_type="ROLE_USERS_UPDATE_FAILED",
                user_email=current_user.get("email"),
                message="No new users to add",
                log_level="WARNING",
                context={"user_id": genie_user_id, "df_id": df_id, "role_id": role_id, "reason": "All users already exist in the role"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "No new users to add. All users already exist in the role.",
                    "role_id": role_id,
                    "updated_users": list(existing_users),
                },
            )

        updated_users = list(existing_users.union(new_users))

        try:
            await self.role_crud.update_role_users(role_id, updated_users)
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

        for user_id in new_users:
            try:
                await self.user_crud.add_role_to_user(user_id, role_id)
            except HTTPException as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error updating user {user_id} roles: {str(e)}",
                )
        await log_business_event(
            event_type="ROLE_USERS_UPDATED",
            user_email=current_user.get("email"),
            message="Users added to role successfully",
            log_level="INFO",
            context={
                "user_id": genie_user_id,
                "df_id": df_id,
                "role_id": role_id,
                "added_users": list(new_users),
                "updated_users": updated_users,
                "reason": "Users added successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Users added to role successfully",
            "role_id": role_id,
            "updated_users": updated_users,
        }

    async def update_role_permissions(
        self,
        role_id: str,
        update_data: UpdateRolePermissions,
        current_user: dict,
        system_admin_role_id: str,
    ):
        role = await self.role_crud.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user_roles = current_user.get("user_roles", [])
        genie_user_id = str(current_user["_id"])
        df_id = current_user.get("df_id")

        is_system_admin = system_admin_role_id in user_roles
        is_role_creator = genie_user_id == role["created_by"]

        if not (is_system_admin or is_role_creator):
            await log_business_event(
                event_type="ROLE_PERMISSIONS_UPDATE_FAILED",
                user_email=current_user.get("email"),
                message="Unauthorized to modify role permissions",
                log_level="WARNING",
                context={
                    "user_id": genie_user_id,
                    "df_id": df_id,
                    "role_id": role_id,
                    "reason": "Only role creators or system admins can modify role permissions",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: Only role creators or system admins can modify role permissions",
            )

        sanitized_routes = []
        for r in update_data.routes_accessible:
            if not getattr(r, "path", None):
                continue
            actions = list(dict.fromkeys(r.actions or []))
            sanitized_routes.append({"path": r.path, "actions": actions})

        try:
            await self.role_crud.update_role_permissions(role_id, sanitized_routes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

        reset_role_policies(role_id, sanitized_routes)
        await log_business_event(
            event_type="ROLE_PERMISSIONS_UPDATED",
            user_email=current_user.get("email"),
            message="Role permissions updated successfully",
            log_level="INFO",
            context={
                "user_id": genie_user_id,
                "df_id": df_id,
                "role_id": role_id,
                "routes_accessible": sanitized_routes,
                "reason": "Permissions updated successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Role permissions updated successfully",
            "role_id": role_id,
            "routes_accessible": sanitized_routes,
        }

    async def search_role(self, role_name: str, current_user: dict):
        df_id = current_user.get("df_id")
        roles_list = await self.role_crud.search_roles(df_id, role_name)

        roles = [
            {
                "id": str(role["_id"]),
                "role_name": role["role_name"],
                "role_description": role.get("role_description", ""),
            }
            for role in roles_list
        ]

        if not roles:
            raise HTTPException(status_code=404, detail="No matching roles found")

        return {"data": roles}

    async def update_role(self, role_id: str, update_data: UpdateRole, current_user: dict, system_admin_role_id: str):
        if not ObjectId.is_valid(role_id):
            raise HTTPException(status_code=400, detail="Invalid role_id format")

        role = await self.role_crud.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user_roles = current_user.get("user_roles", [])
        genie_user_id = str(current_user["_id"])
        df_id = current_user.get("df_id")

        is_system_admin = system_admin_role_id in user_roles
        is_role_creator = genie_user_id == role["created_by"]

        if not (is_role_creator or is_system_admin):
            await log_business_event(
                event_type="ROLE_UPDATE_FAILED",
                user_email=current_user.get("email"),
                message="Unauthorized to update role",
                log_level="WARNING",
                context={
                    "user_id": genie_user_id,
                    "df_id": df_id,
                    "role_id": role_id,
                    "reason": "Only role creators or system admins can update roles",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: Only role creators or system admins can modify roles",
            )

        update_fields = {}
        if update_data.role_name:
            update_fields["role_name"] = update_data.role_name
        if update_data.role_description:
            update_fields["role_description"] = update_data.role_description

        if not update_fields:
            await log_business_event(
                event_type="ROLE_UPDATE_FAILED",
                user_email=current_user.get("email"),
                message="No valid fields to update",
                log_level="WARNING",
                context={"user_id": genie_user_id, "df_id": df_id, "role_id": role_id, "reason": "No fields provided for update"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="No valid fields to update")

        try:
            await self.role_crud.update_role(role_id, update_fields)
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

        await log_business_event(
            event_type="ROLE_UPDATED",
            user_email=current_user.get("email"),
            message="Role updated successfully",
            log_level="INFO",
            context={
                "user_id": genie_user_id,
                "df_id": df_id,
                "role_id": role_id,
                "updated_fields": update_fields,
                "reason": "Role updated successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Role updated successfully",
            "role_id": role_id,
            "updated_fields": update_fields,
        }

    async def soft_delete_role(self, role_id: str, current_user: dict, system_admin_role_id: str):
        if not ObjectId.is_valid(role_id):
            raise HTTPException(status_code=400, detail="Invalid role_id format")

        role = await self.role_crud.find_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user_roles = current_user.get("user_roles", [])
        genie_user_id = str(current_user["_id"])
        df_id = current_user.get("df_id")

        is_system_admin = system_admin_role_id in user_roles
        is_role_creator = genie_user_id == role["created_by"]

        if not (is_role_creator or is_system_admin):
            await log_business_event(
                event_type="ROLE_DELETE_FAILED",
                user_email=current_user.get("email"),
                message="Unauthorized to delete role",
                log_level="WARNING",
                context={
                    "user_id": genie_user_id,
                    "df_id": df_id,
                    "role_id": role_id,
                    "reason": "Only role creators or system admins can delete roles",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: Only role creators or system admins can delete roles",
            )

        updated_data = {
            "role_name": role["role_name"] + "_deleted",
            "role_users": [],
            "modules_accessible": [],
            "routes_accessible": [],
            "apis_accessible": [],
            "is_deleted": True,
        }

        try:
            await self.role_crud.soft_delete_role(role_id, updated_data)
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

        await log_business_event(
            event_type="ROLE_SOFT_DELETED",
            user_email=current_user.get("email"),
            message="Role soft deleted successfully",
            log_level="INFO",
            context={"user_id": genie_user_id, "df_id": df_id, "role_id": role_id, "reason": "Role soft deleted successfully"},
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Role soft deleted successfully",
            "role_id": role_id,
        }

    async def assign_roles_to_user(self, user_id: str, roles: list[str], current_user: dict, system_admin_role_id: str):
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        user = await self.user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        genie_user_id = str(current_user["_id"])
        df_id = str(current_user["df_id"])
        current_user_roles = set(current_user.get("user_roles", []))
        is_system_admin = system_admin_role_id in current_user_roles
        if user.df_id != current_user.get("df_id") and not is_system_admin:
            await log_business_event(
                event_type="ASSIGN_ROLE_FAILED",
                user_email=current_user.get("email"),
                message="Unauthorized to assign roles to user",
                log_level="WARNING",
                context={"user_id": genie_user_id, "df_id": df_id, "target_user_id": user_id, "reason": "Cannot assign roles across different df_id"},
                business_logs_collection=self.business_logs_collection,
            )

            raise HTTPException(status_code=403, detail="Unauthorized action")

        existing_roles = set(user.user_roles)
        newly_added_roles = []

        for role_id in roles:
            if not ObjectId.is_valid(role_id):
                raise HTTPException(status_code=400, detail=f"Invalid role ID: {role_id}")

            role = await self.role_crud.find_by_id(role_id)
            if not role:
                raise HTTPException(status_code=404, detail=f"Role not found: {role_id}")

            if role.get("df_id") != user.df_id:
                raise HTTPException(status_code=400, detail=f"Role {role_id} belongs to a different df_id")

            if role_id not in existing_roles:
                await self.user_crud.add_role_to_user(user_id, role_id)
                newly_added_roles.append(role_id)

            await self.role_crud.add_user_to_role(role_id, user_id)

        await log_business_event(
            event_type="ROLES_ASSIGNED",
            user_email=current_user.get("email"),
            message="Roles assigned to user successfully",
            log_level="INFO",
            context={
                "user_id": genie_user_id,
                "df_id": df_id,
                "target_user_id": user_id,
                "roles_assigned": newly_added_roles,
                "reason": "Roles assigned successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Roles assigned to user successfully",
            "user_id": user_id,
            "roles_assigned": newly_added_roles,
        }

    async def get_all_frontend_routes(self, current_user: dict):
        from app.constants.frontend_routes import frontend_routes

        return {"data": frontend_routes}
