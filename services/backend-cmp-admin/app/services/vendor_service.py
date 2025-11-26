from bson import ObjectId
from app.crud.vendor_crud import VendorCRUD
from app.utils.business_logger import log_business_event
from fastapi import HTTPException
from datetime import datetime, UTC
import re
import string
import random

VALID_VENDOR_SORT_FIELDS = {"dpr_name", "industry", "dpr_country", "created_at"}
VALID_VENDOR_SORT_ORDERS = {"asc", "desc"}


def generate_keys_and_secret(key_size=16, secret_size=64) -> tuple[str, str]:
    key_chars = string.ascii_letters + string.digits
    secret_chars = string.ascii_letters + string.digits + "$@&?!#%^"

    key = "".join(random.choices(key_chars, k=key_size))
    secret = "".join(random.choices(secret_chars, k=secret_size))

    return key, secret


class VendorService:
    def __init__(
        self,
        crud: VendorCRUD,
        user_collection=None,
        business_logs_collection=None,
    ):
        self.crud = crud
        self.user_collection = user_collection
        self.business_logs_collection = business_logs_collection

    async def create_or_update_vendor(
        self,
        vendor_id,
        add_vendor,
        current_user,
    ):
        try:
            genie_user = current_user.get("_id")
            df_id = current_user.get("df_id")

            new_data = add_vendor.model_dump(exclude_unset=True, exclude_defaults=True)

            if vendor_id:
                existing_vendor = await self.crud.get_vendor_by_id(vendor_id) if vendor_id else None

                if existing_vendor:
                    await self.crud.update_vendor(existing_vendor["_id"], new_data)
                    await log_business_event(
                        event_type="VENDOR_UPDATE",
                        user_email=current_user.get("email"),
                        message="Vendor updated successfully",
                        log_level="INFO",
                        context={
                            "user_id": str(genie_user),
                            "df_id": df_id,
                            "vendor_name": existing_vendor["dpr_name"],
                            "vendor_id": str(vendor_id),
                            "reason": "Vendor updated successfully",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )

                    return {
                        "message": "Vendor updated successfully",
                        "vendor_id": vendor_id,
                    }

            new_data["created_by"] = str(genie_user)
            new_data["df_id"] = df_id
            new_data["status"] = "draft"
            new_data["created_at"] = datetime.now(UTC)
            new_data["updated_at"] = datetime.now(UTC)

            result = await self.crud.create_vendor(new_data)
            await log_business_event(
                event_type="VENDOR_CREATE",
                user_email=current_user.get("email"),
                message="Vendor created successfully",
                log_level="INFO",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "vendor_name": add_vendor.dpr_name,
                    "vendor_id": str(result.inserted_id),
                    "reason": "Vendor created successfully",
                },
                business_logs_collection=self.business_logs_collection,
            )
            return {
                "message": "Vendor created successfully",
                "vendor_id": str(result.inserted_id),
            }

        except Exception as e:
            user_email = current_user.get("email")
            await log_business_event(
                event_type="VENDOR_CREATE_OR_UPDATE_FAILED",
                user_email=user_email,
                message=f"Error during vendor create or update: {str(e)}",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "vendor_id": vendor_id,
                    "reason": str(e),
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def edit_data_processing_activities(
        self,
        dpr_id: str,
        data_processing_activities,
        current_user: dict,
    ):
        genie_user = current_user.get("_id")
        df_id = current_user.get("df_id")
        user_email = current_user.get("email")

        update_data = {
            "data_processing_activity": [activity.model_dump() for activity in data_processing_activities],
            "updated_at": datetime.now(UTC),
        }

        try:
            result = await self.crud.update_vendor(dpr_id, update_data)
            if result.modified_count == 1:
                await log_business_event(
                    event_type="DATA_PROCESSING_ACTIVITIES_UPDATE_SUCCESS",
                    user_email=user_email,
                    message="Data processing activities updated successfully",
                    log_level="INFO",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "reason": "Data processing activities updated successfully",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                return {"message": "Data processing activities updated successfully"}
            else:
                await log_business_event(
                    event_type="DATA_PROCESSING_ACTIVITIES_UPDATE_FAILURE",
                    user_email=user_email,
                    message="Failed to update data processing activities: No modification",
                    log_level="WARNING",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "reason": "No changes detected or vendor not found",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail="Failed to update data processing activities: No modification")
        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="DATA_PROCESSING_ACTIVITIES_UPDATE_FAILURE",
                user_email=user_email,
                message=f"Error updating data processing activities: {str(e)}",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "reason": str(e),
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Error updating data processing activities: {str(e)}")

    async def get_all_my_vendors(
        self,
        current_user,
        dpr_country,
        dpr_country_risk,
        industry,
        processing_category,
        cross_border,
        sub_processor,
        audit_result,
        search,
        sort_order,
        page,
        page_size,
    ):
        genie_user = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if sort_order not in VALID_VENDOR_SORT_ORDERS:
            await log_business_event(
                event_type="GET_ALL_VENDORS_FAILURE",
                user_email=user_email,
                message="Invalid sort order provided for fetching vendors",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "sort_order": sort_order,
                    "reason": "Invalid sort_order parameter",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_order. Allowed: {VALID_VENDOR_SORT_ORDERS}",
            )

        query = {"df_id": df_id, "status": {"$ne": "archived"}}

        if dpr_country:
            query["dpr_country"] = {"$regex": dpr_country, "$options": "i"}
        if dpr_country_risk:
            query["dpr_country_risk"] = {"$regex": dpr_country_risk, "$options": "i"}
        if industry:
            query["industry"] = {"$regex": industry, "$options": "i"}
        if processing_category:
            query["processing_category"] = {"$in": [re.compile(val, re.IGNORECASE) for val in processing_category]}
        if cross_border is not None:
            query["cross_border"] = cross_border
        if sub_processor is not None:
            query["sub_processor"] = sub_processor
        if audit_result:
            query["audit_status.audit_result"] = {"$regex": audit_result, "$options": "i"}

        if search:
            query["$or"] = [
                {"dpr_country": {"$regex": search, "$options": "i"}},
                {"industry": {"$regex": search, "$options": "i"}},
                {"dpr_name": {"$regex": search, "$options": "i"}},
            ]

        total_vendors = await self.crud.count_vendors(query)
        vendors = await self.crud.get_vendors(query, sort_order, page, page_size)
        filter_fields = await self.crud.get_filter_fields(df_id)

        await log_business_event(
            event_type="GET_ALL_VENDORS_SUCCESS",
            user_email=user_email,
            message="All vendors fetched successfully",
            log_level="INFO",
            context={
                "user_id": str(genie_user),
                "df_id": df_id,
                "total_vendors": total_vendors,
                "page": page,
                "page_size": page_size,
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "pagination": {
                "total_vendors": total_vendors,
                "current_page": page,
                "page_size": page_size,
                "total_pages": max(1, (total_vendors + page_size - 1) // page_size),
            },
            "filter_fields": filter_fields,
            "sort_order_used": sort_order,
            "vendors": vendors,
        }

    async def get_one_vendor(self, vendor_id: str, current_user: dict):

        genie_user = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        data = await self.crud.get_vendor_by_id(vendor_id)

        if not data:
            await log_business_event(
                event_type="GET_ONE_VENDOR_FAILURE",
                user_email=user_email,
                message="Vendor not found",
                log_level="WARNING",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "vendor_id": vendor_id,
                    "reason": "Vendor does not exist",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="vendor not found")

        created_by_id = data.get("created_by")
        created_by_name = None

        if created_by_id:
            user = await self.user_collection.find_one({"_id": ObjectId(created_by_id)})
            if user:
                first_name = user.get("first_name", "")
                last_name = user.get("last_name", "")
                created_by_name = f"{first_name} {last_name}".strip()

        data["_id"] = str(data["_id"])
        data["created_by"] = str(created_by_id) if created_by_id else None
        data["created_by_name"] = created_by_name

        await log_business_event(
            event_type="GET_ONE_VENDOR_SUCCESS",
            user_email=user_email,
            message="Vendor fetched successfully",
            log_level="INFO",
            context={
                "user_id": str(genie_user),
                "df_id": df_id,
                "vendor_id": vendor_id,
                "vendor_name": data.get("dpr_name"),
            },
            business_logs_collection=self.business_logs_collection,
        )
        return data

    async def delete_vendor(self, dpr_id: str, current_user: dict):
        genie_user = current_user.get("_id")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(dpr_id):
            await log_business_event(
                event_type="DELETE_VENDOR_FAILURE",
                user_email=current_user.get("email"),
                message="Invalid DPR ID format while deleting vendor",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "reason": "Invalid ObjectId format",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Invalid Id format")

        vendor_present = await self.crud.get_vendor_by_id(dpr_id)
        if not vendor_present:
            await log_business_event(
                event_type="DELETE_VENDOR_FAILURE",
                user_email=current_user.get("email"),
                message="Vendor not found while attempting deletion",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "reason": "Vendor not present",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Vendor not present")

        if vendor_present.get("status") == "archived":
            await log_business_event(
                event_type="DELETE_VENDOR_FAILURE",
                user_email=current_user.get("email"),
                message="Attempted to archive an already archived vendor",
                log_level="WARNING",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "status": "archived",
                    "reason": "Already archived",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Already archived")

        try:
            result = await self.crud.archive_vendor(dpr_id)
            if result.modified_count == 1:
                await log_business_event(
                    event_type="DELETE_VENDOR_SUCCESS",
                    user_email=current_user.get("email"),
                    message="Vendor archived successfully",
                    log_level="INFO",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "status": "archived",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                return {"message": "Vendor archived successfully"}
            else:
                await log_business_event(
                    event_type="DELETE_VENDOR_FAILURE",
                    user_email=current_user.get("email"),
                    message="Failed to archive vendor",
                    log_level="ERROR",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "reason": "Database update failed or no modification",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail="Failed to archive vendor")
        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="DELETE_VENDOR_FAILURE",
                user_email=current_user.get("email"),
                message=f"Unhandled exception during vendor deletion: {str(e)}",
                log_level="ERROR",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "reason": str(e),
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Failed to archive vendor: {str(e)}")

    async def make_it_publish(
        self,
        dpr_id: str,
        current_user: dict,
    ):
        try:
            genie_user = current_user.get("_id")
            df_id = current_user.get("df_id")

            if not ObjectId.is_valid(dpr_id):
                await log_business_event(
                    event_type="MAKE_IT_PUBLISH_FAILURE",
                    user_email=current_user.get("email"),
                    message="Invalid DPR ID format while publishing vendor",
                    log_level="ERROR",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "reason": "Invalid ObjectId format",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=400, detail="Invalid ID format")

            vendor_present = await self.crud.get_vendor_by_id(dpr_id)
            if not vendor_present:
                await log_business_event(
                    event_type="MAKE_IT_PUBLISH_FAILURE",
                    user_email=current_user.get("email"),
                    message="Vendor not found while publishing",
                    log_level="ERROR",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=404, detail="Vendor not found")

            api_key, api_secret = generate_keys_and_secret()

            update_result = await self.crud.update_vendor(
                dpr_id,
                {
                    "status": "published",
                    "api_key": api_key,
                    "api_secret": api_secret,
                },
            )

            for purpose in vendor_present.get("data_processing_activity", []):
                update_purpose = await self.crud.update_purpose_with_vendor(
                    purpose_id=purpose.get("purpose_id"),
                    vendor_details={
                        "vendor_id": vendor_present.get("_id"),
                        "vendor_name": vendor_present.get("dpr_name"),
                        "cross_border": vendor_present.get("cross_border"),
                    },
                )

            if update_result.modified_count == 0:
                await log_business_event(
                    event_type="MAKE_IT_PUBLISH_FAILURE",
                    user_email=current_user.get("email"),
                    message="Failed to update vendor during publish",
                    log_level="ERROR",
                    context={
                        "user_id": str(genie_user),
                        "df_id": df_id,
                        "dpr_id": dpr_id,
                        "reason": "Database update failed or no modification",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail="Failed to update vendor")

            await log_business_event(
                event_type="MAKE_IT_PUBLISH_SUCCESS",
                user_email=current_user.get("email"),
                message="Vendor published successfully",
                log_level="INFO",
                context={
                    "user_id": str(genie_user),
                    "df_id": df_id,
                    "dpr_id": dpr_id,
                    "api_key": api_key,
                    "status": "published",
                },
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Vendor published successfully",
                "api_key": api_key,
            }

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="MAKE_IT_PUBLISH_FAILURE",
                user_email=current_user.get("email"),
                message="Unhandled exception during vendor publish",
                log_level="ERROR",
                context={
                    "user_id": str(current_user.get("_id")),
                    "df_id": current_user.get("df_id"),
                    "dpr_id": dpr_id,
                    "reason": str(e),
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=str(e))
