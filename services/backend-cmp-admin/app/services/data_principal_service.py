import json
import re
import uuid
from fastapi import HTTPException
from app.utils.business_logger import log_business_event
from app.crud.data_principal_crud import DataPrincipalCRUD
from app.schemas.data_principal_schema import UpdateDP
from app.utils.common import hash_shake256
from app.utils.data_principal import mask_email, mask_mobile
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection


class DataPrincipalService:
    def __init__(self, data_principal_crud: DataPrincipalCRUD, consent_latest_artifacts: AsyncIOMotorCollection, business_logs_collection: str):
        self.data_principal_crud = data_principal_crud
        self.consent_latest_artifacts = consent_latest_artifacts
        self.business_logs_collection = business_logs_collection

    async def add_data_principal(self, dp_data_list: List[Dict[str, Any]], user: Dict[str, Any]):
        table_name = "dpd"

        user_email = user.get("email")
        df_id = user.get("df_id")

        await self.data_principal_crud.ensure_table(table_name)

        principal_ids = []
        for dp_data in dp_data_list:
            if not dp_data.get("dp_system_id") or str(dp_data["dp_system_id"]).strip() == "":
                raise HTTPException(status_code=400, detail="System ID is required.")

            if "email" in dp_data.dp_identifiers:
                if not dp_data.dp_email or len(dp_data.dp_email) == 0:
                    raise HTTPException(status_code=400, detail="At least one email is required.")
                if len(dp_data.dp_email) != len(set(dp_data.dp_email)):
                    raise HTTPException(status_code=400, detail="Duplicate emails found.")
                for email in dp_data.dp_email:
                    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                        raise HTTPException(status_code=400, detail="Invalid email address")

            if "mobile" in dp_data.dp_identifiers:
                if not dp_data.dp_mobile or len(dp_data.dp_mobile) == 0:
                    raise HTTPException(status_code=400, detail="At least one mobile is required.")
                if len(dp_data.dp_mobile) != len(set(dp_data.dp_mobile)):
                    raise HTTPException(status_code=400, detail="Duplicate mobile numbers found.")
                for mobile in dp_data.dp_mobile:
                    if mobile == 0 or not re.match(r"^\d{10}$", str(mobile)):
                        raise HTTPException(status_code=400, detail="Invalid mobile number")

            result_system_id = await self.data_principal_crud.get_by_system_id(table_name, dp_data.dp_system_id)
            if result_system_id:
                existing_emails, existing_mobiles, is_deleted = result_system_id
                if is_deleted:
                    updated = False
                    if dp_data.dp_email and not all(email in existing_emails for email in dp_data.dp_email):
                        existing_emails = list(set(existing_emails + dp_data.dp_email))
                        updated = True
                    if dp_data.dp_mobile and not all(mobile in existing_mobiles for mobile in dp_data.dp_mobile):
                        existing_mobiles = list(set(existing_mobiles + dp_data.dp_mobile))
                        updated = True

                    if updated:
                        await self.data_principal_crud.insert_or_update_deleted(table_name, dp_data.dp_system_id, existing_emails, existing_mobiles)
                        await log_business_event(
                            event_type="ADD_DP_REACTIVATED",
                            user_email=user_email,
                            message=f"Re-activated deleted Data Principal for system_id={dp_data.dp_system_id}",
                            log_level="INFO",
                            context={
                                "dp_system_id": dp_data.dp_system_id,
                                "df_id": df_id,
                                "emails": existing_emails,
                                "mobiles": existing_mobiles,
                                "added_by": user_email,
                            },
                            business_logs_collection=self.business_logs_collection,
                        )
                        return {"message": "Data Principal re-activated", "principal_id": None}
                else:
                    await log_business_event(
                        event_type="ADD_DP_FAILURE",
                        user_email=user_email,
                        message=f"Duplicate system_id detected: {dp_data.dp_system_id}",
                        log_level="ERROR",
                        context={
                            "dp_system_id": dp_data.dp_system_id,
                            "df_id": df_id,
                            "added_by": user_email,
                            "reason": "System ID already exists",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(status_code=400, detail="System ID already exists.")

            hashed_emails = [hash_shake256(email) for email in dp_data.dp_email] if dp_data.dp_email else []
            hashed_mobiles = [hash_shake256(str(m)) for m in dp_data.dp_mobile] if dp_data.dp_mobile else []

            dp_mobiles_as_str = [str(m) for m in dp_data.dp_mobile] if dp_data.dp_mobile else []

            final_data = {
                "dp_id": str(uuid.uuid4()),
                "dp_system_id": dp_data.dp_system_id,
                "dp_identifiers": dp_data.dp_identifiers,
                "dp_email": dp_data.dp_email,
                "dp_mobile": dp_mobiles_as_str,
                "dp_other_identifier": dp_data.dp_other_identifier,
                "dp_preferred_lang": dp_data.dp_preferred_lang,
                "dp_country": dp_data.dp_country,
                "dp_state": dp_data.dp_state,
                "dp_tags": dp_data.dp_tags if dp_data.dp_tags else None,
                "dp_active_devices": dp_data.dp_active_devices if dp_data.dp_active_devices else None,
                "is_active": dp_data.is_active,
                "is_legacy": dp_data.is_legacy,
                "added_by": user.get("_id"),
                "added_with": "manual",
                "df_id": df_id,
                "created_at_df": dp_data.created_at_df.replace(tzinfo=None) if dp_data.created_at_df else None,
                "last_activity": dp_data.last_activity.replace(tzinfo=None) if dp_data.last_activity else None,
                "dp_e": hashed_emails,
                "dp_m": hashed_mobiles,
                "is_deleted": False,
                "consent_count": 0,
                "consent_status": "unsent",
            }
            principal_ids.append(final_data["dp_id"])

            await self.data_principal_crud.insert(table_name, final_data)

            await log_business_event(
                event_type="ADD_DP_SUCCESS",
                user_email=user_email,
                message=f"Data Principal added successfully for system_id={dp_data.dp_system_id}",
                log_level="INFO",
                context={
                    "dp_id": final_data["dp_id"],
                    "dp_system_id": dp_data.dp_system_id,
                    "df_id": df_id,
                    "added_by": user_email,
                    "emails": dp_data.dp_email,
                    "mobiles": dp_data.dp_mobile,
                },
                business_logs_collection=self.business_logs_collection,
            )

        return {
            "message": "Data Principal Added Successfully",
            "principal_ids": principal_ids,
        }

    async def get_data_principal(self, principal_id: str, user: Dict[str, Any]):
        user_email = user.get("email")
        df_id = user.get("df_id")

        table_name = "dpd"

        row = await self.data_principal_crud.get_by_dp_id(table_name, principal_id)
        if not row:
            await log_business_event(
                event_type="GET_DP_FAILED",
                user_email=user_email,
                message=f"Data Principal not found (principal_id={principal_id})",
                log_level="INFO",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Data Principal not found",
                    "action": "get",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Data Principal not found")

        if row["is_deleted"]:
            await log_business_event(
                event_type="GET_DP_FAILED",
                user_email=user_email,
                message=f"Data Principal is deleted (principal_id={principal_id})",
                log_level="INFO",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Data Principal is deleted",
                    "action": "get",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Data Principal is deleted")

        await log_business_event(
            event_type="GET_DP_SUCCESS",
            user_email=user_email,
            message=f"Data Principal fetched successfully for principal_id={principal_id}",
            log_level="INFO",
            context={
                "dp_id": principal_id,
                "df_id": df_id,
                "action": "get",
            },
            business_logs_collection=self.business_logs_collection,
        )

        raw_emails = row["dp_email"] or []
        raw_mobiles = row["dp_mobile"] or []

        masked_emails = [mask_email(e) for e in raw_emails]
        masked_mobiles = [mask_mobile(m) for m in raw_mobiles]

        return {
            "dp_id": str(row["dp_id"]),
            "dp_system_id": row["dp_system_id"],
            "dp_identifiers": row["dp_identifiers"],
            "dp_email": masked_emails,
            "dp_mobile": masked_mobiles,
            "dp_other_identifier": row["dp_other_identifier"] or [],
            "dp_preferred_lang": row["dp_preferred_lang"],
            "dp_country": row["dp_country"],
            "dp_state": row["dp_state"],
            "dp_active_devices": row["dp_active_devices"],
            "dp_tags": row["dp_tags"] or [],
            "is_active": row["is_active"],
            "is_legacy": row["is_legacy"],
            "added_by": str(row["added_by"]) if row["added_by"] else None,
            "added_with": row["added_with"],
            "created_at_df": row["created_at_df"],
            "last_activity": row["last_activity"],
            "consent_count": row["consent_count"],
            "consent_status": row["consent_status"],
        }

    async def delete_data_principal(self, principal_id: str, user: Dict[str, Any]):
        user_email = user.get("email")
        df_id = user.get("df_id")

        if not df_id:
            await log_business_event(
                event_type="DELETE_DP_FAILED",
                user_email=user_email,
                message=f"Unauthorized delete attempt for principal_id={principal_id}",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Unauthorized user (missing df_id)",
                    "action": "delete",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=401, detail="Unauthorized")

        table_name = "dpd"

        exists = await self.data_principal_crud.exists_not_deleted(table_name, principal_id)
        if not exists:
            await log_business_event(
                event_type="DELETE_DP_FAILED",
                user_email=user_email,
                message=f"Delete failed: Data Principal not found or already deleted (principal_id={principal_id})",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Not found or already deleted",
                    "action": "delete",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=404,
                detail="Data Principal not found or already deleted",
            )

        consent_status = await self.data_principal_crud.get_consent_status(table_name, principal_id)
        status_norm = (consent_status or "").strip().lower()

        if status_norm not in ("unsent", ""):
            await log_business_event(
                event_type="DELETE_DP_FAILED",
                user_email=user_email,
                message=f"Delete failed: Active or in-progress consent for principal_id={principal_id}",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": f"Consent status = {consent_status}",
                    "action": "delete",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(
                status_code=400,
                detail="Cannot delete active Data Principal: consent given or in progress",
            )

        await self.data_principal_crud.soft_delete(table_name, principal_id)
        await log_business_event(
            event_type="DELETE_DP_SUCCESS",
            user_email=user_email,
            message=f"Data Principal deleted successfully for principal_id={principal_id}",
            log_level="INFO",
            context={
                "dp_id": principal_id,
                "df_id": df_id,
                "action": "delete",
                "status": "soft_deleted",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Data Principal deleted successfully"}

    async def get_all_data_principals(
        self,
        page: int,
        limit: int,
        user: Dict[str, Any],
        dp_country: Optional[str] = None,
        dp_preferred_lang: Optional[str] = None,
        is_legacy: Optional[bool] = None,
        consent_status: Optional[str] = None,
        added_with: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        user_email = user.get("email")
        df_id = user.get("df_id")
        table_name = "dpd"

        filters, values = ["is_deleted = false"], []
        idx = 1

        if dp_country:
            filters.append(f"dp_country = ${idx}")
            values.append(dp_country)
            idx += 1
        if dp_preferred_lang:
            filters.append(f"dp_preferred_lang = ${idx}")
            values.append(dp_preferred_lang)
            idx += 1
        if is_legacy is not None:
            filters.append(f"is_legacy = ${idx}")
            values.append(is_legacy)
            idx += 1
        if consent_status:
            filters.append(f"consent_status = ${idx}")
            values.append(consent_status)
            idx += 1
        if added_with:
            filters.append(f"added_with = ${idx}")
            values.append(added_with)
            idx += 1
        if search:
            filters.append(
                f"""(
                EXISTS (SELECT 1 FROM unnest(dp_email) e WHERE e ILIKE ${idx})
                OR EXISTS (SELECT 1 FROM unnest(dp_mobile) m WHERE m ILIKE ${idx})
            )"""
            )
            values.append(f"%{search}%")
            idx += 1

        where_clause = " AND ".join(filters)

        total = await self.data_principal_crud.count(table_name, where_clause, values)
        rows = await self.data_principal_crud.fetch_all(table_name, where_clause, values, limit, (page - 1) * limit)

        principals = []
        for row in rows:
            principals.append(
                {
                    "dp_id": str(row["dp_id"]),
                    "dp_system_id": row["dp_system_id"],
                    "dp_identifiers": row["dp_identifiers"],
                    "dp_email": [mask_email(e) for e in (row["dp_email"] or [])],
                    "dp_mobile": [mask_mobile(m) for m in (row["dp_mobile"] or [])],
                    "dp_other_identifier": row["dp_other_identifier"] or [],
                    "dp_tags": row["dp_tags"] or [],
                    "dp_preferred_lang": row["dp_preferred_lang"],
                    "dp_country": row["dp_country"],
                    "dp_state": row["dp_state"],
                    "dp_active_devices": row["dp_active_devices"],
                    "is_active": row["is_active"],
                    "is_legacy": row["is_legacy"],
                    "added_by": row["added_by"],
                    "added_with": row["added_with"],
                    "created_at_df": row["created_at_df"],
                    "last_activity": row["last_activity"],
                    "consent_count": row["consent_count"],
                    "consent_status": row["consent_status"],
                    "df_id": row["df_id"],
                }
            )

        total_pages = (total + limit - 1) // limit
        options = await self.data_principal_crud.fetch_options(table_name)

        await log_business_event(
            event_type="GET_ALL_DP_SUCCESS",
            user_email=user_email,
            message="All Data Principals fetched successfully",
            log_level="INFO",
            context={
                "df_id": df_id,
                "page": page,
                "limit": limit,
                "total_principals": total,
                "action": "get_all",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "currentPage": page,
            "totalPages": total_pages,
            "totalPrincipals": total,
            "dataPrincipals": principals,
            "available_options": {
                "dp_country": options["dp_country"] or [],
                "dp_preferred_lang": options["dp_preferred_lang"] or [],
                "is_legacy": options["is_legacy"] or [],
                "consent_status": options["consent_status"] or [],
                "added_with": options["added_with"] or [],
                "dp_tags": options["dp_tags"] or [],
            },
        }

    async def update_data_principal(self, principal_id: str, update: UpdateDP, user: Dict[str, Any]):
        user_email = user.get("email")
        df_id = user.get("df_id")

        if not df_id:
            await log_business_event(
                event_type="UPDATE_DP_FAILED",
                user_email=user_email,
                message=f"Unauthorized update attempt for principal_id={principal_id}",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Unauthorized user (missing df_id)",
                    "action": "update",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=401, detail="Unauthorized")

        table_name = "dpd"

        result = await self.data_principal_crud.get_emails_mobiles_and_other_identifiers(table_name, principal_id)
        if not result:
            await log_business_event(
                event_type="UPDATE_DP_FAILED",
                user_email=user_email,
                message=f"Update failed: Data Principal not found (principal_id={principal_id})",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "Principal not found",
                    "action": "update",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Principal ID does not exist")

        existing_emails = result["dp_email"] or []
        existing_mobiles = result["dp_mobile"] or []
        existing_other_identifiers = result["dp_other_identifier"] or []

        update_element = update.model_dump(exclude={"dp_email", "dp_mobile", "dp_other_identifier"}, exclude_defaults=True)

        if not update_element and not update.dp_email and not update.dp_mobile and not update.dp_other_identifier:
            await log_business_event(
                event_type="UPDATE_DP_FAILED",
                user_email=user_email,
                message=f"No valid update fields found for principal_id={principal_id}",
                log_level="WARNING",
                context={
                    "dp_id": principal_id,
                    "df_id": df_id,
                    "reason": "No update content provided",
                    "action": "update",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="No update found")

        if update.dp_email:
            for email in update.dp_email:
                if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                    await log_business_event(
                        event_type="UPDATE_DP_FAILED",
                        user_email=user_email,
                        message=f"Invalid email format during update for principal_id={principal_id}",
                        log_level="ERROR",
                        context={
                            "dp_id": principal_id,
                            "df_id": df_id,
                            "invalid_email": email,
                            "reason": "Invalid email format",
                            "action": "update",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(status_code=400, detail="Invalid email address format")
            existing_emails = list(set(existing_emails + update.dp_email))

        if update.dp_mobile:
            validated_mobiles = []
            for mobile in update.dp_mobile:
                mobile_str = str(mobile)
                if mobile == 0 or not re.match(r"^\d{10}$", mobile_str):
                    await log_business_event(
                        event_type="UPDATE_DP_FAILED",
                        user_email=user_email,
                        message=f"Invalid mobile number format for principal_id={principal_id}",
                        log_level="ERROR",
                        context={
                            "dp_id": principal_id,
                            "df_id": df_id,
                            "invalid_mobile": mobile,
                            "reason": "Mobile number not 10 digits or zero",
                            "action": "update",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(
                        status_code=400,
                        detail="Mobile number must be exactly 10 digits and cannot be 0.",
                    )
                validated_mobiles.append(mobile_str)

            existing_mobiles = list(set([str(m) for m in existing_mobiles] + validated_mobiles))

        if update.dp_other_identifier:
            existing_other_identifiers = list(set(existing_other_identifiers + update.dp_other_identifier))
            update_element["dp_other_identifier"] = existing_other_identifiers

        set_clauses = []
        values = []
        idx = 1

        for field, value in update_element.items():
            set_clauses.append(f"{field} = ${idx}")
            values.append(value)
            idx += 1

        set_clauses.append(f"dp_email = ${idx}")
        values.append(existing_emails)
        idx += 1

        set_clauses.append(f"dp_mobile = ${idx}")
        values.append(existing_mobiles)
        idx += 1

        values.append(principal_id)

        await self.data_principal_crud.update_principal(table_name, principal_id, ", ".join(set_clauses), values)

        await log_business_event(
            event_type="UPDATE_DP_SUCCESS",
            user_email=user_email,
            message=f"Data Principal updated successfully for principal_id={principal_id}",
            log_level="INFO",
            context={
                "dp_id": principal_id,
                "df_id": df_id,
                "updated_fields": list(update_element.keys()),
                "emails": existing_emails,
                "mobiles": existing_mobiles,
                "action": "update",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Data Principal updated successfully", "principal_id": principal_id}

    async def get_all_dp_tags(self, user: Dict[str, Any]) -> Dict[str, Any]:
        user_email = user.get("email")
        df_id = user.get("df_id")

        table_name = "dpd"

        tags = await self.data_principal_crud.fetch_all_tags(table_name)

        await log_business_event(
            event_type="GET_ALL_DP_TAGS_SUCCESS",
            user_email=user_email,
            message="All Data Principal tags fetched successfully",
            log_level="INFO",
            context={
                "df_id": df_id,
                "action": "get_all_dp_tags",
                "tag_count": len(tags or []),
            },
            business_logs_collection=self.business_logs_collection,
        )

        return {"dp_tags": tags or []}

    async def get_dps_by_data_elements(self, de_titles: List[str], user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 1: Search Mongo consent_latest_artifacts for dp_ids
        Step 2: Fetch matching DPs from Postgres
        """
        user_email = user.get("email")
        df_id = user.get("df_id")

        table_name = "dpd"

        mongo_filter = {"artifact.consent_scope.data_elements.title": {"$in": de_titles}}

        dp_ids = await self.consent_latest_artifacts.distinct("artifact.data_principal.dp_id", mongo_filter)

        if not dp_ids:
            return []

        query = f"""
            SELECT 
                dp_id,
                dp_system_id,
                dp_email,
                dp_mobile,
                dp_tags,
                dp_identifiers,
                dp_country,
                dp_state,
                is_deleted,
                consent_status
            FROM {table_name}
            WHERE dp_id = ANY($1::uuid[])
              AND is_deleted = FALSE
        """

        async with self.data_principal_crud.pool.acquire() as conn:
            rows = await conn.fetch(query, dp_ids)

        result = []
        for row in rows:
            result.append(
                {
                    "dp_id": str(row["dp_id"]),
                    "dp_system_id": row["dp_system_id"],
                    "dp_identifiers": row["dp_identifiers"],
                    "dp_email": row["dp_email"] or [],
                    "dp_mobile": row["dp_mobile"] or [],
                    "dp_country": row["dp_country"],
                    "dp_state": row["dp_state"],
                    "dp_tags": row["dp_tags"] or [],
                    "consent_status": row["consent_status"],
                }
            )

        await log_business_event(
            event_type="GET_DPS_BY_DATA_ELEMENTS_SUCCESS",
            user_email=user_email,
            message="Data Principals fetched successfully by data elements",
            log_level="INFO",
            context={
                "df_id": df_id,
                "data_elements": de_titles,
                "principal_count": len(result),
                "action": "get_dps_by_data_elements",
            },
            business_logs_collection=self.business_logs_collection,
        )

        return result
