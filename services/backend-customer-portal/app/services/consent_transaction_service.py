from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.utils.common import clean_mongo_doc
from app.core.logger import app_logger


class ConsentTransactionService:
    def __init__(
        self,
        consent_artifact_collection: AsyncIOMotorCollection,
        dpar_collection: Optional[AsyncIOMotorCollection] = None,
        grievance_collection: Optional[AsyncIOMotorCollection] = None,
    ):
        self.collection = consent_artifact_collection
        self.dpar_collection = dpar_collection
        self.grievance_collection = grievance_collection

    def _parse_iso(self, dt_str: Optional[str]) -> datetime:
        """
        Parse ISO 8601 string to a timezone-aware datetime in UTC.
        Falls back to epoch UTC if missing/invalid.
        """
        if not dt_str:
            return datetime.fromtimestamp(0, tz=timezone.utc)
        try:
            if dt_str.endswith("Z"):
                dt_str = dt_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except Exception as e:
            app_logger.warning(f"Error parsing ISO datetime string '{dt_str}': {e}. Falling back to epoch.")
            return datetime.fromtimestamp(0, tz=timezone.utc)

    async def get_all_consent_transactions(self, dp_id: str):
        app_logger.info(f"Fetching all consent transactions for dp_id: {dp_id}")
        if not dp_id:
            app_logger.warning("get_all_consent_transactions failed: dp_id is required")
            raise HTTPException(status_code=400, detail="dp_id is required")

        query = {
            "artifact.data_principal.dp_id": dp_id,
        }
        cursor = self.collection.find(query)
        all_artifacts = [doc async for doc in cursor]

        if not all_artifacts:
            app_logger.info(f"No consent transactions found for dp_id: {dp_id}")
            raise HTTPException(status_code=404, detail="No consent transactions found")
        app_logger.info(f"Retrieved {len(all_artifacts)} consent artifacts for dp_id: {dp_id}")

        artifacts_by_hash: dict[str, dict] = {}
        referenced_hashes: set[str] = set()

        for doc in all_artifacts:
            doc["_id"] = str(doc["_id"])
            agreement_hash = doc.get("agreement_hash_id") or ""
            linked_hash = (doc.get("artifact", {}) or {}).get("linked_agreement_hash") or ""

            if agreement_hash:
                artifacts_by_hash[agreement_hash] = doc
            if linked_hash:
                referenced_hashes.add(linked_hash)

        terminal_artifacts = [doc for ah, doc in artifacts_by_hash.items() if ah and ah not in referenced_hashes]

        if not terminal_artifacts:
            terminal_artifacts = all_artifacts

        latest_by_cp: dict[str, dict] = {}
        for doc in terminal_artifacts:
            cp_name = (doc.get("artifact", {}) or {}).get("cp_name") or "_unknown_cp"
            agreement_date = self._parse_iso((doc.get("artifact", {}) or {}).get("data_fiduciary", {}).get("agreement_date"))

            current_best = latest_by_cp.get(cp_name)
            if current_best is None or agreement_date > current_best["dt"]:
                latest_by_cp[cp_name] = {"doc": doc, "dt": agreement_date}

        latest_artifacts = [v["doc"] for v in latest_by_cp.values()]
        latest_artifacts.sort(key=lambda d: (d.get("artifact", {}).get("cp_name") or "").lower())

        return {
            "message": "Latest consent transactions retrieved successfully per collection point",
            "data": latest_artifacts,
        }

    async def get_consent_transaction(self, agreement_id: str):
        visited = set()
        chain = []

        async def fetch_by_agreement_id(aid: str):
            return await self.collection.find_one({"artifact.agreement_id": aid})

        async def fetch_by_hash(hash_id: str):
            return await self.collection.find_one({"agreement_hash_id": hash_id})

        async def traverse_forward(current_doc):
            nonlocal chain
            while current_doc and current_doc["artifact"]["agreement_id"] not in visited:
                visited.add(current_doc["artifact"]["agreement_id"])
                chain.append(current_doc)
                linked_hash = current_doc["artifact"].get("linked_agreement_hash")
                if not linked_hash:
                    break
                current_doc = await fetch_by_hash(linked_hash)

        app_logger.info(f"Fetching consent transaction chain for agreement_id: {agreement_id}")
        base_doc = await fetch_by_agreement_id(agreement_id)
        if not base_doc:
            app_logger.warning(f"Consent agreement not found for ID: {agreement_id}")
            raise HTTPException(status_code=404, detail="Agreement ID not found")
        app_logger.debug(f"Found base artifact for agreement_id: {agreement_id}")

        await traverse_forward(base_doc)

        return {"agreement_chain": clean_mongo_doc(chain)}

    async def extract_highest_version_data_elements(self, dp_id: str):
        """
        Extract data elements and processors for each CP (highest agreement version per CP)
        under the given dp_id.
        """
        try:

            app_logger.info(f"Extracting highest version data elements for dp_id: {dp_id}")
            artifacts = await self.collection.find({"artifact.data_principal.dp_id": dp_id}).to_list(None)

            if not artifacts:
                app_logger.info(f"No artifacts found for dp_id: {dp_id}")
                raise HTTPException(status_code=404, detail="No artifacts found for this dp_id")
            app_logger.debug(f"Found {len(artifacts)} artifacts for dp_id: {dp_id}")

            cp_groups = {}
            for doc in artifacts:
                artifact = doc.get("artifact", {})
                cp_name = artifact.get("cp_name")
                version = artifact.get("agreement_version", 0)

                if not cp_name:
                    continue

                if cp_name not in cp_groups or version > cp_groups[cp_name]["artifact"].get("agreement_version", 0):
                    cp_groups[cp_name] = doc

            unique_elements = {}

            for cp_name, doc in cp_groups.items():
                artifact = doc.get("artifact", {})
                consent_scope = artifact.get("consent_scope", {})
                data_elements = consent_scope.get("data_elements", [])

                for de in data_elements:
                    de_id = de.get("de_id")
                    if not de_id:
                        continue

                    de_title = de.get("title")

                    if de_id not in unique_elements:
                        unique_elements[de_id] = {"data_element_id": de_id, "data_element_title": de_title, "cp_names": set(), "data_processors": {}}

                    unique_elements[de_id]["cp_names"].add(cp_name)

                    for consent in de.get("consents", []):
                        for dp in consent.get("data_processors", []):
                            dp_id = dp.get("data_processor_id")
                            if dp_id:
                                unique_elements[de_id]["data_processors"][dp_id] = {
                                    "data_processor_id": dp_id,
                                    "data_processor_name": dp.get("data_processor_name", ""),
                                }

            result = []
            for de_id, info in unique_elements.items():
                result.append(
                    {
                        "data_element_id": info["data_element_id"],
                        "data_element_title": info["data_element_title"],
                        "cp_names": list(info["cp_names"]),
                        "data_processors": list(info["data_processors"].values()),
                    }
                )

            return {"dp_id": dp_id, "total_cp": len(cp_groups), "total_data_elements": len(result), "data_elements": result}

        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"Error extracting highest version data elements for dp_id: {dp_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    async def get_dashboard_counts(self, dp_id: str):
        app_logger.info(f"Fetching dashboard counts for dp_id: {dp_id}")
        try:

            consent_count = await self.collection.count_documents({"dp_id": dp_id})

            cp_count = len(await self.collection.distinct("cp_id", {"dp_id": dp_id}))

            dpar_count = await self.dpar_collection.count_documents({"requested_by": dp_id})

            grievance_count = await self.grievance_collection.count_documents({"dp_id": dp_id})

            return {
                "consent_count": consent_count,
                "cp_count": cp_count,
                "dpar_count": dpar_count,
                "grievance_count": grievance_count,
            }

        except Exception as e:
            app_logger.error(f"Failed to fetch dashboard counts for dp_id: {dp_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch dashboard counts")
