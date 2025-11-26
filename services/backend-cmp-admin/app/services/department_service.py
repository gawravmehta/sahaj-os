from fastapi import HTTPException
from app.crud.department_crud import DepartmentCRUD
from app.crud.user_crud import UserCRUD
from app.schemas.department_schema import AddDepartment, UpdateDepartmentPermission, UpdateDepartmentRequest, UpdateDepartmentUsers
from app.utils.business_logger import log_business_event
from datetime import datetime, UTC
from bson import ObjectId
from typing import List


class DepartmentService:
    def __init__(
        self,
        department_crud: DepartmentCRUD,
        user_crud: UserCRUD,
        business_logs_collection: str,
    ):
        self.department_crud = department_crud
        self.user_crud = user_crud
        self.business_logs_collection = business_logs_collection

    async def add_department(
        self,
        department: AddDepartment,
        current_user: dict,
    ):
        try:
            user_id = str(current_user["_id"])
            df_id = current_user.get("df_id")

            if not df_id:
                await log_business_event(
                    event_type="DEPARTMENT_CREATE_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "reason": "User does not have an associated df_id",
                    },
                    message="Failed to create department",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=400, detail="User does not have an associated df_id")

            existing_department = await self.department_crud.find_by_name(department.department_name, df_id)

            if existing_department:
                await log_business_event(
                    event_type="DEPARTMENT_CREATE_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "reason": "Department with same name already exists",
                    },
                    message="Failed to create department",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(
                    status_code=400,
                    detail="A department with the same name already exists.",
                )

            department_data = {
                "df_id": df_id,
                "department_name": department.department_name,
                "department_description": department.department_description,
                "department_users": [],
                "department_admins": [],
                "created_at": datetime.now(UTC),
                "created_by": user_id,
                "modules_accessible": [],
                "routes_accessible": [],
                "apis_accessible": [],
                "is_deleted": False,
            }

            try:
                result = await self.department_crud.create(department_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database insertion error: {str(e)}")
            await log_business_event(
                event_type="DEPARTMENT_CREATED",
                user_email=current_user["email"],
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "department_id": str(result.inserted_id),
                    "reason": "Department created successfully",
                },
                message="Department created successfully",
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Department added successfully",
                "department_id": str(result.inserted_id),
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def update_department_users(
        self,
        department_id: str,
        update_data: UpdateDepartmentUsers,
        current_user: dict,
        SYSTEM_ADMIN_ROLE_ID: str,
    ):
        try:

            if not ObjectId.is_valid(department_id):
                raise HTTPException(status_code=400, detail="Invalid department_id format")

            department = await self.department_crud.find_by_id(department_id)
            if not department:
                await log_business_event(
                    event_type="UPDATE_DEPT_USERS_NOT_FOUND",
                    user_email=current_user["email"],
                    message="Department not found",
                    log_level="ERROR",
                    context={"user_id": user_id, "df_id": df_id, "department_id": department_id},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=404, detail="Department not found")

            user_roles = current_user.get("user_roles", [])
            user_id = str(current_user["_id"])
            df_id = str(current_user["df_id"])

            is_system_admin = SYSTEM_ADMIN_ROLE_ID in user_roles
            is_department_admin = user_id in department.get("department_admins", [])

            if not (is_department_admin or is_system_admin):
                await log_business_event(
                    event_type="UPDATE_DEPT_USERS_UNAUTHORIZED",
                    user_email=current_user["email"],
                    message="Unauthorized attempt to modify department users",
                    log_level="WARNING",
                    context={"user_id": user_id, "df_id": df_id, "department_id": department_id},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized: Only department admins or system admins can modify department users",
                )

            department_df_id = department.get("df_id")

            async def validate_users(user_ids: List[str]):
                valid_users = set()
                for user_id in user_ids:
                    if ObjectId.is_valid(user_id):
                        user = await self.user_crud.get_user_by_id(user_id)
                        if user and user.df_id == department_df_id:
                            valid_users.add(user_id)
                        else:
                            await log_business_event(
                                event_type="UPDATE_DEPT_USERS_FAILED",
                                user_email=current_user["email"],
                                message="User validation failed",
                                log_level="ERROR",
                                context={"user_id": user_id, "df_id": df_id, "invalid_user": user_id},
                                business_logs_collection=self.business_logs_collection,
                            )
                            raise HTTPException(
                                status_code=400,
                                detail=f"User {user_id} not found or does not belong to the same df_id as the department",
                            )
                return valid_users

            new_users = await validate_users(update_data.department_users)
            new_admins = await validate_users(update_data.department_admins)

            overlapping_users = new_users.intersection(new_admins)
            if overlapping_users:
                await log_business_event(
                    event_type="UPDATE_DEPT_USERS_CONFLICT",
                    user_email=current_user["email"],
                    message="Users cannot be both admins and users",
                    log_level="ERROR",
                    context={"user_id": user_id, "df_id": df_id, "overlap": list(overlapping_users)},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"User(s) {', '.join(overlapping_users)} cannot be both users and admins in the same department.",
                )

            existing_department_users = set(department.get("department_users", []))
            existing_department_admins = set(department.get("department_admins", []))

            duplicate_users = set(new_users).intersection(existing_department_users)

            if duplicate_users:
                user_names = []
                for user_id in duplicate_users:
                    user = await self.user_crud.get_user_by_id(user_id)
                    if user:
                        user_names.append(user.email or user_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"The following users already exist in the department: {', '.join(user_names)}",
                )

            duplicate_admins = set(new_admins).intersection(existing_department_admins)
            if duplicate_admins:
                admin_names = []
                for admin_id in duplicate_admins:
                    admin = await self.user_crud.get_user_by_id(admin_id)
                    if admin:
                        admin_names.append(admin.email or admin_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"The following admins already exist in the department: {', '.join(admin_names)}",
                )

            promoted_users = existing_department_users.intersection(new_admins)
            demoted_admins = existing_department_admins.intersection(new_users)

            existing_department_users.difference_update(promoted_users)

            existing_department_admins.difference_update(demoted_admins)

            updated_users = list(existing_department_users.union(new_users))
            updated_admins = list(existing_department_admins.union(new_admins))

            try:
                await self.department_crud.update_department(
                    department_id,
                    {
                        "department_users": updated_users,
                        "department_admins": updated_admins,
                    },
                )
            except Exception as e:
                await log_business_event(
                    event_type="UPDATE_DEPT_USERS_DB_ERROR",
                    user_email=current_user["email"],
                    message="Database update error",
                    log_level="ERROR",
                    context={"user_id": user_id, "df_id": df_id, "department_id": department_id, "reason": str(e)},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

            for user_id in new_users:
                await self.user_crud.add_department_to_user(user_id, department_id)

            for user_id in new_admins:
                await self.user_crud.add_department_to_user(user_id, department_id)

            await log_business_event(
                event_type="UPDATE_DEPT_USERS_SUCCESS",
                user_email=current_user["email"],
                message="Department users/admins updated successfully",
                log_level="INFO",
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "department_id": department_id,
                    "added_users": list(new_users),
                    "added_admins": list(new_admins),
                    "promoted_users": list(promoted_users),
                    "demoted_admins": list(demoted_admins),
                },
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Department users and admins updated successfully",
                "department_id": department_id,
                "department_users": updated_users,
                "department_admins": updated_admins,
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            await log_business_event(
                event_type="UPDATE_DEPT_USERS_INTERNAL_ERROR",
                user_email=current_user["email"],
                message="Unexpected error while updating department users",
                log_level="ERROR",
                context={"user_id": user_id, "df_id": df_id, "department_id": department_id, "reason": str(e)},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def update_department_permissions(
        self,
        department_id: str,
        update_data: UpdateDepartmentPermission,
        current_user: dict,
        SYSTEM_ADMIN_ROLE_ID: str,
    ):
        try:

            if not ObjectId.is_valid(department_id):
                raise HTTPException(status_code=400, detail="Invalid department_id format")

            department = await self.department_crud.find_by_id(department_id)
            if not department:
                await log_business_event(
                    event_type="UPDATE_DEPT_PERMISSIONS_NOT_FOUND",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "Department not found",
                    },
                    message="Failed to update department permissions",
                    log_level="ERROR",
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=404, detail="Department not found")

            user_roles = current_user.get("user_roles", [])
            user_id = str(current_user["_id"])
            df_id = str(current_user["df_id"])

            is_system_admin = SYSTEM_ADMIN_ROLE_ID in user_roles
            is_department_admin = user_id in department.get("department_admins", [])

            if not (is_department_admin or is_system_admin):
                await log_business_event(
                    event_type="UPDATE_DEPT_PERMISSIONS_UNAUTHORIZED",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "Unauthorized attempt to update permissions",
                    },
                    message="Unauthorized attempt to modify department permissions",
                    log_level="WARNING",
                )
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized: Only department admins or system admins can modify department permissions",
                )

            existing_modules = set(department.get("modules_accessible", []))
            existing_routes = set(department.get("routes_accessible", []))
            existing_apis = set(department.get("apis_accessible", []))

            new_modules = set(update_data.modules_accessible)
            new_routes = set(update_data.routes_accessible)
            new_apis = set(update_data.apis_accessible)

            updated_modules = list(existing_modules.union(new_modules))
            updated_routes = list(existing_routes.union(new_routes))
            updated_apis = list(existing_apis.union(new_apis))

            try:
                await self.department_crud.update_department(
                    department_id,
                    {
                        "modules_accessible": updated_modules,
                        "routes_accessible": updated_routes,
                        "apis_accessible": updated_apis,
                    },
                )
            except Exception as e:
                await log_business_event(
                    event_type="UPDATE_DEPT_PERMISSIONS_DB_ERROR",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": str(e),
                    },
                    message="Database update error while updating department permissions",
                    log_level="ERROR",
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

            await log_business_event(
                event_type="UPDATE_DEPT_PERMISSIONS_SUCCESS",
                user_email=current_user["email"],
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "department_id": department_id,
                    "added_modules": list(new_modules - existing_modules),
                    "added_routes": list(new_routes - existing_routes),
                    "added_apis": list(new_apis - existing_apis),
                },
                message="Department permissions updated successfully",
                log_level="INFO",
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Department permissions updated successfully",
                "department_id": department_id,
                "modules_accessible": updated_modules,
                "routes_accessible": updated_routes,
                "apis_accessible": updated_apis,
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            await log_business_event(
                event_type="UPDATE_DEPT_PERMISSIONS_INTERNAL_ERROR",
                user_email=current_user["email"],
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "department_id": department_id,
                    "reason": str(e),
                },
                message="Internal server error during department permissions update",
                log_level="ERROR",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def search_department(
        self,
        department_name: str,
        current_user: dict,
    ):
        user_email = current_user["email"]
        df_id = current_user.get("df_id")

        try:

            results = await self.department_crud.search_by_name(department_name, df_id)

            if not results:
                await log_business_event(
                    event_type="DEPARTMENT_SEARCH_FAILED",
                    user_email=user_email,
                    context={
                        "df_id": df_id,
                        "search_query": department_name,
                        "reason": "No matching departments found",
                    },
                    message="No matching departments found",
                    business_logs_collection=self.business_logs_collection,
                    log_level="INFO",
                )
                raise HTTPException(status_code=404, detail="No matching departments found")

            for result in results:
                result["_id"] = str(result["_id"])

            await log_business_event(
                event_type="DEPARTMENT_SEARCH_SUCCESS",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "search_query": department_name,
                    "result_count": len(results),
                },
                message="Department search completed successfully",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )
            return results

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def get_all_departments(
        self,
        page: int,
        limit: int,
        current_user: dict,
    ):
        try:

            df_id = current_user.get("df_id")

            if page < 1 or limit < 1:
                await log_business_event(
                    event_type="GET_ALL_DEPARTMENTS_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "df_id": df_id,
                        "page": page,
                        "limit": limit,
                        "reason": "Page and limit must be positive integers",
                    },
                    message="Failed to get all departments due to invalid pagination",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=400, detail="Page and limit must be positive integers")

            skip = (page - 1) * limit

            departments_cursor = await self.department_crud.get_all(df_id, skip=skip, limit=limit)

            departments = [
                {
                    "id": str(dep["_id"]),
                    "department_name": dep["department_name"],
                    "department_description": dep.get("department_description", ""),
                }
                for dep in departments_cursor
            ]

            total_departments = await self.department_crud.count_departments(df_id)

            await log_business_event(
                event_type="GET_ALL_DEPARTMENTS_SUCCESS",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "page": page,
                    "limit": limit,
                    "total_departments": total_departments,
                },
                message="Successfully fetched all departments",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )

            return {
                "page": page,
                "limit": limit,
                "total_departments": total_departments,
                "total_pages": (total_departments // limit) + (1 if total_departments % limit > 0 else 0),
                "data": departments,
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            await log_business_event(
                event_type="GET_ALL_DEPARTMENTS_INTERNAL_ERROR",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "reason": str(e),
                },
                message="Internal server error during fetching all departments",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def get_one_department(
        self,
        department_id: str,
        current_user: dict,
    ):
        user_id = str(current_user["_id"])
        df_id = current_user.get("df_id")

        try:
            if not ObjectId.is_valid(department_id):
                raise HTTPException(status_code=400, detail="Invalid department_id format")

            department = await self.department_crud.find_by_id(department_id)

            if not department:
                await log_business_event(
                    event_type="GET_ONE_DEPARTMENT_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "Department not found",
                    },
                    message="Department not found",
                    business_logs_collection=self.business_logs_collection,
                    log_level="INFO",
                )
                raise HTTPException(status_code=404, detail="Department not found")

            if department["df_id"] != current_user.get("df_id"):
                await log_business_event(
                    event_type="GET_ONE_DEPARTMENT_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": user_id,
                        "df_id": df_id,
                        "department_id": department_id,
                        "department_df_id": department["df_id"],
                        "reason": "Unauthorized access to department",
                    },
                    message="Unauthorized access to department",
                    business_logs_collection=self.business_logs_collection,
                    log_level="WARNING",
                )
                raise HTTPException(status_code=403, detail="Unauthorized access to department")

            department["_id"] = str(department["_id"])

            await log_business_event(
                event_type="GET_ONE_DEPARTMENT_SUCCESS",
                user_email=current_user["email"],
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "department_id": department_id,
                },
                message="Department fetched successfully",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )

            user_ids = department.get("department_users", [])
            admin_ids = department.get("department_admins", [])

            users = await self.user_crud.find_by_ids(user_ids)
            admins = await self.user_crud.find_by_ids(admin_ids)

            def clean_user_data(user):
                user["_id"] = str(user["_id"])
                return user

            department["department_users_data"] = [clean_user_data(user) for user in users]
            department["department_admins_data"] = [clean_user_data(admin) for admin in admins]

            return department

        except HTTPException as e:
            raise e
        except Exception as e:

            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def update_department(
        self,
        department_id: str,
        department: UpdateDepartmentRequest,
        current_user: dict,
    ):
        df_id = str(current_user["df_id"])
        if not ObjectId.is_valid(department_id):
            raise HTTPException(status_code=400, detail="Invalid department_id format")

        try:
            existing_department = await self.department_crud.find_by_id(department_id)
            if not existing_department:
                await log_business_event(
                    event_type="UPDATE_DEPARTMENT_NOT_FOUND",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "Department not found",
                    },
                    message="Failed to update department",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=404, detail="Department not found")

            update_data = department.model_dump(exclude_unset=True)

            if not update_data:
                await log_business_event(
                    event_type="UPDATE_DEPARTMENT_NO_FIELDS",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "No fields provided to update",
                    },
                    message="No fields provided for department update",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=400, detail="No fields provided to update")

            result = await self.department_crud.update_department(department_id, update_data)

            if result.modified_count == 0:
                await log_business_event(
                    event_type="UPDATE_DEPARTMENT_NO_CHANGES",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "df_id": df_id,
                        "department_id": department_id,
                        "reason": "No changes made",
                    },
                    message="Department update attempted but no changes made",
                    business_logs_collection=self.business_logs_collection,
                    log_level="INFO",
                )
                return {"message": "No changes made", "id": department_id}

            await log_business_event(
                event_type="UPDATE_DEPARTMENT_SUCCESS",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "department_id": department_id,
                    "updated_fields": list(update_data.keys()),
                },
                message="Department updated successfully",
                business_logs_collection=self.business_logs_collection,
            )

            return {"message": "Department updated successfully", "id": department_id}

        except HTTPException as e:
            raise e
        except Exception as e:
            await log_business_event(
                event_type="UPDATE_DEPARTMENT_INTERNAL_ERROR",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "department_id": department_id,
                    "reason": str(e),
                },
                message="Internal server error during department update",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def soft_delete_department(
        self,
        department_id: str,
        current_user: dict,
        SYSTEM_ADMIN_ROLE_ID: str,
    ):
        try:

            if not ObjectId.is_valid(department_id):
                raise HTTPException(status_code=400, detail="Invalid department_id format")

            department = await self.department_crud.find_by_id(department_id)
            if not department:
                await log_business_event(
                    event_type="DEPARTMENT_DELETE_FAILED",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "df_id": current_user.get("df_id"),
                        "department_id": department_id,
                        "reason": "Department not found",
                    },
                    message="Failed to soft delete department",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=404, detail="Department not found")

            user_roles = current_user.get("user_roles", [])
            user_id = str(current_user["_id"])

            is_system_admin = SYSTEM_ADMIN_ROLE_ID in user_roles
            is_department_admin = user_id in department.get("department_admins", [])

            if not (is_department_admin or is_system_admin):
                await log_business_event(
                    event_type="DELETE_DEPARTMENT_UNAUTHORIZED",
                    user_email=current_user["email"],
                    context={
                        "user_id": str(current_user["_id"]),
                        "department_id": str(department_id),
                        "reason": "Unauthorized attempt to delete department",
                    },
                    message="User attempted to delete department without required permissions",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized: Only department admins or system admins can delete departments",
                )

            updated_data = {
                "department_name": department["department_name"] + "_deleted",
                "department_users": [],
                "department_admins": [],
                "modules_accessible": [],
                "routes_accessible": [],
                "apis_accessible": [],
                "is_deleted": True,
            }

            try:
                await self.department_crud.update_department(department_id, updated_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database update error: {str(e)}")

            await log_business_event(
                event_type="DEPARTMENT_DELETED",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": current_user.get("df_id"),
                    "department_id": department_id,
                    "reason": "Department soft deleted successfully",
                },
                message="Department soft deleted successfully",
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Department soft deleted successfully",
                "department_id": department_id,
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    async def remove_department_members(
        self,
        department_id: str,
        admin_ids: List[str],
        user_ids: List[str],
        current_user: dict,
        SYSTEM_ADMIN_ROLE_ID: str,
    ):
        df_id = current_user.get("df_id")
        current_user_id = current_user.get("_id")

        department = await self.department_crud.find_by_id(department_id)

        if not department:
            await log_business_event(
                event_type="REMOVE_DEPARTMENT_MEMBERS_FAILED",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "department_id": department_id,
                    "reason": "Department not found",
                },
                message="Failed to remove members from department",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Department not found")

        department_admins = department.get("department_admins", [])
        department_users = department.get("department_users", [])

        is_system_admin = SYSTEM_ADMIN_ROLE_ID in current_user.get("user_roles", [])
        is_department_admin = current_user_id in department_admins
        if not (is_system_admin or is_department_admin):
            await log_business_event(
                event_type="REMOVE_DEPARTMENT_MEMBERS_UNAUTHORIZED",
                user_email=current_user["email"],
                context={
                    "user_id": str(current_user["_id"]),
                    "df_id": df_id,
                    "department_id": department_id,
                    "reason": "User not authorized to remove members",
                },
                message="Unauthorized attempt to remove department members",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )

            raise HTTPException(status_code=403, detail="Only admins can remove members")

        updated_admins = [admin for admin in department_admins if admin not in admin_ids]

        updated_users = [user for user in department_users if user not in user_ids]

        await self.department_crud.update_department(
            department_id,
            {
                "department_admins": updated_admins,
                "department_users": updated_users,
            },
        )
        await log_business_event(
            event_type="REMOVE_DEPARTMENT_MEMBERS_SUCCESS",
            user_email=current_user["email"],
            context={
                "user_id": str(current_user["_id"]),
                "df_id": df_id,
                "department_id": department_id,
                "removed_admins": admin_ids,
                "removed_users": user_ids,
            },
            message="Department members removed successfully",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Members removed successfully",
            "removed_admins": admin_ids,
            "removed_users": user_ids,
        }
