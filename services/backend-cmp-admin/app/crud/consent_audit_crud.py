from motor.motor_asyncio import AsyncIOMotorCollection


class ConsentAuditCRUD:
    def __init__(self, consent_audit_collection: AsyncIOMotorCollection):
        self.collection = consent_audit_collection

    def get_logs(self, dp_id: str, df_id: str = None):
        query = {"dp_id": dp_id}
        if df_id:
            query["df_id"] = df_id

        return self.collection.find(query).sort("timestamp", 1)
