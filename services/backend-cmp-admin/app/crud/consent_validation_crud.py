from motor.motor_asyncio import AsyncIOMotorCollection


class ConsentValidationCRUD:
    def __init__(self, consent_validation_collection: AsyncIOMotorCollection, consent_validation_files_collection: AsyncIOMotorCollection):
        self.consent_validation_collection = consent_validation_collection
        self.consent_validation_files_collection = consent_validation_files_collection

    async def insert_verification_log(self, log_data):
        return await self.consent_validation_collection.insert_one(log_data)

    def find_logs(self, query, sort_dir, skip, limit):
        return self.consent_validation_collection.find(query).sort("timestamp", sort_dir).skip(skip).limit(limit)

    async def count_total_logs(self, query):
        return await self.consent_validation_collection.count_documents(query)

    async def find_one_log(self, query):
        return await self.consent_validation_collection.find_one(query)

    async def count_logs(self, query):
        return await self.consent_validation_collection.count_documents(query)

    async def find_distinct_logs(self, field, query):
        return await self.consent_validation_collection.distinct(field, query)

    async def insert_validation_file_details(self, file_data):
        return await self.consent_validation_files_collection.insert_one(file_data)

    async def get_all_uploaded_files(self, query, sort_dir, skip, limit):
        cursor = self.consent_validation_files_collection.find(query).sort("created_at", sort_dir).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
