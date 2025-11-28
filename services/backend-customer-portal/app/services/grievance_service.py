import secrets
import string
from datetime import datetime, UTC
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas import token
from app.utils.mail_utils import mailSender, get_email_credentials
from app.core.logger import app_logger
from app.schemas.grievance_schema import GrievanceCreateRequest
from app.utils.s3_utils import upload_file_to_s3
from app.utils.common import clean_mongo_doc
from app.core.config import settings


class GrievanceService:
    def __init__(self, collection: AsyncIOMotorCollection, df_register_collection: AsyncIOMotorCollection):
        self.collection = collection
        self.df_register_collection = df_register_collection

    async def create_grievance(self, payload: GrievanceCreateRequest, current_user: dict):
        app_logger.info(f"Creating grievance for dp_id: {current_user.get('dp_id')}, email: {payload.email}, mobile: {payload.mobile_number}")
        df_id = current_user.get("df_id")
        dp_id = current_user.get("dp_id")

        token_chars = string.ascii_letters + string.digits
        dp_email_token, dp_mobile_token = None, None
        is_verified = False
        request_status = "open"

        if payload.email:
            dp_email_token = "".join(secrets.choice(token_chars) for _ in range(16))
            verification_link = f"{settings.CUSTOMER_PORTAL_FRONTEND_URL}/verify/e-{dp_email_token}"

            app_logger.info(f"Verification link: {verification_link}")
            credentials = await get_email_credentials(df_id, self.df_register_collection)
            if credentials:
                await mailSender(
                    destination_email=payload.email,
                    subject="DP Grievance Verification Code",
                    email_template=(f"Dear User,\n\nPlease verify your grievance request by clicking:\n{verification_link}\n\n"),
                    credentials=credentials,
                )
            else:
                app_logger.info(f"Grievance verification email sent to {payload.email}")

        if payload.mobile_number:
            dp_mobile_token = "".join(secrets.choice(token_chars) for _ in range(6))

        now = datetime.now(UTC)
        grievance_record = {
            "email": payload.email,
            "mobile_number": payload.mobile_number,
            "dp_id": dp_id,
            "df_id": df_id,
            "is_registered_user": current_user.get("is_existing", False),
            "dp_email_token": dp_email_token,
            "dp_mobile_token": dp_mobile_token,
            "is_verified": is_verified,
            "request_status": request_status,
            "subject": payload.subject,
            "message": payload.message,
            "category": payload.category,
            "sub_category": payload.sub_category,
            "dp_type": payload.dp_type,
            "created_at": now,
            "last_updated_at": now,
            "ticket_allocated": [],
        }

        result = await self.collection.insert_one(grievance_record)
        gr_id = result.inserted_id

        return {"message": "Grievance created successfully", "grievance_id": str(gr_id)}

    async def verify_grievance_token(self, token: str):
        if not token or len(token) < 3 or token[1] != "-":
            raise HTTPException(status_code=400, detail="Invalid token")

        token_type, actual_token = token[0], token[2:]
        query_field = "dp_email_token" if token_type == "e" else "dp_mobile_token" if token_type == "m" else None
        if not query_field:
            raise HTTPException(status_code=400, detail="Unknown token prefix")
        token_chars = string.ascii_letters + string.digits
        new_token = "".join(secrets.choice(token_chars) for _ in range(16))

        query = {query_field: actual_token, "is_verified": False}
        update = {"$set": {"is_verified": True, query_field: new_token}}

        result = await self.collection.update_one(query, update)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Token not found or already verified")

        return {"message": "Token verified successfully", "token": f"{token_type}-{new_token}"}

    async def cancel_grievance_request(self, token: str):
        if not token or len(token) < 3 or token[1] != "-":
            raise HTTPException(status_code=400, detail="Invalid token format")

        token_type, actual_token = token[0], token[2:]
        query_field = "dp_email_token" if token_type == "e" else "dp_mobile_token" if token_type == "m" else None
        if not query_field:
            raise HTTPException(status_code=400, detail="Unknown token prefix")

        query = {query_field: actual_token, "request_status": "open"}
        update = {"$set": {"request_status": "cancelled"}, "$unset": {query_field: ""}}

        result = await self.collection.update_one(query, update)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Token not found or cannot be cancelled anymore")

        return {"status": "success", "message": "Grievance request cancelled successfully", "token": token}

    async def get_all_grievances(self, current_user: dict, skip: int, limit: int):
        df_id = current_user.get("df_id")

        if current_user.get("is_existing"):
            filters = {"dp_id": current_user.get("dp_id"), "df_id": df_id}
        else:
            identifiers = []
            if current_user.get("email"):
                identifiers.append({"email": current_user["email"]})
            if current_user.get("mobile"):
                identifiers.append({"mobile_number": current_user["mobile"]})
            identifiers.append({"df_id": df_id})

            if not identifiers:
                raise HTTPException(status_code=400, detail="Missing email or mobile for non-existing user")

            filters = {"$or": identifiers}

        grievances_cursor = self.collection.find(filters).skip(skip).limit(limit)
        grievances = await grievances_cursor.to_list(length=limit)
        total = await self.collection.count_documents(filters)

        return {"total": total, "data": clean_mongo_doc(grievances)}

    async def get_one_grievance(self, grievance_id: str):
        if not ObjectId.is_valid(grievance_id):
            raise HTTPException(status_code=400, detail="Invalid grievance ID")

        grievance = await self.collection.find_one({"_id": ObjectId(grievance_id)})
        if not grievance:
            raise HTTPException(status_code=404, detail="Grievance not found")

        return clean_mongo_doc(grievance)

    async def upload_reference_document(self, grievance_id: str, files, s3_client):
        user_request = await self.collection.find_one({"_id": ObjectId(grievance_id)})

        if not user_request:
            raise HTTPException(status_code=404, detail="Request not found")

        uploaded_urls = []
        for file in files:
            url = upload_file_to_s3(file, s3_client)
            uploaded_urls.append(url)

        update_data = {"$push": {"uploaded_files": {"$each": uploaded_urls}}}

        await self.collection.update_one({"_id": ObjectId(grievance_id)}, update_data)

        return {
            "status": "success",
            "message": f"{len(uploaded_urls)} reference document(s) uploaded successfully",
            "uploaded_files": uploaded_urls,
        }
