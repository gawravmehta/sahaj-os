from motor.motor_asyncio import AsyncIOMotorCollection
import asyncpg


class NoticeNotificationCRUD:
    def __init__(self, collection: AsyncIOMotorCollection, pool: asyncpg.Pool):
        self.collection = collection
        self.pool = pool

    async def insert_notice_notification(self, document: dict):
        return await self.collection.insert_one(document)

    async def get_total_notice_notifications_count(self, df_id: str) -> int:
        query = f"""
        SELECT COUNT(*)
        FROM consent_notifications
        WHERE df_id = $1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, df_id)

    async def get_notice_notifications(self, df_id: str, limit: int, skip: int):
        query = f"""
        SELECT *
        FROM consent_notifications
        WHERE df_id = $1
        ORDER BY RANDOM()
        LIMIT $2 OFFSET $3
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, df_id, limit, skip)
            return [dict(row) for row in rows]

    async def mark_notification_as_read(self, event_id: str):
        query = """
            UPDATE consent_notifications
            SET is_notification_read = TRUE
            WHERE notification_id = $1 AND is_notification_read = FALSE
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(query, event_id)

    async def mark_notification_as_clicked(self, event_id: str):
        query = """
            UPDATE consent_notifications
            SET is_notification_clicked = TRUE
            WHERE notification_id = $1 AND is_notification_clicked = FALSE
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(query, event_id)
