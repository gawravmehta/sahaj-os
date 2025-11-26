import json
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends, Request
from pymongo.database import Database
from contextlib import contextmanager

from app.db.session import get_mongo_master_db, get_redis, get_tracer
from app.core.logger import get_logger


logger = get_logger("api.deps")


@contextmanager
def open_span(name):
    """A dummy context manager for when no tracer is found."""
    yield None


async def get_validated_df(
    request: Request,
    x_df_id: Optional[str] = Header(None, description="DF ID"),
    x_df_key: Optional[str] = Header(None, description="DF Key"),
    x_df_secret: Optional[str] = Header(None, description="DF Secret"),
    db: Database = Depends(get_mongo_master_db),
    redis_client=Depends(get_redis),
    tracer=Depends(get_tracer),
) -> Dict[str, Any]:
    """
    FastAPI dependency to authenticate a Data Fiduciary (DF) using headers.
    It checks cache first, then falls back to the database.
    """
    if not all([x_df_id, x_df_key, x_df_secret]):
        raise HTTPException(
            status_code=401,
            detail="Missing required authentication headers: x-df-id, x-df-key, x-df-secret",
        )

    span_name = "dependency:get_validated_df"
    with tracer.start_as_current_span(span_name) if tracer else open_span(span_name) as span:
        redis_key = f"{x_df_id}_detail"

        redis_data = await redis_client.get(redis_key)
        matching_df = json.loads(redis_data) if redis_data else None

        if not matching_df:
            logger.info(f"DF {x_df_id} not in cache, checking MongoDB...", extra={"df_id": x_df_id})
            matching_df = await db.df_keys.find_one({"df_id": x_df_id})
            if matching_df:
                logger.info(f"DF {x_df_id} found in MongoDB, caching now.", extra={"df_id": x_df_id})
                await redis_client.set(redis_key, json.dumps(matching_df, default=str))

        if not matching_df:
            logger.warning(f"DF {x_df_id} not found.", extra={"df_id": x_df_id})
            raise HTTPException(status_code=401, detail="Unknown Data Fiduciary.")

        if x_df_key != matching_df.get("df_key") or x_df_secret != matching_df.get("df_secret"):
            logger.warning(f"Invalid credentials for DF {x_df_id}.", extra={"df_id": x_df_id})
            raise HTTPException(status_code=401, detail="Invalid Data Fiduciary credentials.")

        if span:
            span.set_attribute("df.id", x_df_id)

        logger.info(f"Successfully validated DF {x_df_id}.", extra={"df_id": x_df_id})
        return matching_df
