from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from app.crud.consent_validation_crud import ConsentValidationCRUD
from app.crud.vendor_crud import VendorCRUD

import csv
from io import StringIO
import io
import json
import os
import time
from fastapi import HTTPException

from fastapi.responses import JSONResponse, StreamingResponse

from app.db.rabbitmq import publish_message
from app.schemas.consent_validation_schema import VerificationRequest
from app.utils.common import count_rows_in_file, hash_shake256
from datetime import UTC, datetime, timezone
import uuid

from pymongo import DESCENDING, ASCENDING
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import Regex

from app.core.config import settings
from app.utils.business_logger import log_business_event


class ConsentValidationService:
    def __init__(
        self,
        consent_validation_crud: ConsentValidationCRUD,
        consent_artifact_crud: ConsentArtifactCRUD,
        vendor_crud: VendorCRUD,
        business_logs_collection: str,
        customer_notifications_collection: AsyncIOMotorCollection,
    ):
        self.consent_validation_crud = consent_validation_crud
        self.consent_artifact_crud = consent_artifact_crud
        self.vendor_crud = vendor_crud
        self.business_logs_collection = business_logs_collection
        self.customer_notifications_collection = customer_notifications_collection

    async def verify_consent_internal(
        self,
        payload: VerificationRequest,
        current_user,
    ):
        dp_id = payload.dp_id
        dp_system_id = payload.dp_system_id
        dp_e = hash_shake256(payload.dp_e)
        dp_m = hash_shake256(payload.dp_m)
        data_elements_hash = payload.data_elements_hash
        purpose_hash = payload.purpose_hash

        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "data_elements_hash": data_elements_hash,
                    "purpose_hash": purpose_hash,
                    "error": "User Not Found (df_id missing)",
                },
                message="Consent verification failed: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        if not dp_id and not dp_system_id and not (dp_e or dp_m):
            await log_business_event(
                event_type="VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "data_elements_hash": data_elements_hash,
                    "purpose_hash": purpose_hash,
                    "error": "Data Principal ID or System ID or Email/Mobile is required",
                },
                message="Consent verification failed: Missing Data Principal identification.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="Data Principal ID or Data Principal System ID is required",
            )

        if not purpose_hash:
            await log_business_event(
                event_type="VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "data_elements_hash": data_elements_hash,
                    "purpose_hash": purpose_hash,
                    "error": "Purpose hash is required",
                },
                message="Consent verification failed: Purpose hash is missing.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="Either purpose_hash is required",
            )

        if not data_elements_hash:
            await log_business_event(
                event_type="VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "data_elements_hash": data_elements_hash,
                    "purpose_hash": purpose_hash,
                    "error": "Data element hash is required",
                },
                message="Consent verification failed: Data element hash is missing.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="At least one data element hash is required",
            )

        query = {}
        if dp_id:
            query["artifact.data_principal.dp_id"] = dp_id
        elif dp_system_id:
            query["artifact.data_principal.dp_df_id"] = dp_system_id
        elif dp_e:
            query["artifact.data_principal.dp_e"] = dp_e
        elif dp_m:
            query["artifact.data_principal.dp_m"] = dp_m

        consent_artifacts = await self.consent_artifact_crud.get_filtered_consent_artifacts(query, DESCENDING, 0, 1000).to_list(length=100)

        if not consent_artifacts:
            await log_business_event(
                event_type="VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "data_elements_hash": data_elements_hash,
                    "purpose_hash": purpose_hash,
                    "error": "Consent Artifact(s) Not Found",
                    "query": query,
                },
                message="Consent verification failed: No matching Consent Artifacts found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Consent Artifact(s) Not Found")

        current_time = datetime.now(timezone.utc)
        matched_elements = set()

        for artifact_doc in consent_artifacts:
            artifact = artifact_doc.get("artifact", {})
            data_elements = artifact.get("consent_scope", {}).get("data_elements", [])

            for element in data_elements:
                element_hash = element.get("de_hash_id")
                if element_hash not in data_elements_hash:
                    continue

                for consent in element.get("consents", []):
                    if consent.get("purpose_hash_id") != purpose_hash:
                        continue
                    if consent.get("consent_status") != "approved":
                        continue

                    expiry_str = consent.get("consent_expiry_period")
                    if not expiry_str:
                        continue

                    try:
                        expiry_date = datetime.fromisoformat(expiry_str)
                        if expiry_date.tzinfo is None:
                            expiry_date = expiry_date.replace(tzinfo=timezone.utc)

                        if expiry_date > current_time:
                            matched_elements.add(element_hash)
                            break
                    except (TypeError, ValueError):

                        pass

        all_verified = all(elem in matched_elements for elem in data_elements_hash)

        artifact_for_log = consent_artifacts[0].get("artifact", {})

        verification_log = {
            "request_id": uuid.uuid4().hex,
            "df_id": df_id,
            "dp_id": dp_id or artifact_for_log.get("data_principal", {}).get("dp_id"),
            "dp_system_id": dp_system_id or artifact_for_log.get("data_principal", {}).get("dp_df_id"),
            "dp_e": dp_e or artifact_for_log.get("data_principal", {}).get("dp_e"),
            "dp_m": dp_m or artifact_for_log.get("data_principal", {}).get("dp_m"),
            "internal_external": "Internal",
            "ver_requested_by": str(current_user.get("_id")),
            "consent_status": all_verified,
            "scope": {
                "data_element_hashes": data_elements_hash,
                "purpose_hash": purpose_hash,
            },
            "status": "successful",
            "timestamp": current_time,
        }

        verification_req = await self.consent_validation_crud.insert_verification_log(verification_log)

        await log_business_event(
            event_type="VERIFY_CONSENT_SUCCESS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "dp_id": dp_id,
                "dp_system_id": dp_system_id,
                "data_elements_hash": data_elements_hash,
                "purpose_hash": purpose_hash,
                "verified_status": all_verified,
                "verification_request_id": str(verification_req.inserted_id),
            },
            message=f"Consent verification completed. Status: {'Verified' if all_verified else 'Denied'}.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        if not all_verified:
            # Create notification for DP
            dp_id_for_notif = dp_id or artifact_for_log.get("data_principal", {}).get("dp_id")
            if dp_id_for_notif:
                now = datetime.now(UTC)
                notification = {
                    "dp_id": dp_id_for_notif,
                    "type": "CONSENT_VALIDATION_FAILED",
                    "title": "Consent Validation Failed",
                    "message": f"A Data Fiduciary attempted to validate your consent for purpose {purpose_hash}, but it was found to be invalid or expired.",
                    "status": "unread",
                    "created_at": now,
                    "verification_request_id": str(verification_req.inserted_id),
                    "df_id": df_id,
                }
                await self.customer_notifications_collection.insert_one(notification)

        return {
            "verified": all_verified,
            "consented_data_elements": list(matched_elements),
            "verification_request_id": str(verification_req.inserted_id),
        }

    async def get_all_verification_logs(
        self,
        page,
        limit,
        sort_order,
        search,
        internal_external,
        status,
        from_date,
        to_date,
        purpose_hashes,
        data_element_hashes,
        current_user,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="LIST_VERIFICATION_LOGS_FAILED",
                user_email=current_user.get("email"),
                context={"error": "User Not Found (df_id missing)"},
                message="Failed to list verification logs: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        skip = (page - 1) * limit
        sort_dir = DESCENDING if sort_order == "desc" else ASCENDING

        query = {}

        if search:
            regex = {"$regex": Regex(search, "i")}
            hashed_search = hash_shake256(search)

            query["$or"] = [
                {"dp_id": regex},
                {"dp_system_id": regex},
                {"dp_e": hashed_search},
                {"dp_m": hashed_search},
            ]

        if internal_external:
            query["internal_external"] = internal_external

        if status:
            query["status"] = status

        if from_date or to_date:
            query["timestamp"] = {}
            if from_date:
                query["timestamp"]["$gte"] = from_date
            if to_date:
                query["timestamp"]["$lte"] = to_date

        or_filters = []
        if purpose_hashes:
            or_filters.append({"scope.purpose_hash": {"$in": purpose_hashes}})
        if data_element_hashes:
            or_filters.append({"scope.data_element_hashes": {"$in": data_element_hashes}})
        if or_filters:

            if "$and" in query:
                query["$and"].append({"$or": or_filters})
            else:
                query["$and"] = [{"$or": or_filters}]

        cursor = self.consent_validation_crud.find_logs(query, sort_dir, skip, limit)
        logs_list = await cursor.to_list(length=limit)
        for doc in logs_list:
            doc["_id"] = str(doc["_id"])

        total_count = await self.consent_validation_crud.count_logs(query)
        total_pages = (total_count + limit - 1) // limit

        min_date_cursor = self.consent_validation_crud.find_logs({"df_id": df_id}, ASCENDING, 0, 1)
        min_date_list = await min_date_cursor.to_list(length=1)
        min_date_doc = min_date_list[0] if min_date_list else None

        max_date_cursor = self.consent_validation_crud.find_logs({"df_id": df_id}, DESCENDING, 0, 1)
        max_date_list = await max_date_cursor.to_list(length=1)
        max_date_doc = max_date_list[0] if max_date_list else None

        filter_options = {
            "internal_external": await self.consent_validation_crud.find_distinct_logs("internal_external", {"df_id": df_id}),
            "status": await self.consent_validation_crud.find_distinct_logs("status", {"df_id": df_id}),
            "purpose_titles": await self.consent_validation_crud.find_distinct_logs("scope.purpose_title", {"df_id": df_id}),
            "data_element_titles": await self.consent_validation_crud.find_distinct_logs("scope.data_element_titles", {"df_id": df_id}),
            "min_date": min_date_doc["timestamp"] if min_date_doc else None,
            "max_date": max_date_doc["timestamp"] if max_date_doc else None,
        }

        await log_business_event(
            event_type="LIST_VERIFICATION_LOGS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "current_page": page,
                "data_per_page": limit,
                "search": search,
                "internal_external": internal_external,
                "status": status,
                "from_date": from_date,
                "to_date": to_date,
                "purpose_hashes": purpose_hashes,
                "data_element_hashes": data_element_hashes,
            },
            message=f"User listed verification logs. Page: {page}, Items per page: {limit}.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "logs_data": logs_list,
            "filter_options": filter_options,
        }

    async def download_verification_logs(
        self,
        sort_order,
        search,
        internal_external,
        status,
        from_date,
        to_date,
        purpose_hashes,
        data_element_hashes,
        current_user,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="DOWNLOAD_VERIFICATION_LOGS_FAILED",
                user_email=current_user.get("email"),
                context={"error": "User Not Found (df_id missing)"},
                message="Failed to download verification logs: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        sort_dir = DESCENDING if sort_order == "desc" else ASCENDING

        query = {}

        if search:
            regex = {"$regex": Regex(search, "i")}
            hashed_search = hash_shake256(search)

            query["$or"] = [
                {"dp_id": regex},
                {"dp_system_id": regex},
                {"dp_e": hashed_search},
                {"dp_m": hashed_search},
            ]

        if internal_external:
            query["internal_external"] = internal_external

        if status:
            query["status"] = status

        if from_date or to_date:
            query["timestamp"] = {}
            if from_date:
                try:
                    query["timestamp"]["$gte"] = datetime.fromisoformat(from_date)
                except ValueError:
                    await log_business_event(
                        event_type="DOWNLOAD_VERIFICATION_LOGS_FAILED",
                        user_email=current_user.get("email"),
                        context={"error": f"Invalid from_date format: {from_date}"},
                        message="Failed to download verification logs: Invalid 'from_date' format.",
                        business_logs_collection=self.business_logs_collection,
                        log_level="ERROR",
                    )
                    raise HTTPException(status_code=400, detail="Invalid from_date format")
            if to_date:
                try:
                    query["timestamp"]["$lte"] = datetime.fromisoformat(to_date)
                except ValueError:
                    await log_business_event(
                        event_type="DOWNLOAD_VERIFICATION_LOGS_FAILED",
                        user_email=current_user.get("email"),
                        context={"error": f"Invalid to_date format: {to_date}"},
                        message="Failed to download verification logs: Invalid 'to_date' format.",
                        business_logs_collection=self.business_logs_collection,
                        log_level="ERROR",
                    )
                    raise HTTPException(status_code=400, detail="Invalid to_date format")

        or_filters = []

        if purpose_hashes:
            or_filters.append({"scope.purpose_hash": {"$in": purpose_hashes}})

        if data_element_hashes:
            or_filters.append({"scope.data_element_hashes": {"$in": data_element_hashes}})

        if or_filters:
            if "$and" in query:
                query["$and"].append({"$or": or_filters})
            else:
                query["$and"] = [{"$or": or_filters}]

        logs_cursor = self.consent_validation_crud.find_logs(query, sort_dir, 0, 10000)

        logs_list = await logs_cursor.to_list(length=None)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "Request ID",
                "DP ID",
                "DP System ID",
                "Internal/External",
                "Request By",
                "Status",
                "Purpose Hash",
                "Data Element Hashes",
                "Consent Status",
                "Timestamp",
            ]
        )

        for doc in logs_list:
            ver_requested_by = doc.get("ver_requested_by", {})

            data_elements = doc.get("scope", {}).get("data_element_hashes", [])
            data_element_str = ", ".join(data_elements) if isinstance(data_elements, list) else str(data_elements)

            consent_status = doc.get("consent_status", False)
            consent_status_str = "Granted" if consent_status else "Denied"

            timestamp_obj = doc.get("timestamp")
            timestamp_str = timestamp_obj.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp_obj, datetime) else str(timestamp_obj or "")

            writer.writerow(
                [
                    doc.get("request_id", ""),
                    doc.get("dp_id", ""),
                    doc.get("dp_system_id", ""),
                    doc.get("internal_external", ""),
                    ver_requested_by,
                    doc.get("status", ""),
                    doc.get("scope", {}).get("purpose_hash", ""),
                    data_element_str,
                    consent_status_str,
                    timestamp_str,
                ]
            )

        output.seek(0)

        await log_business_event(
            event_type="DOWNLOAD_VERIFICATION_LOGS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "search": search,
                "internal_external": internal_external,
                "status": status,
                "from_date": from_date,
                "to_date": to_date,
                "purpose_hashes": purpose_hashes,
                "data_element_hashes": data_element_hashes,
                "num_records": len(logs_list),
            },
            message=f"User downloaded {len(logs_list)} verification logs to CSV.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=verification_logs.csv"},
        )

    async def bulk_verify_consent_internal(
        self,
        file,
        current_user,
        s3_client,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="BULK_VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={"error": "User Not Found (df_id missing)"},
                message="Bulk consent verification failed: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        genie_user_id = str(current_user.get("_id"))
        if not genie_user_id:
            await log_business_event(
                event_type="BULK_VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "error": "Genie user id is missing"},
                message="Bulk consent verification failed: Genie user ID is missing.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=401, detail="Genie user id is missing")

        contents = await file.read()
        file_type = file.filename.rsplit(".", 1)[-1].lower()
        if file_type not in ("csv",):
            await log_business_event(
                event_type="BULK_VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "file_type": file_type, "error": "Unsupported file type"},
                message=f"Bulk consent verification failed: Unsupported file type '{file_type}'.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(415, "Unsupported file type")

        filename = f"{df_id}_{genie_user_id}_verification_{int(time.time())}.{file_type}"
        local_path = f"app/uploads/{filename}"
        with open(local_path, "wb") as buf:
            buf.write(contents)

        try:
            s3_client.fput_object(
                settings.UNPROCESSED_VERIFICATION_FILES_BUCKET,
                filename,
                local_path,
                file.content_type,
            )
            os.remove(local_path)

            await self.consent_validation_crud.insert_validation_file_details(
                {
                    "filename": filename,
                    "df_id": df_id,
                    "genie_user_id": genie_user_id,
                    "status": "pending",
                    "created_at": datetime.now(UTC),
                }
            )
            await log_business_event(
                event_type="BULK_VERIFY_FILE_UPLOADED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "filename": filename, "status": "pending"},
                message=f"Bulk verification file '{filename}' uploaded to S3 successfully.",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )

        except Exception as e:
            await log_business_event(
                event_type="BULK_VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "filename": file.filename, "error": str(e)},
                message=f"Bulk consent verification failed: Failed to upload file to S3: {e}",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(500, f"Failed to upload file to S3: {e}")

        try:
            message = json.dumps(
                {
                    "filename": filename,
                    "df_id": df_id,
                    "genie_user_id": genie_user_id,
                    "file_type": file_type,
                }
            )
            await publish_message("consent_bulk_verification", message)
            await log_business_event(
                event_type="BULK_VERIFY_MESSAGE_PUBLISHED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "filename": filename, "queue": "consent_bulk_verification"},
                message=f"Bulk verification message for '{filename}' published to RabbitMQ.",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )
        except Exception as e:
            await log_business_event(
                event_type="BULK_VERIFY_CONSENT_FAILED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "filename": file.filename, "error": str(e)},
                message=f"Bulk consent verification failed: Failed to publish message to queue: {e}",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(500, f"Failed to publish message to queue: {e}")

        row_count = count_rows_in_file(contents, file_type) - 1

        return JSONResponse(
            {
                "status": "processing_started",
                "message": "Consent verification started in background.",
                "files_received": file.filename,
                "row_count": row_count,
            }
        )

    async def get_all_uploaded_verification_files(
        self,
        current_user,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="LIST_UPLOADED_FILES_FAILED",
                user_email=current_user.get("email"),
                context={"error": "User Not Found (df_id missing)"},
                message="Failed to list uploaded verification files: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        files_cursor = await self.consent_validation_crud.get_all_uploaded_files({"df_id": df_id}, DESCENDING, 0, 10000)

        for file in files_cursor:
            file["_id"] = str(file["_id"])
            file["created_at"] = str(file.get("created_at", ""))
            file["started_at"] = str(file.get("started_at", ""))
            file["completed_at"] = str(file.get("completed_at", ""))

        await log_business_event(
            event_type="LIST_UPLOADED_FILES",
            user_email=current_user.get("email"),
            context={"df_id": df_id, "num_files": len(files_cursor)},
            message=f"User listed {len(files_cursor)} uploaded verification files.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return JSONResponse(content=files_cursor)

    async def download_verified_file(
        self,
        file_name: str,
        current_user,
        download_type,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="DOWNLOAD_VERIFIED_FILE_FAILED",
                user_email=current_user.get("email"),
                context={"file_name": file_name, "error": "User Not Found (df_id missing)"},
                message="Failed to download verified file: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        logs_cursor = await self.consent_validation_crud.find_logs(
            {
                "bulk_file_name": file_name,
                "df_id": df_id,
            },
            DESCENDING,
            0,
            10000,
        ).to_list(length=None)

        if not logs_cursor:
            await log_business_event(
                event_type="DOWNLOAD_VERIFIED_FILE_FAILED",
                user_email=current_user.get("email"),
                context={"file_name": file_name, "df_id": df_id, "error": "No records found"},
                message=f"Failed to download verified file '{file_name}': No records found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="No records found for this file")

        formatted_logs = []
        for log in logs_cursor:
            formatted_logs.append(
                {
                    "request_id": log.get("request_id"),
                    "dp_id": log.get("dp_id"),
                    "dp_system_id": log.get("dp_system_id", ""),
                    "dp_e": log.get("dp_e"),
                    "dp_m": log.get("dp_m"),
                    "internal_external": log.get("internal_external", ""),
                    "ver_requested_by": log.get("ver_requested_by", ""),
                    "consent_status": log.get("consent_status", False),
                    "data_elements": ", ".join(log.get("scope", {}).get("data_element_hashes", [])),
                    "purpose_title": log.get("scope", {}).get("purpose_hash", ""),
                    "status": log.get("status", ""),
                    "timestamp": (log.get("timestamp").isoformat() if log.get("timestamp") else ""),
                }
            )

        if download_type == "csv":
            csv_buffer = StringIO()
            fieldnames = list(formatted_logs[0].keys())
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()
            for row in formatted_logs:
                writer.writerow(row)
            csv_buffer.seek(0)

            await log_business_event(
                event_type="DOWNLOAD_VERIFIED_FILE_CSV",
                user_email=current_user.get("email"),
                context={"file_name": file_name, "df_id": df_id, "download_type": "csv", "num_records": len(formatted_logs)},
                message=f"User downloaded verified file '{file_name}' as CSV.",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )

            return StreamingResponse(
                csv_buffer,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={file_name or 'verified_logs'}.csv"},
            )

        await log_business_event(
            event_type="DOWNLOAD_VERIFIED_FILE_JSON",
            user_email=current_user.get("email"),
            context={"file_name": file_name, "df_id": df_id, "download_type": "json", "num_records": len(formatted_logs)},
            message=f"User downloaded verified file '{file_name}' as JSON.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )
        return JSONResponse(
            content=formatted_logs,
            headers={"Content-Disposition": f"attachment; filename={file_name or 'verified_logs'}.json"},
        )

    async def get_one_verification_log(self, request_id, current_user):
        df_id = current_user.get("df_id")
        if not df_id:
            await log_business_event(
                event_type="GET_ONE_VERIFICATION_LOG_FAILED",
                user_email=current_user.get("email"),
                context={"request_id": request_id, "error": "User Not Found (df_id missing)"},
                message="Failed to get single verification log: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        verification_log = await self.consent_validation_crud.find_one_log({"request_id": request_id, "df_id": df_id})
        if not verification_log:
            await log_business_event(
                event_type="GET_ONE_VERIFICATION_LOG_FAILED",
                user_email=current_user.get("email"),
                context={"request_id": request_id, "df_id": df_id, "error": "Not Found"},
                message=f"Failed to get single verification log: Log with request ID '{request_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Not Found")

        verification_log["_id"] = str(verification_log["_id"])
        await log_business_event(
            event_type="GET_ONE_VERIFICATION_LOG",
            user_email=current_user.get("email"),
            context={"request_id": request_id, "df_id": df_id},
            message=f"User fetched single verification log with request ID '{request_id}'.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )
        return verification_log

    async def get_verification_dashboard_stats(
        self,
        current_user,
    ):
        """Get dashboard stats for consent verification"""
        df_id = current_user["df_id"]

        if not df_id:
            await log_business_event(
                event_type="GET_DASHBOARD_STATS_FAILED",
                user_email=current_user.get("email"),
                context={"error": "User Not Found (df_id missing)"},
                message="Failed to get verification dashboard stats: User Data Fiduciary ID not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="User Not Found")

        total_requests = await self.consent_validation_crud.count_total_logs({"df_id": df_id})

        successful_verifications = await self.consent_validation_crud.count_total_logs({"df_id": df_id, "consent_status": True})

        failed_verifications = await self.consent_validation_crud.count_total_logs({"df_id": df_id, "consent_status": False})

        successful_verification_status = await self.consent_validation_crud.count_total_logs({"df_id": df_id, "status": "successful"})

        failed_verification_status = await self.consent_validation_crud.count_total_logs({"df_id": df_id, "status": "unsuccessful"})

        notification_count = await self.consent_validation_crud.count_total_logs({"df_id": df_id, "status": "successful", "consent_status": False})

        stats = {
            "data_processors": await self.vendor_crud.count_vendors({"df_id": df_id}),
            "total_requests": total_requests,
            "valid_results": successful_verifications,
            "invalid_results": failed_verifications,
            "notification_count": notification_count,
            "success_rate_percentage": (round(successful_verification_status / total_requests * 100, 2) if total_requests > 0 else 0),
            "failure_rate_percentage": (round(failed_verification_status / total_requests * 100, 2) if total_requests > 0 else 0),
        }

        await log_business_event(
            event_type="GET_DASHBOARD_STATS",
            user_email=current_user.get("email"),
            context={"df_id": df_id, "stats": stats},
            message="User fetched verification dashboard statistics.",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return stats
