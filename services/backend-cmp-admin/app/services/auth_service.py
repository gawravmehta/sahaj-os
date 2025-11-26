from datetime import UTC, datetime, timedelta
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from app.core.security import verify_password, create_access_token, get_password_hash
from app.crud.user_crud import UserCRUD
from app.schemas.auth_schema import UserLogin, Token, UserInDB

from app.core.config import settings
from app.utils.business_logger import log_business_event
from motor.motor_asyncio import AsyncIOMotorCollection
from app.utils.common import pwd_context


class AuthService:
    def __init__(
        self,
        user_crud,
        business_logs_collection,
        user_collection,
        df_register_collection,
    ):
        self.user_crud = user_crud
        self.business_logs_collection = business_logs_collection
        self.user_collection = user_collection
        self.df_register_collection = df_register_collection

    async def authenticate_user(self, email: str, password: str) -> UserInDB:
        """Authenticate user by email and password."""
        user_data = await self.user_crud.get_user_by_email(email)

        if not user_data:
            await log_business_event(
                event_type="LOGIN_FAILED",
                user_email=email,
                context={"reason": "User not found"},
                message=f"Authentication failed: User '{email}' not found",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not pwd_context.verify(password, user_data.password):
            await log_business_event(
                event_type="LOGIN_FAILED",
                user_email=email,
                context={"reason": "Incorrect password"},
                message=f"Authentication failed: Incorrect password for user '{email}'",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        df_id = user_data.df_id
        if not df_id:
            df_id = str(uuid.uuid4())
            await self.df_register_collection.insert_one(
                {
                    "name": "Default Organization",
                    "created_at": datetime.now(UTC),
                    "df_id": df_id,
                    "configured": False,
                }
            )
            await self.user_collection.update_one({"_id": user_data["_id"]}, {"$set": {"df_id": df_id}})

        await log_business_event(
            event_type="LOGIN_SUCCESS",
            user_email=email,
            context={"user_id": str(user_data.id)},
            message=f"User '{email}' authenticated successfully",
            log_level="INFO",
            business_logs_collection=self.business_logs_collection,
        )

        return UserInDB(
            id=str(user_data.id),
            email=user_data.email,
            user_roles=user_data.user_roles,
            df_id=df_id,
            is_password_reseted=user_data.is_password_reseted,
            is_org_configured=user_data.is_org_configured,
            is_invited_user=getattr(user_data, "is_invited_user", False),
        )

    async def create_access_token_for_user(self, user: UserInDB) -> Token:
        """Generate JWT access token for authenticated user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {
            "sub": str(user.id),
            "email": user.email,
            "user_roles": user.user_roles,
        }
        access_token = create_access_token(data=data, expires_delta=access_token_expires)
        await log_business_event(
            event_type="ACCESS_TOKEN_CREATED",
            user_email=user.email,
            context={"user_id": str(user.id), "df_id": user.df_id},
            message=f"Access token created for user '{user.email}'",
            log_level="INFO",
            business_logs_collection=self.business_logs_collection,
        )
        return Token(access_token=access_token)
