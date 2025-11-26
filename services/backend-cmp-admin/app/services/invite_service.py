from fastapi import HTTPException
from datetime import datetime, timedelta, UTC, timezone
from bson import ObjectId

from app.crud.data_fiduciary_crud import DataFiduciaryCRUD
from app.crud.invite_crud import InviteCRUD
from app.crud.role_crud import RoleCRUD
from app.crud.user_crud import UserCRUD
from app.schemas.invite_schema import InviteModel
from app.utils.invitation import generate_invite_token, get_invitation_html
from app.utils.mail_sender_utils import mail_sender
from app.utils.business_logger import log_business_event
import uuid

from app.core.config import settings


class InviteService:
    def __init__(
        self,
        user_crud: UserCRUD,
        role_crud: RoleCRUD,
        invite_crud: InviteCRUD,
        df_crud: DataFiduciaryCRUD,
        business_logs_collection: str,
        df_register_collection,
    ):
        self.user_crud = user_crud
        self.role_crud = role_crud
        self.invite_crud = invite_crud
        self.df_crud = df_crud
        self.business_logs_collection = business_logs_collection
        self.df_register_collection = df_register_collection

    async def create_invite(self, invite_data: InviteModel, current_user: dict, system_admin_role_id: str):
        current_user_id = current_user["_id"]
        df_id = current_user["df_id"]
        invite_email = invite_data.invited_user_email

        if await self.user_crud.get_user_by_email(invite_email):
            await log_business_event(
                event_type="INVITE_CREATION_FAILED",
                user_email=current_user.get("email"),
                message="Invite creation failed: User already exists",
                log_level="WARNING",
                context={
                    "user_id": str(current_user_id),
                    "df_id": df_id,
                    "invite_email": invite_email,
                    "reason": "User already exists in the system",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="User already exists in the system")

        if await self.invite_crud.get_pending_invite(invite_email):
            await log_business_event(
                event_type="INVITE_CREATION_FAILED",
                user_email=current_user.get("email"),
                message="Invite creation failed: Pending invite already exists",
                log_level="WARNING",
                context={
                    "user_id": str(current_user_id),
                    "df_id": df_id,
                    "invite_email": invite_email,
                    "reason": "Pending invite already exists for this email",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="An invitation is already pending for this email")

        for role_id in invite_data.invited_user_roles:
            if not ObjectId.is_valid(role_id):
                await log_business_event(
                    event_type="INVITE_CREATION_FAILED",
                    user_email=current_user.get("email"),
                    message="Invite creation failed: Invalid role id",
                    log_level="ERROR",
                    context={"user_id": str(current_user_id), "df_id": df_id, "role_id": role_id, "reason": "Invalid role_id format"},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=400, detail=f"Invalid role_id: {role_id}")

            role = await self.role_crud.find_by_id(role_id)
            if not role:
                await log_business_event(
                    event_type="INVITE_CREATION_FAILED",
                    user_email=current_user.get("email"),
                    message="Invite creation failed: Role not found",
                    log_level="ERROR",
                    context={"user_id": str(current_user_id), "df_id": df_id, "role_id": role_id, "reason": "Role not found in database"},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=404, detail=f"Role not found: {role_id}")

            user_roles = current_user.get("user_roles", [])
            user_id = str(current_user["_id"])
            is_system_admin = system_admin_role_id in user_roles
            is_role_creator = user_id == role["created_by"]

            if not (is_role_creator or is_system_admin):
                await log_business_event(
                    event_type="INVITE_CREATION_FAILED",
                    user_email=current_user.get("email"),
                    message=f"Invite creation failed: Permission denied for role {role['role_name']}",
                    log_level="WARNING",
                    context={
                        "user_id": str(current_user_id),
                        "df_id": df_id,
                        "role_id": role_id,
                        "reason": f"Permission denied to assign role '{role['role_name']}'",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"You do not have permission to assign role '{role['role_name']}'",
                )

        while True:
            invite_token = generate_invite_token(prefix=df_id, length=32)
            if not await self.invite_crud.get_invite_by_token(invite_token):
                break

        invite_html = get_invitation_html(invite_data.invited_user_name, invite_token)
        invite_dict = {
            "invited_by": current_user_id,
            "invited_df": df_id,
            "invited_by_name": current_user["email"],
            "invited_user_email": invite_email,
            "invited_user_id": invite_data.invited_user_id,
            "invited_user_name": invite_data.invited_user_name,
            "invited_user_roles": invite_data.invited_user_roles,
            "invited_at": datetime.now(UTC),
            "expiry_at": datetime.now(UTC) + timedelta(days=30),
            "invite_token": invite_token,
            "invite_status": "pending",
            "is_deleted": False,
        }

        await mail_sender(
            invite_email,
            "Invitation to SAHAJ",
            invite_html,
            df_register_collection=self.df_register_collection,
        )

        await self.invite_crud.create_invite(invite_dict)

        await log_business_event(
            event_type="INVITE_CREATED",
            user_email=current_user.get("email"),
            message="Invitation created successfully",
            log_level="INFO",
            context={
                "user_id": str(current_user_id),
                "df_id": df_id,
                "invite_email": invite_email,
                "roles": invite_data.invited_user_roles,
                "invite_token": invite_token,
                "reason": "Invite created successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Invite sent successfully!",
            "invite_url": f"{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}",
            "invite_dev_url": f"{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}",
        }

    async def verify_token(
        self,
        token: str,
    ):

        invite = await self.invite_crud.get_invite_by_token(token)
        if not invite:
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=None,
                context={"reason": "Invalid token", "token": token},
                message=f"Invite verification failed: Invalid token {token}",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Invalid invite token")

        user_detail = await self.user_crud.get_user_by_email(invite["invited_user_email"])

        has_set_password = bool(user_detail and user_detail.password)

        if user_detail and has_set_password:
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=invite["invited_user_email"],
                context={"reason": "User already exists and set password"},
                message=f"Invite verification failed: User '{invite['invited_user_email']}' already exists",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=400,
                detail="User already exists and has set a password. Please log in.",
            )

        if not invite:
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=None,
                context={"reason": "Invalid token", "token": token},
                message=f"Invite verification failed: Invalid token {token}",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Invalid invite token")

        elif invite["invite_status"] == "accepted" and has_set_password:
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=invite["invited_user_email"],
                context={"reason": "Already accepted"},
                message=f"Invite verification failed: Invite already accepted for '{invite['invited_user_email']}'",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Invite has already been accepted")

        expiry_at = invite["expiry_at"]
        if expiry_at.tzinfo is None:
            expiry_at = expiry_at.replace(tzinfo=UTC)

        if expiry_at < datetime.now(UTC):
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=invite["invited_user_email"],
                context={"reason": "Expired token", "expiry": str(expiry_at)},
                message=f"Invite verification failed: Invite expired for '{invite['invited_user_email']}'",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Invite has expired")

        new_forget_password_token = str(uuid.uuid4())
        token_expiry_time = datetime.now(UTC) + timedelta(minutes=10)

        df_data = await self.df_crud.get_data_fiduciary(invite["invited_df"])
        if not df_data:
            await log_business_event(
                event_type="INVITE_VERIFICATION_FAILED",
                user_email=invite["invited_user_email"],
                context={"reason": "DF not found", "df_id": invite["invited_df"]},
                message=f"Invite verification failed: DF not found for '{invite['invited_user_email']}'",
                log_level="WARNING",
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="DF not found")

        name = invite.get("invited_user_name", "").strip()
        parts = name.split()

        first_name = parts[0] if parts else None
        last_name = " ".join(parts[1:]) if len(parts) > 1 else None

        existing_user = await self.user_crud.get_user_by_email(invite["invited_user_email"])
        if existing_user:
            if not existing_user.get("password"):
                raise HTTPException(status_code=400, detail="User already exists but has not set a password. Please reset your password.")
            else:
                await log_business_event(
                    event_type="INVITE_VERIFICATION_FAILED",
                    user_email=invite["invited_user_email"],
                    context={"reason": "User already exists"},
                    message=f"Invite verification failed: User already exists for '{invite['invited_user_email']}'",
                    log_level="WARNING",
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=400, detail="User already exists. Please log in.")

        new_genie_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": invite["invited_user_email"],
            "designation": None,
            "phone": None,
            "df_id": invite["invited_df"],
            "token": new_forget_password_token,
            "is_email_verified": True,
            "user_roles": invite["invited_user_roles"],
            "user_departments": [],
            "password": None,
            "created_at": datetime.now(UTC),
            "token_expiry": token_expiry_time,
            "is_invited_user": True,
        }

        user_id = await self.user_crud.insert_user_data(new_genie_user)
        user_id = str(user_id)

        await self.invite_crud.update_invite_data(
            str(invite["_id"]),
            {"invite_status": "accepted", "invited_user_id": user_id},
        )

        await self.role_crud.add_user_to_roles(
            [role_id for role_id in invite["invited_user_roles"]],
            user_id,
        )

        await log_business_event(
            event_type="INVITE_ACCEPTED",
            user_email=invite["invited_user_email"],
            context={
                "user_id": user_id,
                "df_id": invite["invited_df"],
                "roles_assigned": invite["invited_user_roles"],
                "invite_id": str(invite["_id"]),
            },
            message=f"Invite accepted successfully for {invite['invited_user_email']}",
            log_level="INFO",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Invite accepted successfully!",
            "user_id": user_id,
            "token": new_forget_password_token,
            "token_expiry": token_expiry_time.isoformat(),
        }

    async def get_all_invites(
        self,
        current_user: dict,
        page: int = 1,
        page_size: int = 10,
    ):
        df_id = current_user["df_id"]

        user_email = current_user.get("email")
        user_id = str(current_user["_id"])

        invites = await self.invite_crud.get_invites(df_id, page, page_size)

        if not invites:
            await log_business_event(
                event_type="INVITE_LIST_SUCCESS",
                user_email=user_email,
                message="No invites found for the data fiduciary",
                log_level="INFO",
                context={"user_id": user_id, "df_id": df_id, "page": page, "page_size": page_size, "result_count": 0},
                business_logs_collection=self.business_logs_collection,
            )
            return {"pending": [], "accepted": [], "expired": []}

        pending = []
        accepted = []
        expired = []

        current_time = datetime.now(UTC)

        for invite in invites:
            invite["_id"] = str(invite["_id"])

            expiry_at = invite["expiry_at"]

            if expiry_at.tzinfo is None:
                expiry_at = expiry_at.replace(tzinfo=timezone.utc)

            if invite["invite_status"] == "accepted":
                accepted.append(invite)
            elif expiry_at > current_time and invite["invite_status"] == "pending":
                pending.append(invite)
            elif expiry_at < current_time and invite["invite_status"] == "pending":
                expired.append(invite)

            def paginate(items: list) -> list:
                start = (page - 1) * page_size
                end = start + page_size
                return items[start:end]

            pending_paginated = paginate(pending)
            accepted_paginated = paginate(accepted)
            expired_paginated = paginate(expired)

        await log_business_event(
            event_type="INVITE_LIST_SUCCESS",
            user_email=user_email,
            message="Invites fetched successfully for the data fiduciary",
            log_level="INFO",
            context={
                "user_id": user_id,
                "df_id": df_id,
                "page": page,
                "page_size": page_size,
                "total_invites": len(invites),
                "pending_count": len(pending_paginated),
                "accepted_count": len(accepted_paginated),
                "expired_count": len(expired_paginated),
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "pending": pending_paginated,
            "accepted": accepted_paginated,
            "expired": expired_paginated,
        }

    async def resend_invites(
        self,
        invite_id: str,
        current_user: dict,
    ):
        user_id = str(current_user["_id"])
        df_id = str(current_user["df_id"])
        invite = await self.invite_crud.get_invite_by_id(invite_id)
        if not invite:
            await log_business_event(
                event_type="INVITE_RESEND_FAILED",
                user_email=current_user.get("email"),
                message="Invite resend failed: Invite not found",
                log_level="WARNING",
                context={"invite_id": invite_id, "user_id": user_id, "df_id": df_id, "reason": "Invite not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Invite not found")

        while True:
            new_invite_token = generate_invite_token(prefix=df_id, length=32)
            if not await self.invite_crud.get_invite_by_token(new_invite_token):
                break

        if invite["invite_status"] == "accepted":
            await log_business_event(
                event_type="INVITE_RESEND_FAILED",
                user_email=current_user.get("email"),
                message="Invite resend failed: Already accepted",
                log_level="WARNING",
                context={"invite_id": invite_id, "user_id": user_id, "df_id": df_id, "reason": "Invite has already been accepted"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Invite has already been accepted")

        if invite.get("is_deleted", True):
            await log_business_event(
                event_type="INVITE_RESEND_FAILED",
                user_email=current_user.get("email"),
                message="Invite resend failed: Invite deleted",
                log_level="ERROR",
                context={"invite_id": invite_id, "user_id": user_id, "df_id": df_id, "reason": "Invite is already deleted"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Invite not found")

        new_invited_at = datetime.now(UTC)
        new_expiry_at = new_invited_at + timedelta(days=30)

        await self.invite_crud.update_invite_data(
            invite_id,
            {
                "invite_token": new_invite_token,
                "invited_at": new_invited_at,
                "expiry_at": new_expiry_at,
            },
        )

        invite_html = get_invitation_html(invite.get("invited_user_name", "User"), new_invite_token)

        await mail_sender(
            invite["invited_user_email"],
            "Invitation to SAHAJ",
            invite_html,
            df_register_collection=self.df_register_collection,
        )

        await log_business_event(
            event_type="INVITE_RESENT",
            user_email=current_user.get("email"),
            message="Invitation resent successfully",
            log_level="INFO",
            context={
                "invite_id": str(invite_id),
                "invite_email": invite["invited_user_email"],
                "new_token": new_invite_token,
                "user_id": user_id,
                "df_id": df_id,
                "reason": "Invite resent successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Invite resent successfully!",
            "new_invite_url": f"{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{new_invite_token}",
            "new_invite_dev_url": f"{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{new_invite_token}",
        }

    async def cancel_invite(self, invite_id: str, current_user: dict):
        user_id = str(current_user["_id"])
        df_id = str(current_user["df_id"])

        invite = await self.invite_crud.get_invite_by_id(invite_id)
        if not invite:
            await log_business_event(
                event_type="INVITE_CANCEL_FAILED",
                user_email=current_user.get("email"),
                message="Cancel invite failed: Invite not found",
                log_level="WARNING",
                context={"invite_id": invite_id, "user_id": user_id, "df_id": df_id, "reason": "Invite not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Invite not found")

        if invite.get("is_deleted", True):
            await log_business_event(
                event_type="INVITE_CANCEL_FAILED",
                user_id=str(current_user["_id"]),
                df_id=current_user.get("df_id"),
                user_email=current_user.get("email"),
                message="Cancel invite failed: Invite already deleted",
                log_level="WARNING",
                context={"invite_id": invite_id, "user_id": user_id, "df_id": df_id, "reason": "Invite not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Invite is already deleted")

        await self.invite_crud.soft_delete_invite(invite_id)

        await log_business_event(
            event_type="INVITE_CANCELLED",
            user_email=current_user.get("email"),
            message="Invitation cancelled successfully",
            log_level="INFO",
            context={
                "invite_id": str(invite_id),
                "invite_email": invite["invited_user_email"],
                "user_id": user_id,
                "df_id": df_id,
                "reason": "Invite cancelled successfully",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Invite deleted successfully!"}
