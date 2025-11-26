from bson import ObjectId


class InviteCRUD:
    def __init__(self, collection):
        self.collection = collection

    async def get_pending_invite(self, email: str):
        return await self.collection.find_one(
            {
                "invited_user_email": email,
                "invite_status": "pending",
                "is_deleted": False,
            }
        )

    async def get_invite_by_token(self, token: str):
        return await self.collection.find_one({"invite_token": token, "is_deleted": False})

    async def get_invite_by_id(self, invite_id: str):
        return await self.collection.find_one({"_id": ObjectId(invite_id), "is_deleted": False})

    async def create_invite(self, invite_dict: dict):
        return await self.collection.insert_one(invite_dict)

    async def update_invite_data(self, invite_id: str, update_data: dict):
        return await self.collection.update_one(
            {"_id": ObjectId(invite_id)},
            {"$set": update_data},
        )

    async def get_invites(self, df_id: str, page: int = 1, page_size: int = 10):
        cursor = self.collection.find({"invited_df": df_id, "is_deleted": False})
        return await cursor.skip((page - 1) * page_size).limit(page_size).to_list(length=None)

    async def soft_delete_invite(self, invite_id: str):
        return await self.collection.update_one(
            {"_id": ObjectId(invite_id)},
            {"$set": {"is_deleted": True}},
        )
