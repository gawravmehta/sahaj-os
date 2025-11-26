import uuid
import json
import asyncpg
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, BackgroundTasks
from pymongo.database import Database
from bson import ObjectId

from app.core.config import settings
from app.db.session import get_postgres_pool
from app.schemas.authentication import AuthRequestSchema
from app.core.logger import get_logger


logger = get_logger("service.auth_service")


async def find_user_in_postgres(
    pool: asyncpg.Pool,
    dp_id=None,
    dp_e=None,
    dp_m=None,
):
    """
    Find user by dp_id OR ANY email match OR ANY mobile match.
    Works whether dp_e/dp_m are strings or lists.
    Matches ANY element in Postgres array fields dp_e / dp_m.
    """

    def normalize_array(value):
        """
        Convert:
        - None → None
        - string → [string]
        - list → list (as-is)
        Removes empty/blank entries.
        """
        if value is None:
            return None
        if isinstance(value, list):
            cleaned = [str(v).strip() for v in value if str(v).strip()]
            return cleaned or None
        value = str(value).strip()
        return [value] if value else None

    def normalize_single(value):
        if isinstance(value, list):
            value = value[0] if value else None
        if value is None:
            return None
        value = str(value).strip()
        return value or None

    dp_id = normalize_single(dp_id)
    dp_e_list = normalize_array(dp_e)
    dp_m_list = normalize_array(dp_m)

    try:
        async with pool.acquire() as conn:
            query = """
                SELECT dp_id
                FROM dpd
                WHERE
                    ($1::text IS NOT NULL AND dp_id::text = $1::text)
                    OR ($2::text[] IS NOT NULL AND dp_e && $2::text[])
                    OR ($3::text[] IS NOT NULL AND dp_m && $3::text[])
                LIMIT 1
            """
            record = await conn.fetchrow(query, dp_id, dp_e_list, dp_m_list)
            return record["dp_id"] if record else None

    except Exception as e:
        logger.error(f"Postgres Query Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Postgres error: {str(e)}")


async def write_dp_details_in_postgres(dp_data: dict, df_id: str, pool: asyncpg.Pool):
    """
    Inserts/updates the DP details in Postgres into the dpd table.
    Pool is passed as parameter to avoid connection pool exhaustion in background tasks.
    """

    try:
        user_details = await find_user_in_postgres(
            pool,
            dp_id=dp_data["dp_id"],
            dp_e=dp_data["dp_e"],
            dp_m=dp_data["dp_m"],
        )

        now_ts = datetime.now().replace(tzinfo=None)

        async with pool.acquire() as conn:
            if user_details:
                logger.info("Record exists in Postgres, performing update", extra={"dp_id": user_details})
                logger.info(
                    f"Update params: dp_e={dp_data['dp_e']} (type: {type(dp_data['dp_e'])}), dp_m={dp_data['dp_m']} (type: {type(dp_data['dp_m'])}), last_activity={now_ts}, user_details={user_details} (type: {type(user_details)})"
                )

                update_query = """
                    UPDATE dpd
                    SET dp_e = (
                            SELECT array(SELECT DISTINCT unnest(dp_e || $1::text[]))
                        ),
                        dp_m = (
                            SELECT array(SELECT DISTINCT unnest(dp_m || $2::text[]))
                        ),
                        last_activity = $3
                    WHERE dp_id = $4
                """
                try:
                    await conn.execute(update_query, dp_data["dp_e"], dp_data["dp_m"], now_ts, user_details, timeout=5)
                except Exception as e:
                    logger.error(f"Error updating Postgres record: {e}", exc_info=True)
                    raise
                return

            logger.info("Inserting new record in Postgres", extra={"dp_id": dp_data["dp_id"]})

            dp_identifiers = []
            if dp_data["dp_email"]:
                dp_identifiers.append("email")
            if dp_data["dp_mobile"]:
                dp_identifiers.append("mobile")

            insert_query = """
                INSERT INTO dpd (dp_id, dp_e, dp_m, dp_email, dp_mobile, dp_identifiers,dp_preferred_lang, last_activity,is_legacy, is_active, is_deleted)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """
            await conn.execute(
                insert_query,
                dp_data["dp_id"],
                dp_data["dp_e"],
                dp_data["dp_m"],
                dp_data["dp_email"],
                dp_data["dp_mobile"],
                dp_identifiers,
                "eng",
                now_ts,
                False,
                True,
                False,
            )

    except Exception as e:
        logger.error(f"Error writing in Postgres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error writing in Postgres: {str(e)}")


class AuthenticationService:
    def __init__(
        self,
        db: Database,
        redis_client,
        tracer=None,
        pool: asyncpg.Pool = None,
    ):
        self.db = db
        self.redis = redis_client
        self.tracer = tracer
        self.pool = pool

    async def _get_collection_point(self, cp_id: str) -> dict:
        """Fetches collection point from cache or database."""
        redis_key = f"cp:{cp_id}"
        cached_cp = await self.redis.get(redis_key)
        if cached_cp:
            return json.loads(cached_cp)

        try:
            db_cp = await self.db.cp_master.find_one({"_id": ObjectId(cp_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Collection Point ID format.")

        if not db_cp:
            raise HTTPException(status_code=404, detail="Unknown Collection Point.")

        await self.redis.set(redis_key, json.dumps(db_cp, default=str))
        return db_cp

    def _create_jwt_token(self, payload: dict) -> str:
        """Encodes a JWT token."""
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    async def authenticate_user_and_get_token(
        self,
        *,
        auth_params: AuthRequestSchema,
        df_id: str,
        client_ip: str,
        background_tasks: BackgroundTasks,
    ) -> str:
        """Main service method to orchestrate the authentication flow."""

        cp = await self._get_collection_point(auth_params.cp_id)

        if not any([auth_params.dp_id, auth_params.dp_e, auth_params.dp_m]):
            raise HTTPException(status_code=400, detail="Data Principal identifier is mandatory.")

        existing_dp_id = await find_user_in_postgres(
            self.pool,
            dp_id=auth_params.dp_id,
            dp_e=auth_params.dp_e,
            dp_m=auth_params.dp_m,
        )

        dp_id = str(existing_dp_id) if existing_dp_id else (auth_params.dp_id or str(uuid.uuid4()))

        dp_data = {
            "dp_id": dp_id,
            "dp_e": [auth_params.dp_e] if auth_params.dp_e else [],
            "dp_m": [auth_params.dp_m] if auth_params.dp_m else [],
            "dp_email": [auth_params.dp_email] if auth_params.dp_email else [],
            "dp_mobile": [auth_params.dp_mobile] if auth_params.dp_mobile else [],
            "timestamp": datetime.now().isoformat(),
        }
        background_tasks.add_task(
            write_dp_details_in_postgres,
            dp_data,
            df_id,
            self.pool,
        )

        issued_at = datetime.now()
        expiry_time = issued_at + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        request_id = str(uuid.uuid4())

        payload = {
            "dp_id": dp_id,
            "cp_id": auth_params.cp_id,
            "language": auth_params.pref_lang or cp.get("default_language") or "eng",
            "exp": expiry_time.timestamp(),
            "iat": issued_at.timestamp(),
            "binded_ip": client_ip,
            "df_id": df_id,
            "request_id": request_id,
        }
        token = self._create_jwt_token(payload)

        redis_session_key = f"session:{df_id}:{dp_id}:{request_id}"
        await self.redis.setex(
            redis_session_key,
            int(timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS).total_seconds()),
            token,
        )

        return token
