import json
from app.db.session import get_postgres_pool
from app.core.logger import get_logger


logger = get_logger("service.postgres_service")


async def get_token_information(token: str, dpar_token: str, redis_client):
    """Fetch token details from Postgres and cache in Redis, including notification_id."""

    pool = await get_postgres_pool()

    query = """
        SELECT token, df_id, dp_id, cp_id
        FROM ln_tokens
        WHERE token = $1
    """

    query_notification = """
        SELECT notification_id
        FROM consent_notifications
        WHERE token = $1
    """

    async with pool.acquire() as conn:
        token_row = await conn.fetchrow(query, token)
        notification_row = await conn.fetchrow(query_notification, token)

    if token_row:
        token_data = dict(token_row)
        token_data["dpar_token"] = dpar_token
        token_data["notification_id"] = str(notification_row["notification_id"]) if notification_row else None

        await redis_client.setex(f"token:{token}", 3600, json.dumps(token_data))
        return token_data

    else:
        return {}


async def delete_token_information(token: str, df_id: str, dp_id: str, redis_client):
    """
    Delete the token row from Postgres and remove it from Redis cache.
    Also increments consent_count for the Data Principal if present.
    """

    pool = await get_postgres_pool()

    async with pool.acquire() as conn:
        if df_id and dp_id:
            try:
                update_query = """
                    UPDATE dpd
                    SET consent_count = consent_count + 1
                    WHERE dp_id = $1
                """
                await conn.execute(update_query, dp_id)
            except Exception as e:
                logger.error(f"Error updating consent_count for dp_id {dp_id}: {e}", exc_info=True)

        try:
            delete_query = "DELETE FROM ln_tokens WHERE token = $1"
            await conn.execute(delete_query, token)
        except Exception as e:
            logger.error(f"Error deleting token {token} from Postgres: {e}", exc_info=True)

    await redis_client.delete(f"token:{token}")
