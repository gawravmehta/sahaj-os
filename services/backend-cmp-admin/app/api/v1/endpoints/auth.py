from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.api.v1.deps import get_auth_service, get_current_user
from app.constants.frontend_routes import frontend_routes
from app.schemas.auth_schema import Token, UserInDB, UserLogin, UserOut
from app.services.auth_service import AuthService
from app.db.dependencies import get_user_collection
from app.utils.common import pwd_context
from app.core.security import rbac_enforcer
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.logger import get_logger


router = APIRouter()
logger = get_logger("api.auth")


@router.post("/token", response_model=Token, summary="Authenticate user and get access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    user = await service.authenticate_user(user_login.email, user_login.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await service.create_access_token_for_user(user)
    logger.info(f"User {user.email} logged in successfully.")
    return token


@router.post("/login", response_model=UserOut, summary="Login user and get access token")
async def login_user(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    user_model = await service.authenticate_user(credentials.email, credentials.password)
    token_obj = await service.create_access_token_for_user(user_model)
    logger.info(f"User {user_model.email} logged in successfully via /login endpoint.")
    return UserOut(
        df_id=user_model.df_id,
        access_token=token_obj.access_token,
        is_password_reseted=user_model.is_password_reseted,
        is_org_configured=user_model.is_org_configured,
        is_invited_user=getattr(user_model, "is_invited_user", False),
    )


@router.post("/reset-password")
async def reset_password(new_password: str, user=Depends(get_current_user), users_collection=Depends(get_user_collection)):
    hashed = pwd_context.hash(new_password)
    await users_collection.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"password": hashed, "is_password_reseted": True}})
    logger.info(f"User {user.get('email')} ({user.get('_id')}) reset their password.")
    return {"msg": "Password updated successfully"}


@router.patch("/set-password")
async def set_password(
    request: Request,
    token: str,
    new_password: str = Query(..., min_length=8),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    service: AuthService = Depends(get_auth_service),
):
    user = await user_collection.find_one({"token": token})
    if not user:
        logger.warning(f"Attempted password set with invalid token: {token}")
        raise HTTPException(status_code=404, detail="Invalid token")

    token_expiry = user.get("token_expiry")
    if token_expiry and token_expiry.tzinfo is None:
        token_expiry = token_expiry.replace(tzinfo=UTC)

    if token_expiry and token_expiry < datetime.now(tz=UTC):
        logger.warning(f"Attempted password set with expired token for user {user.get('email')}: {token}")
        raise HTTPException(status_code=400, detail="Token has expired")

    hashed_password = pwd_context.hash(new_password)
    await user_collection.update_one(
        {"token": token}, {"$set": {"password": hashed_password, "is_password_reseted": True, "is_org_configured": True}, "$unset": {"token": ""}}
    )

    user_model = UserInDB(
        id=str(user["_id"]),
        email=user["email"],
        user_roles=user["user_roles"],
        df_id=user["df_id"],
    )

    token_obj = await service.create_access_token_for_user(user_model)
    logger.info(f"User {user_model.email} set their initial password and is now configured.")
    return {"message": "Password set successfully", "access_token": token_obj.access_token}


@router.get("/get-my-profile")
async def get_user_profile(current_user: dict = Depends(get_current_user), user_collection=Depends(get_user_collection)):
    if not current_user:
        logger.warning("Attempted to get profile without authentication.")
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_details = await user_collection.find_one({"_id": ObjectId(current_user["_id"])})
    if not user_details:
        logger.error(f"User details not found for ID: {current_user.get('_id')}")
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = {
        "id": str(current_user["_id"]),
        "first_name": user_details.get("first_name"),
        "last_name": user_details.get("last_name"),
        "email": user_details.get("email"),
        "phone": user_details.get("phone"),
        "designation": user_details.get("designation"),
        "user_roles": user_details.get("user_roles", []),
        "df_id": user_details.get("df_id"),
    }
    logger.info(f"User {current_user.get('email')} fetched their profile.")
    return user_profile


@router.patch("/update-my-profile")
async def update_user_profile(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    designation: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    user_collection=Depends(get_user_collection),
):
    if not current_user:
        logger.warning("Attempted to update profile without authentication.")
        raise HTTPException(status_code=401, detail="Unauthorized")

    update_data = {}
    if first_name is not None:
        update_data["first_name"] = first_name
    if last_name is not None:
        update_data["last_name"] = last_name
    if phone is not None:
        update_data["phone"] = phone
    if designation is not None:
        update_data["designation"] = designation
    if email is not None and email != current_user.get("email"):
        existing_user = await user_collection.find_one({"email": email})
        if existing_user:
            logger.warning(f"User {current_user.get('email')} tried to change email to {email}, which is already in use.")
            raise HTTPException(status_code=400, detail="Email already in use")
        update_data["email"] = email

    if not update_data:
        logger.warning(f"User {current_user.get('email')} attempted profile update with no data.")
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = await user_collection.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": update_data})

    if result.modified_count == 0:
        logger.info(f"User {current_user.get('email')} submitted profile update but no changes were made.")
        raise HTTPException(status_code=400, detail="No changes made to the profile")

    logger.info(f"User {current_user.get('email')} updated their profile. Changes: {update_data}")
    return {"message": "Profile updated successfully"}


@router.get("/get-df-users")
async def get_df_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    search: Optional[str] = Query(None),
    exclude_current_user: Optional[bool] = Query(False),
    current_user: dict = Depends(get_current_user),
    user_collection=Depends(get_user_collection),
):
    try:
        df_id = current_user.get("df_id", "")
        if not df_id:
            raise HTTPException(status_code=400, detail="df_id not found in user")

        query = {"df_id": df_id}

        if exclude_current_user:
            current_user_id = str(current_user["_id"])
            query["_id"] = {"$ne": ObjectId(current_user_id)}

        if search:
            query["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]

        total_users = await user_collection.count_documents(query)
        skip = (page - 1) * page_size

        users_cursor = await user_collection.find(query).skip(skip).limit(page_size).to_list(length=page_size)

        users = []
        for user in users_cursor:
            user["_id"] = str(user["_id"])
            users.append(user)

        return {
            "total_users": total_users,
            "current_page": page,
            "page_size": page_size,
            "total_pages": max(1, (total_users + page_size - 1) // page_size),
            "data": users,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.critical(f"Internal Server Error in get_df_users for DF {current_user.get('df_id')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


available_for_all_roles_routes = [
    "/apps",
    "/apps/get-started",
    "/apps/support",
]


@router.post("/seed-rbac-policies")
async def seed_rbac_policies(admin_role_id):
    rbac_enforcer.load_policy()

    default_policies = []
    for route in frontend_routes:
        default_policies.append((admin_role_id, route["href"], "write"))
        default_policies.append((admin_role_id, route["href"], "read"))

    seeded = False
    for policy in default_policies:
        if not rbac_enforcer.has_policy(*policy):
            rbac_enforcer.add_policy(*policy)
            seeded = True

    if seeded:
        rbac_enforcer.save_policy()
        logger.info("Seeding default RBAC policies...")
    else:
        logger.info("Default RBAC policies already exist, skipping seeding.")


@router.get("/check-access/{path:path}")
async def check_access(
    path: str,
    action: str = Query("read", description="Action to check: read or write"),
    current_user: dict = Depends(get_current_user),
):
    """
    Checks if the current user's roles have permission for a given path and action.
    If a main path (e.g. /apps/data-elements) is accessible, all its subroutes are also accessible.
    """
    try:

        path = "/" + path.lstrip("/")
        path = path.rstrip("/") or "/"

        user_roles = current_user.get("user_roles", [])
        if not user_roles:
            raise HTTPException(status_code=403, detail="User has no roles assigned.")

        if path in available_for_all_roles_routes:
            return {"access": True, "path": path, "action": action}

        for role_id in user_roles:

            if rbac_enforcer.enforce(role_id, path, action):
                return {"access": True, "path": path, "action": action}

            all_policies = rbac_enforcer.get_filtered_policy(0, role_id)
            for policy in all_policies:
                _, policy_path, policy_action = policy
                if policy_action != action:
                    continue

                if path.startswith(policy_path.rstrip("/") + "/"):
                    return {"access": True, "path": path, "action": action}

        logger.info(f"Access denied for user roles {user_roles} on path {path} with action {action}.")
        return {"access": False, "path": path, "action": action}

    except Exception as e:
        logger.critical(f"Server Error in check_access for user {current_user.get('email')}, path {path}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@router.get("/get-my-permissions")
async def get_my_permissions(
    current_user: dict = Depends(get_current_user),
):
    """
    Returns all permissions (path + action) for the user's roles.
    Certain public routes are always accessible by everyone.
    """
    try:

        public_routes = [
            "/apps/get-started",
            "/apps/support",
        ]

        user_roles = current_user.get("user_roles", [])
        if not user_roles:
            raise HTTPException(status_code=403, detail="User has no roles assigned.")

        all_permissions = set()
        structured_permissions = []

        for path in public_routes:
            for action in ["read", "write"]:
                all_permissions.add((path, action))
                structured_permissions.append(
                    {
                        "role": "public",
                        "path": path,
                        "action": action,
                    }
                )

        for role_id in user_roles:
            role_permissions = rbac_enforcer.get_permissions_for_user(role_id)

            for _, path, action in role_permissions:
                if (path, action) not in all_permissions:
                    all_permissions.add((path, action))
                    structured_permissions.append(
                        {
                            "role": role_id,
                            "path": path,
                            "action": action,
                        }
                    )

        logger.info(f"User {current_user.get('email')} fetched their permissions.")
        return {"permissions": structured_permissions}

    except Exception as e:
        logger.critical(f"Server Error in get_my_permissions for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@router.get("/batch-check-access")
async def batch_check_access(
    paths: str = Query(..., description="Comma-separated list of paths to check"),
    action: str = Query("read", description="Action to check: read or write"),
    current_user: dict = Depends(get_current_user),
):
    """
    Checks access for multiple paths for the current user.
    Example: /auth/batch-check-access?paths=/apps/foo,/apps/bar&action=read
    """
    try:
        user_roles = current_user.get("user_roles", [])
        if not user_roles:
            raise HTTPException(status_code=403, detail="User has no roles assigned.")

        path_list = ["/" + p.lstrip("/").rstrip("/") for p in paths.split(",") if p]

        access_results = {}

        for path in path_list:

            if path in available_for_all_roles_routes:
                access_results[path] = True
                continue

            is_allowed = any(rbac_enforcer.enforce(role_id, path, action) for role_id in user_roles)
            access_results[path] = is_allowed

        logger.info(f"User {current_user.get('email')} performed batch access check for paths: {paths}.")
        return {"access": access_results, "action": action}

    except Exception as e:
        logger.critical(f"Server Error in batch_check_access for user {current_user.get('email')}, paths {paths}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
