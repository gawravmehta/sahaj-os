import asyncpg
from typing import List, Dict, Any


class DataPrincipalCRUD:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def ensure_table(self, table_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    dp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    dp_system_id TEXT NOT NULL,
                    dp_identifiers TEXT[],
                    dp_email TEXT[],
                    dp_mobile TEXT[],
                    dp_other_identifier TEXT[],
                    dp_preferred_lang TEXT,
                    dp_country TEXT,
                    dp_state TEXT,
                    dp_active_devices TEXT[],
                    dp_tags TEXT[],
                    is_active BOOLEAN DEFAULT TRUE,
                    is_legacy BOOLEAN DEFAULT FALSE,
                    added_by TEXT,
                    added_with TEXT,
                    created_at_df TIMESTAMPTZ DEFAULT NOW(),
                    last_activity TIMESTAMPTZ,
                    dp_e TEXT[],
                    dp_m TEXT[],
                    is_deleted BOOLEAN DEFAULT FALSE,
                    consent_count INTEGER DEFAULT 0,
                    consent_status TEXT,
                    inserted_at TIMESTAMPTZ DEFAULT NOW(),
                    legacy_notification_ids TEXT[],
                    consent_artifacts TEXT[],
                    dpar_req TEXT[]
                )
            """
            )

    async def get_by_system_id(self, table_name: str, system_id: str):
        async with self.pool.acquire() as conn:
            query = f"""
                SELECT dp_email, dp_mobile, is_deleted
                FROM {table_name}
                WHERE dp_system_id = $1
            """
            return await conn.fetchrow(query, system_id)

    async def get_by_dp_id(self, table_name: str, dp_id: str):
        query = f"""
        SELECT 
            dp_id,
            dp_system_id,
            dp_identifiers,
            dp_email,
            dp_mobile,
            dp_other_identifier,
            dp_preferred_lang,
            dp_country,
            dp_state,
            dp_active_devices,
            dp_tags,
            is_active,
            is_legacy,
            added_by,
            added_with,
            created_at_df,
            last_activity,
            consent_count,
            consent_status,
            is_deleted
        FROM {table_name}
        WHERE dp_id = $1
        LIMIT 1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, dp_id)

    async def insert_or_update_deleted(self, table_name: str, system_id: str, emails, mobiles):
        async with self.pool.acquire() as conn:
            query = f"""
                INSERT INTO {table_name} (
                    dp_id, dp_system_id, dp_email, dp_mobile, is_deleted
                ) VALUES (
                    gen_random_uuid(), $1, $2, $3, FALSE
                )
                ON CONFLICT (dp_system_id) 
                DO UPDATE SET dp_email = $2, dp_mobile = $3, is_deleted = FALSE
            """
            await conn.execute(query, system_id, emails, mobiles)

    async def insert(self, table_name: str, data: dict):
        async with self.pool.acquire() as conn:
            query = f"""
                INSERT INTO {table_name} (
                    dp_id, dp_system_id, dp_identifiers, dp_email, dp_mobile, dp_other_identifier,
                    dp_preferred_lang, dp_country, dp_state, dp_active_devices, dp_tags,
                    is_active, is_legacy, added_by, added_with, created_at_df, last_activity,
                    dp_e, dp_m, is_deleted, consent_count, consent_status
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
                    $11,$12,$13,$14,$15,$16,$17,$18,$19,$20, $21,$22
                )
            """
            await conn.execute(
                query,
                data["dp_id"],
                data["dp_system_id"],
                data["dp_identifiers"],
                data["dp_email"],
                data["dp_mobile"],
                data["dp_other_identifier"],
                data["dp_preferred_lang"],
                data["dp_country"],
                data["dp_state"],
                data["dp_active_devices"],
                data["dp_tags"],
                data["is_active"],
                data["is_legacy"],
                data["added_by"],
                data["added_with"],
                data["created_at_df"],
                data["last_activity"],
                data["dp_e"],
                data["dp_m"],
                data["is_deleted"],
                data["consent_count"],
                data["consent_status"],
            )

    async def exists_not_deleted(self, table_name: str, principal_id: str) -> bool:
        query = f"""
            SELECT COUNT(*) 
            FROM {table_name}
            WHERE dp_id = $1 AND is_deleted = false
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, principal_id)

    async def get_consent_status(self, table_name: str, principal_id: str) -> str:
        query = f"""
            SELECT consent_status
            FROM {table_name}
            WHERE dp_id = $1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, principal_id)

    async def soft_delete(self, table_name: str, principal_id: str):
        query = f"""
            UPDATE {table_name}
            SET is_deleted = true
            WHERE dp_id = $1
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, principal_id)

    async def count(self, table_name: str, where_clause: str, values: List[Any]) -> int:
        query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *values)

    async def fetch_all(self, table_name: str, where_clause: str, values: List[Any], limit: int, offset: int) -> List[Dict]:
        query = f"""
            SELECT 
                dp_id,
                dp_system_id,
                dp_identifiers,
                dp_email,
                dp_mobile,
                dp_other_identifier,
                dp_preferred_lang,
                dp_country,
                dp_state,
                dp_active_devices,
                dp_tags,
                is_active,
                is_legacy,
                added_by,
                added_with,
                created_at_df,
                last_activity,
                consent_count,
                consent_status
            FROM {table_name}
            WHERE {where_clause}
            ORDER BY created_at_df DESC
            LIMIT ${len(values)+1} OFFSET ${len(values)+2}
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *values, limit, offset)

    async def fetch_options(self, table_name: str) -> Dict:
        query = f"""
            SELECT 
                array_agg(DISTINCT dp_country) FILTER (WHERE dp_country IS NOT NULL) AS dp_country,
                array_agg(DISTINCT dp_preferred_lang) FILTER (WHERE dp_preferred_lang IS NOT NULL) AS dp_preferred_lang,
                array_agg(DISTINCT is_legacy) AS is_legacy,
                array_agg(DISTINCT is_legacy) AS is_legacy,
                (
                    SELECT array_agg(DISTINCT tag)
                    FROM {table_name}, unnest(dp_tags) AS tag
                    WHERE dp_tags IS NOT NULL
                ) AS dp_tags,
                array_agg(DISTINCT consent_status) FILTER (WHERE consent_status IS NOT NULL) AS consent_status,
                array_agg(DISTINCT added_with) FILTER (WHERE added_with IS NOT NULL) AS added_with
            FROM {table_name}
            WHERE is_deleted = false
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query)

    async def get_emails_mobiles_and_other_identifiers(self, table_name: str, principal_id: str):
        query = f"""
            SELECT dp_email, dp_mobile, dp_other_identifier
            FROM {table_name}
            WHERE dp_id = $1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, principal_id)

    async def update_principal(self, table_name: str, principal_id: str, set_clauses: str, values: list):
        query = f"""
            UPDATE {table_name}
            SET {set_clauses}
            WHERE dp_id = ${len(values)}
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)

    async def fetch_all_tags(self, table_name: str) -> List[str]:
        query = f"""
            SELECT DISTINCT unnest(dp_tags) AS tag
            FROM {table_name}
            WHERE is_deleted = FALSE AND dp_tags IS NOT NULL
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [row["tag"] for row in rows if row["tag"]]
