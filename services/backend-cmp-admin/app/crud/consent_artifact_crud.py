from motor.motor_asyncio import AsyncIOMotorCollection


class ConsentArtifactCRUD:
    def __init__(
        self,
        consent_artifact_collection: AsyncIOMotorCollection,
    ):
        self.consent_artifact_collection = consent_artifact_collection

    def get_filtered_consent_artifacts(self, query, sort_dir, skip, limit):
        return self.consent_artifact_collection.find(query).sort("artifact.data_fiduciary.agreement_date", sort_dir).skip(skip).limit(limit)

    async def count_filtered_consent_artifacts(self, query):
        return await self.consent_artifact_collection.count_documents(query)

    async def get_one_consent_artifacts(self, query):
        return await self.consent_artifact_collection.find_one(query)

    def get_expiring_consent_artifacts(self, query):
        return self.consent_artifact_collection.find(query)

    async def count_collected_data_elements(self, query):
        """
        Count unique data elements that have been collected across all consent artifacts.
        Extracts unique de_id values from artifact.consent_scope.data_elements.
        """
        unique_de_ids = set()
        async for doc in self.consent_artifact_collection.find(query):
            if "artifact" in doc and "consent_scope" in doc["artifact"] and "data_elements" in doc["artifact"]["consent_scope"]:
                for de in doc["artifact"]["consent_scope"]["data_elements"]:
                    if "de_id" in de:
                        unique_de_ids.add(de["de_id"])
        return len(unique_de_ids)

    async def count_collected_purposes(self, query):
        """
        Count unique purposes that have been collected across all consent artifacts.
        Extracts unique purpose_id values from artifact.consent_scope.data_elements.consents.
        """
        unique_purpose_ids = set()
        async for doc in self.consent_artifact_collection.find(query):
            if "artifact" in doc and "consent_scope" in doc["artifact"] and "data_elements" in doc["artifact"]["consent_scope"]:
                for de in doc["artifact"]["consent_scope"]["data_elements"]:
                    if "consents" in de:
                        for consent in de["consents"]:
                            if "purpose_id" in consent:
                                unique_purpose_ids.add(consent["purpose_id"])
        return len(unique_purpose_ids)

    async def count_collected_collection_points(self, query):
        """
        Count unique collection points that have been used across all consent artifacts.
        Extracts unique cp_id values from the root level of consent artifacts.
        """
        unique_cp_ids = await self.consent_artifact_collection.distinct("cp_id", query)
        return len(unique_cp_ids)
