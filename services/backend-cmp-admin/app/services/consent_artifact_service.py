from io import StringIO
from datetime import datetime, timedelta

from bson import ObjectId
from fastapi.responses import StreamingResponse
from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from fastapi import HTTPException

from app.utils.common import hash_shake256
from pymongo import ASCENDING, DESCENDING
from app.schemas.consent_artifact_schema import PurposeConsentExpiry, ExpiringConsentsByDpIdResponse
from typing import Optional
from app.utils.business_logger import log_business_event


class ConsentArtifactService:
    def __init__(
        self,
        crud: ConsentArtifactCRUD,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection

    async def get_all_consent_artifact(
        self,
        page,
        limit,
        search,
        cp_names_query,
        purposes_query,
        data_elements_query,
        sort_order,
        start_date,
        end_date,
        current_user,
    ):
        df_id = current_user.get("df_id")

        if not df_id:
            raise HTTPException(status_code=404, detail="User Not Found")

        skip = (page - 1) * limit
        query = {}

        if search:
            hashed = hash_shake256(search)
            query["$or"] = [
                {"artifact.data_principal.dp_e": hashed},
                {"artifact.data_principal.dp_m": hashed},
            ]

        if cp_names_query:
            query["artifact.cp_name"] = {"$in": cp_names_query}

        if purposes_query:
            query["artifact.consent_scope.data_elements.consents"] = {"$elemMatch": {"description": {"$in": purposes_query}}}

        if data_elements_query:
            query["artifact.consent_scope.data_elements"] = {"$elemMatch": {"title": {"$in": data_elements_query}}}

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["artifact.data_fiduciary.agreement_date"] = date_filter

        sort_dir = DESCENDING if sort_order == "desc" else ASCENDING

        cursor = self.crud.get_filtered_consent_artifacts(query, sort_dir, skip, limit)

        results = await cursor.to_list(length=limit)

        consent_list = []
        for doc in results:
            doc["_id"] = str(doc["_id"])
            consent_list.append(doc)

        total_count = await self.crud.count_filtered_consent_artifacts(query)
        total_pages = (total_count + limit - 1) // limit

        cp_names = list({doc["artifact"].get("cp_name") for doc in consent_list if doc.get("artifact", {}).get("cp_name")})

        purpose_titles = list(
            {
                purpose.get("purpose_title")
                for doc in consent_list
                for data_element in doc.get("artifact", {}).get("consent_scope", {}).get("data_elements", [])
                for purpose in data_element.get("consents", [])
                if purpose.get("purpose_title")
            }
        )

        data_elements = list(
            {
                data_element.get("title")
                for doc in consent_list
                for data_element in doc.get("artifact", {}).get("consent_scope", {}).get("data_elements", [])
                if data_element.get("title")
            }
        )

        min_cursor = self.crud.get_filtered_consent_artifacts(query, ASCENDING, 0, 1)
        max_cursor = self.crud.get_filtered_consent_artifacts(query, DESCENDING, 0, 1)

        min_doc_list = await min_cursor.to_list(length=1)
        max_doc_list = await max_cursor.to_list(length=1)

        min_doc = min_doc_list[0] if min_doc_list else None
        max_doc = max_doc_list[0] if max_doc_list else None

        min_date_val = min_doc["artifact"]["data_fiduciary"]["agreement_date"] if min_doc else None
        max_date_val = max_doc["artifact"]["data_fiduciary"]["agreement_date"] if max_doc else None

        await log_business_event(
            event_type="LIST_CONSENT_ARTIFACTS",
            user_email=current_user.get("email"),
            context={
                "current_page": page,
                "data_per_page": limit,
                "df_id": df_id,
                "search": search,
                "cp_names_query": cp_names_query,
                "purposes_query": purposes_query,
                "data_elements_query": data_elements_query,
                "sort_order": sort_order,
                "start_date": start_date,
                "end_date": end_date,
            },
            message=f"User listed Consent Artifacts. Page: {page}, Items per page: {limit}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "consent_data": consent_list,
            "filter_options": {
                "cp_names": cp_names,
                "purpose_titles": purpose_titles,
                "data_elements": data_elements,
                "min_date": min_date_val,
                "max_date": max_date_val,
            },
        }

    async def download_consent_artifact(
        self,
        search,
        cp_names_query,
        purposes_query,
        data_elements_query,
        sort_order,
        start_date,
        end_date,
        current_user,
    ):
        df_id = current_user.get("df_id")
        if not df_id:
            raise HTTPException(status_code=404, detail="User Not Found")

        query = {}

        if search:
            hashed = hash_shake256(search)
            query["$or"] = [
                {"artifact.data_principal.dp_e": hashed},
                {"artifact.data_principal.dp_m": hashed},
            ]

        if cp_names_query:
            query["artifact.cp_name"] = {"$in": cp_names_query}

        if purposes_query:
            query["artifact.consent_scope.data_elements.consents"] = {"$elemMatch": {"purpose_title": {"$in": purposes_query}}}

        if data_elements_query:
            query["artifact.consent_scope.data_elements.title"] = {"$in": data_elements_query}

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["artifact.data_fiduciary.agreement_date"] = date_filter

        sort_dir = ASCENDING if sort_order == "asc" else DESCENDING

        cursor = self.crud.get_filtered_consent_artifacts(query, sort_dir, 0, 0)
        results = await cursor.to_list(length=None)

        output = StringIO()
        writer = output.write
        writer("Agreement ID,Agreement Timestamp,Collection Point,Data Elements,DP ID,DP Email,DP Mobile,Purposes\n")

        for doc in results:
            artifact = doc.get("artifact", {})
            dp = artifact.get("data_principal", {})
            df = artifact.get("data_fiduciary", {})

            agreement_id = artifact.get("agreement_id", "")
            agreement_date = df.get("agreement_date", "")
            cp_name = artifact.get("cp_name", "")
            dp_id = dp.get("dp_id", "") if dp else ""
            dp_email = dp.get("dp_e", "") if dp else ""
            dp_mobile = dp.get("dp_m", "") if dp else ""

            data_elements = artifact.get("consent_scope", {}).get("data_elements", [])
            element_titles = [de.get("title", "") for de in data_elements]
            purpose_titles = [consent.get("purpose_title", "") for de in data_elements for consent in de.get("consents", [])]

            writer(
                f"{agreement_id},"
                f"{agreement_date},"
                f"{cp_name},"
                f"{'|'.join(element_titles)},"
                f"{dp_id},"
                f"{dp_email},"
                f"{dp_mobile},"
                f"{'|'.join(purpose_titles)}\n"
            )

        output.seek(0)

        await log_business_event(
            event_type="DOWNLOAD_CONSENT_ARTIFACTS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "search": search,
                "cp_names_query": cp_names_query,
                "purposes_query": purposes_query,
                "data_elements_query": data_elements_query,
                "sort_order": sort_order,
                "start_date": start_date,
                "end_date": end_date,
            },
            message=f"User downloaded Consent Artifacts to CSV.",
            business_logs_collection=self.business_logs_collection,
        )

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=consent_artifacts.csv"},
        )

    async def get_consent_artifact_by_id(self, consent_artifact_id: str, current_user: dict):
        df_id = current_user.get("df_id")
        if not df_id:
            raise HTTPException(status_code=404, detail="User Not Found")

        consent_artifact = await self.crud.get_one_consent_artifacts({"_id": ObjectId(consent_artifact_id), "df_id": df_id})

        if not consent_artifact:
            await log_business_event(
                event_type="GET_CONSENT_ARTIFACT_NOT_FOUND",
                user_email=current_user.get("email"),
                context={
                    "consent_artifact_id": consent_artifact_id,
                    "df_id": df_id,
                },
                message=f"Consent Artifact with ID '{consent_artifact_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Consent Artifact Not Found")

        consent_artifact["_id"] = str(consent_artifact["_id"])

        await log_business_event(
            event_type="GET_CONSENT_ARTIFACT",
            user_email=current_user.get("email"),
            context={
                "consent_artifact_id": consent_artifact_id,
                "df_id": df_id,
            },
            message=f"User fetched Consent Artifact with ID '{consent_artifact_id}'.",
            business_logs_collection=self.business_logs_collection,
        )
        return consent_artifact

    async def get_expiring_consents(self, df_id: str, dp_id: Optional[str] = None, days_to_expire: Optional[str] = None):
        current_time = datetime.now()
        seven_days_from_now = current_time + timedelta(days=7)
        fifteen_days_from_now = current_time + timedelta(days=15)
        thirty_days_from_now = current_time + timedelta(days=30)

        query = {
            "df_id": df_id,
            "artifact.consent_scope.data_elements.consents.consent_expiry_period": {
                "$gt": current_time.isoformat(),
            },
        }
        if dp_id:
            query["dp_id"] = dp_id

        if days_to_expire == "7":
            query["artifact.consent_scope.data_elements.consents.consent_expiry_period"]["$lte"] = seven_days_from_now.isoformat()
        elif days_to_expire == "15":
            query["artifact.consent_scope.data_elements.consents.consent_expiry_period"]["$lte"] = fifteen_days_from_now.isoformat()
        elif days_to_expire == "30":
            query["artifact.consent_scope.data_elements.consents.consent_expiry_period"]["$lte"] = thirty_days_from_now.isoformat()
        else:
            query["artifact.consent_scope.data_elements.consents.consent_expiry_period"]["$lte"] = thirty_days_from_now.isoformat()

        expiring_consents_cursor = self.crud.get_expiring_consent_artifacts(query)
        expiring_consents_list = await expiring_consents_cursor.to_list(length=None)

        seven_days_expiring = {}
        fifteen_days_expiring = {}
        thirty_days_expiring = {}

        for artifact_doc in expiring_consents_list:
            dp_id_from_doc = artifact_doc.get("dp_id")
            df_id_from_doc = artifact_doc.get("df_id")

            if not dp_id_from_doc:
                continue

            for data_element in artifact_doc.get("artifact", {}).get("consent_scope", {}).get("data_elements", []):
                for consent in data_element.get("consents", []):
                    consent_expiry_str = consent.get("consent_expiry_period")
                    if not consent_expiry_str:
                        continue

                    try:
                        consent_expiry_dt = datetime.fromisoformat(consent_expiry_str.replace("Z", "+00:00"))
                    except ValueError:
                        continue

                    purpose_consent_expiry = PurposeConsentExpiry(
                        purpose_id=consent.get("purpose_id"),
                        purpose_title=consent.get("purpose_title"),
                        consent_expiry_period=consent_expiry_dt,
                        dp_id=dp_id_from_doc,
                        df_id=df_id_from_doc,
                    )

                    if current_time < consent_expiry_dt <= seven_days_from_now:
                        if dp_id_from_doc not in seven_days_expiring:
                            seven_days_expiring[dp_id_from_doc] = ExpiringConsentsByDpIdResponse(dp_id=dp_id_from_doc, expiring_purposes=[])
                        seven_days_expiring[dp_id_from_doc].expiring_purposes.append(purpose_consent_expiry)

                    if current_time < consent_expiry_dt <= fifteen_days_from_now:
                        if dp_id_from_doc not in fifteen_days_expiring:
                            fifteen_days_expiring[dp_id_from_doc] = ExpiringConsentsByDpIdResponse(dp_id=dp_id_from_doc, expiring_purposes=[])
                        fifteen_days_expiring[dp_id_from_doc].expiring_purposes.append(purpose_consent_expiry)

                    if current_time < consent_expiry_dt <= thirty_days_from_now:
                        if dp_id_from_doc not in thirty_days_expiring:
                            thirty_days_expiring[dp_id_from_doc] = ExpiringConsentsByDpIdResponse(dp_id=dp_id_from_doc, expiring_purposes=[])
                        thirty_days_expiring[dp_id_from_doc].expiring_purposes.append(purpose_consent_expiry)

        if days_to_expire == "7":
            return list(seven_days_expiring.values())
        elif days_to_expire == "15":
            return list(fifteen_days_expiring.values())
        else:
            expiring_consents_result = list(thirty_days_expiring.values())

        await log_business_event(
            event_type="LIST_EXPIRING_CONSENTS",
            user_email=df_id,
            context={
                "df_id": df_id,
                "dp_id": dp_id,
                "days_to_expire": days_to_expire,
                "num_expiring_consents": len(expiring_consents_list),
            },
            message=f"User queried expiring consents for Data Fiduciary '{df_id}'. Days to expire: {days_to_expire or '30'}.",
            business_logs_collection=self.business_logs_collection,
        )

        return expiring_consents_result
