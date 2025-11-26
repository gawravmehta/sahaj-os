import csv
import io
import json
import asyncpg
from fastapi import APIRouter, Body, Depends, HTTPException, Header, Query, Request
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
from fastapi.responses import StreamingResponse
from jose import jwt
from pydantic import BaseModel, ValidationError, field_validator, model_validator

from app.db.dependencies import get_batch_collection, get_df_keys_collection
from app.db.rabbitmq import publish_message
from app.db.session import get_postgres_pool

router = APIRouter()

SECRET_KEY = "dp_process"
TOKEN_EXPIRY_TIME = timedelta(hours=24)


class BulkDpApiModel(BaseModel):
    dp_system_id: str
    dp_identifiers: List[str]
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[int]] = []
    dp_other_identifier: Optional[List[str]] = []
    dp_preferred_lang: Optional[str] = "eng"
    dp_country: Optional[str] = ""
    dp_state: Optional[str] = ""
    dp_active_devices: Optional[List[str]] = []
    dp_tags: Optional[List[str]] = []
    is_active: Optional[bool] = False
    is_legacy: bool
    created_at_df: datetime
    last_activity: Optional[datetime]

    @field_validator("dp_preferred_lang", "dp_country", "dp_state", "dp_tags", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("dp_email", "dp_active_devices", mode="before")
    def lowercase_list_fields(cls, v):
        if isinstance(v, list):
            return [item.lower() for item in v if isinstance(item, str)]
        return v


async def generate_jwt_token(df_id: str, batch_collection) -> str:
    """Generate a JWT token for the given df_id and save it in MongoDB."""
    expiration = datetime.now(UTC) + TOKEN_EXPIRY_TIME
    payload = {
        "df_id": df_id,
        "exp": expiration,
        "status": "start",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    await batch_collection.update_one(
        {"df_id": df_id},
        {"$set": {"token": token, "status": "start", "expiry": expiration}},
        upsert=True,
    )

    return token


class UpdateBulkDPModel(BaseModel):

    dp_id: Optional[str] = None
    dp_system_id: Optional[str] = None
    dp_identifiers: Optional[List[str]] = []
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[str]] = []
    dp_other_identifier: Optional[List[str]] = []
    dp_preferred_lang: Optional[str] = "eng"
    dp_country: Optional[str] = ""
    dp_state: Optional[str] = ""
    dp_active_devices: Optional[List[str]] = []
    dp_tags: Optional[List[str]] = []
    is_active: Optional[bool] = False
    is_legacy: Optional[bool] = True
    created_at_df: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    @field_validator("dp_preferred_lang", "dp_country", "dp_state", "dp_tags", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("dp_email", "dp_active_devices", mode="before")
    def lowercase_list_fields(cls, v):
        if isinstance(v, list):
            return [item.lower() for item in v if isinstance(item, str)]
        return v

    @field_validator("dp_identifiers", mode="before")
    def validate_identifiers(cls, v):
        if not isinstance(v, list):
            raise ValueError("dp_identifiers must be a list")
        allowed = {"email", "mobile"}
        invalid = [x for x in v if x not in allowed]
        if invalid:
            raise ValueError(f"dp_identifiers may only include {', '.join(allowed)}; got {invalid}")
        return v

    @model_validator(mode="after")
    def _require_ident_values(cls, model: "UpdateBulkDPModel") -> "UpdateBulkDPModel":

        if "email" in model.dp_identifiers and not (model.dp_email and len(model.dp_email)):
            raise ValueError("dp_email is required when 'email' is in dp_identifiers")
        if "mobile" in model.dp_identifiers and not (model.dp_mobile and len(model.dp_mobile)):
            raise ValueError("dp_mobile is required when 'mobile' is in dp_identifiers")
        return model


async def validate_jwt_token(authorization: str = Header(...), batch_collection=Depends(get_batch_collection)) -> dict:
    """Validate JWT token from Authorization header."""
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    df_id = payload.get("df_id")
    exp_timestamp = payload.get("exp")
    if not df_id or not exp_timestamp:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    expiry = datetime.fromtimestamp(exp_timestamp, UTC)
    if datetime.now(UTC) > expiry:
        await batch_collection.update_one(
            {"df_id": df_id},
            {"$set": {"status": "end", "token": None}},
        )
        raise HTTPException(status_code=401, detail="Token expired")

    batch_data = await batch_collection.find_one({"df_id": df_id})
    if not batch_data or batch_data.get("token") != token:
        raise HTTPException(status_code=401, detail="Invalid token or session expired")

    return {"df_id": df_id, "token": token}


@router.post("/authenticate")
async def authenticate(
    api_key: str = Header(..., alias="api-key"),
    api_secret: str = Header(..., alias="api-secret"),
    df_keys_collection=Depends(get_df_keys_collection),
    batch_collection=Depends(get_batch_collection),
):
    """Authenticate API key/secret and generate or reuse JWT token."""
    df_doc = await df_keys_collection.find_one({"api_keys.add_dp_key": api_key})

    if not df_doc or api_secret != df_doc["api_keys"]["add_dp_secret"]:
        raise HTTPException(status_code=401, detail="Invalid API Key or Secret")

    df_id = df_doc["df_id"]
    batch_data = await batch_collection.find_one({"df_id": df_id})

    if batch_data:
        token_valid = batch_data.get("status") != "end" and datetime.now(UTC) < batch_data.get("expiry", datetime.now(UTC))
        if token_valid:
            return {
                "message": "Authentication successful, reusing existing token",
                "token": batch_data["token"],
            }

    token = await generate_jwt_token(df_id, batch_collection)
    return {"message": "Authentication successful", "token": token}


@router.post("/add-bulk")
async def add_dp_bulk_api_external(
    request: Request,
    dp_data_list: List[BulkDpApiModel],
    batch_tag: Optional[str] = Query(None),
    validated_token: dict = Depends(validate_jwt_token),
    batch_collection=Depends(get_batch_collection),
):
    """Process bulk DP data with JWT validation and queueing to RabbitMQ."""
    df_id = validated_token["df_id"]
    token = validated_token["token"]

    batch_data = await batch_collection.find_one({"df_id": df_id, "token": token})
    if not batch_data or batch_data.get("status") == "end":
        return {
            "message": "Token has expired, please authenticate again",
            "token": None,
        }

    message_data = {
        "df_id": df_id,
        "batch_tag": batch_tag,
        "batch_id": str(batch_data["_id"]),
        "expiry": (batch_data.get("expiry").isoformat() if batch_data.get("expiry") else None),
        "publish_time": datetime.now(UTC).isoformat(),
        "token": token,
    }

    if batch_tag == "end":
        end_time = datetime.now(UTC)
        await batch_collection.update_one(
            {"df_id": df_id, "token": token},
            {"$set": {"status": "end", "token": None, "end_time": end_time}},
        )
        message_data["end_time"] = end_time.isoformat()
        await publish_message("dp_external", json.dumps(message_data))
        return {"message": "Batch processing ended. Token expired.", "token": None}

    if len(dp_data_list) > 1000:
        raise HTTPException(status_code=400, detail="Cannot process more than 1000 records at once")

    processed_data = []
    for dp in dp_data_list:
        dp_dict = dp.model_dump()
        if isinstance(dp_dict.get("created_at_df"), datetime):
            dp_dict["created_at_df"] = dp_dict["created_at_df"].isoformat()
        if isinstance(dp_dict.get("last_activity"), datetime):
            dp_dict["last_activity"] = dp_dict["last_activity"].isoformat()

        processed_data.append(dp_dict)

    update_fields = {"status": "processing"}
    if not batch_data.get("start_time"):
        update_fields["start_time"] = datetime.now(UTC)

    await batch_collection.update_one(
        {"df_id": df_id, "token": token},
        {"$set": update_fields},
    )

    message_data["valid_data"] = processed_data

    await publish_message("dp_external", json.dumps(message_data))

    return {"message": "Bulk import queued for processing", "token": token}


@router.get("/get-bulk")
async def get_data_principal(
    api_key: str = Header(..., alias="api-key"),
    api_secret: str = Header(..., alias="api-secret"),
    page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    dp_identifiers: Optional[List[str]] = Query(None),
    dp_preferred_lang: Optional[str] = Query(None),
    dp_country: Optional[str] = Query(None),
    dp_state: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_legacy: Optional[bool] = Query(None),
    last_activity_from: Optional[datetime] = Query(None),
    last_activity_to: Optional[datetime] = Query(None),
    dp_e: Optional[str] = Query(None),
    dp_m: Optional[str] = Query(None),
    consent_count: Optional[int] = Query(None),
    consent_status: Optional[str] = Query(None),
    df_keys_collection=Depends(get_df_keys_collection),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
):

    df_doc = await df_keys_collection.find_one({"api_keys.add_dp_key": api_key})
    if not df_doc or api_secret != df_doc["api_keys"]["add_dp_secret"]:
        raise HTTPException(status_code=401, detail="Invalid API Key or Secret")

    table_name = "dpd"
    filters: List[str] = []
    values: List[Any] = []

    def add_filter(sql: str, value: Any):
        """Helper to append filters with correct placeholder number"""
        idx = len(values) + 1
        filters.append(sql.replace("{}", f"${idx}"))
        values.append(value)

    if dp_identifiers:
        bad = [x for x in dp_identifiers if x not in ("email", "mobile")]
        if bad:
            raise HTTPException(400, f"dp_identifiers may only include 'email','mobile'; got {bad}")

        add_filter("dp_identifiers @> {}::text[]", dp_identifiers)

    if dp_preferred_lang:
        add_filter("dp_preferred_lang = {}", dp_preferred_lang)

    if dp_country:
        add_filter("dp_country = {}", dp_country)

    if dp_state:
        add_filter("dp_state = {}", dp_state)

    if is_active is not None:
        add_filter("is_active = {}", is_active)

    if is_legacy is not None:
        add_filter("is_legacy = {}", is_legacy)

    if last_activity_from:
        add_filter("last_activity >= {}", last_activity_from)

    if last_activity_to:
        add_filter("last_activity <= {}", last_activity_to)

    if dp_e:
        if dp_e == "empty":
            filters.append("cardinality(dp_email) = 0")
        elif dp_e == "some":
            filters.append("cardinality(dp_email) > 0")
        elif dp_e.isdigit():
            add_filter("cardinality(dp_email) = {}", int(dp_e))
        else:
            raise HTTPException(400, "dp_e must be 'empty','some' or a number")

    if dp_m:
        if dp_m == "empty":
            filters.append("cardinality(dp_mobile) = 0")
        elif dp_m == "some":
            filters.append("cardinality(dp_mobile) > 0")
        elif dp_m.isdigit():
            add_filter("cardinality(dp_mobile) = {}", int(dp_m))
        else:
            raise HTTPException(400, "dp_m must be 'empty','some' or a number")

    if consent_count is not None:
        add_filter("consent_count = {}", consent_count)

    if consent_status:
        add_filter("consent_status = {}", consent_status)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    offset = (page_number - 1) * page_size
    limit = page_size

    select_cols = """
        dp_id,
        dp_system_id,
        dp_identifiers,
        dp_email,
        dp_mobile,
        dp_other_identifier,
        dp_tags,
        cardinality(dp_email)  AS dp_email_count,
        cardinality(dp_mobile) AS dp_mobile_count,
        dp_preferred_lang,
        dp_country,
        dp_state,
        dp_active_devices,
        is_active,
        is_legacy,
        created_at_df,
        last_activity,
        added_by,
        added_with,
        is_deleted,
        consent_status,
        consent_count
    """

    query_count = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
    query_data = f"SELECT {select_cols} FROM {table_name} {where_clause} LIMIT {limit} OFFSET {offset}"

    try:
        async with pool.acquire() as conn:
            total_dp = await conn.fetchval(query_count, *values)
            rows = await conn.fetch(query_data, *values)
    except Exception as e:
        raise HTTPException(500, f"Postgres query error: {e}")

    data = [dict(row) for row in rows]

    return {
        "message": "Data Principals fetched successfully",
        "page_number": page_number,
        "page_size": page_size,
        "returned_records": len(data),
        "total_dp": total_dp,
        "data_principals": data,
    }


@router.put("/update-bulk")
async def update_bulk_dp(
    data_list: List[UpdateBulkDPModel] = Body(...),
    api_key: str = Header(..., alias="api-key"),
    api_secret: str = Header(..., alias="api-secret"),
    df_keys_collection=Depends(get_df_keys_collection),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
):

    df_doc = await df_keys_collection.find_one({"api_keys.add_dp_key": api_key})
    if not df_doc or api_secret != df_doc["api_keys"]["add_dp_secret"]:
        raise HTTPException(status_code=401, detail="Invalid API Key or Secret")
    table_name = f"dpd"

    successes, failures = [], []

    async with pool.acquire() as conn:
        for dp in data_list:

            if not (dp.dp_system_id or dp.dp_id):
                failures.append({"record": dp, "reason": "Require dp_system_id or dp_id"})
                continue
            id_field, id_val = ("dp_system_id", dp.dp_system_id) if dp.dp_system_id else ("dp_id", dp.dp_id)

            select_q = f"""
                SELECT
                    dp_email, dp_mobile, dp_identifiers,
                    dp_state, dp_preferred_lang,
                    dp_active_devices, is_active, is_legacy
                FROM {table_name}
                WHERE {id_field} = $1
                LIMIT 1
            """
            row = await conn.fetchrow(select_q, id_val)
            if not row:
                failures.append({"record": dp, "reason": f"No record for {id_field}={id_val}"})
                continue

            (
                existing_emails,
                existing_mobiles,
                existing_identifiers,
                existing_state,
                existing_preferred_lang,
                existing_active_devices,
                existing_is_active,
                existing_legacy,
            ) = row

            merged_emails = list(set(existing_emails or []) | set(dp.dp_email or []))
            merged_mobiles = list(set(existing_mobiles or []) | set(dp.dp_mobile or []))
            new_identifiers = dp.dp_identifiers or existing_identifiers
            new_state = dp.dp_state or existing_state
            new_lang = dp.dp_preferred_lang or existing_preferred_lang
            new_active_devices = dp.dp_active_devices or existing_active_devices
            new_is_active = dp.is_active if dp.is_active is not None else existing_is_active
            new_is_legacy = dp.is_legacy if dp.is_legacy is not None else existing_legacy

            update_q = f"""
                UPDATE {table_name}
                SET
                    dp_email          = $1,
                    dp_mobile         = $2,
                    dp_other_identifier = $3,
                    dp_identifiers    = $4,
                    dp_state          = $5,
                    dp_preferred_lang = $6,
                    dp_active_devices = $7,
                    dp_tags          = $8,
                    is_active         = $9,
                    is_legacy         = $10
                WHERE {id_field} = $11
            """
            params = [
                merged_emails,
                merged_mobiles,
                new_identifiers,
                new_state,
                new_lang,
                new_active_devices,
                new_is_active,
                new_is_legacy,
                id_val,
            ]

            try:
                result = await conn.execute(update_q, *params)

                if result.startswith("UPDATE"):
                    successes.append(id_val)
                else:
                    failures.append({"record": dp, "reason": f"Update failed for {id_val}"})
            except Exception as e:
                failures.append({"record": dp, "reason": f"DB error: {e}"})

    return {
        "message": "Bulk update finished",
        "total_processed": len(data_list),
        "success_count": len(successes),
        "failure_count": len(failures),
        "failed_details": failures,
    }


@router.get("/export-bulk")
async def export_data_principal(
    api_key: str = Header(..., alias="api-key"),
    api_secret: str = Header(..., alias="api-secret"),
    dp_identifiers: Optional[List[str]] = Query(None, description="email/mobile"),
    dp_preferred_lang: Optional[str] = Query(None),
    dp_country: Optional[str] = Query(None),
    dp_state: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_legacy: Optional[bool] = Query(None),
    last_activity_from: Optional[datetime] = Query(None),
    last_activity_to: Optional[datetime] = Query(None),
    dp_e: Optional[str] = Query(None, description="'empty','some' or exact count for emails"),
    dp_m: Optional[str] = Query(None, description="'empty','some' or exact count for mobiles"),
    consent_count: Optional[int] = Query(None),
    consent_status: Optional[str] = Query(None),
    df_keys_collection=Depends(get_df_keys_collection),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
):

    df_doc = await df_keys_collection.find_one({"api_keys.add_dp_key": api_key, "api_keys.add_dp_secret": api_secret})
    if not df_doc:
        raise HTTPException(401, "Invalid API Key or API Secret")

    table_name = f"dpd"

    filters: List[str] = []
    params: List[Any] = []

    if dp_identifiers:
        bad = [x for x in dp_identifiers if x not in ("email", "mobile")]
        if bad:
            raise HTTPException(400, f"dp_identifiers only email/mobile; got {bad}")
        filters.append(f"dp_identifiers @> ${len(params)+1}")
        params.append(dp_identifiers)

    if dp_preferred_lang:
        filters.append(f"dp_preferred_lang = ${len(params)+1}")
        params.append(dp_preferred_lang)

    if dp_country:
        filters.append(f"dp_country = ${len(params)+1}")
        params.append(dp_country)

    if dp_state:
        filters.append(f"dp_state = ${len(params)+1}")
        params.append(dp_state)

    if is_active is not None:
        filters.append(f"is_active = ${len(params)+1}")
        params.append(is_active)

    if is_legacy is not None:
        filters.append(f"is_legacy = ${len(params)+1}")
        params.append(is_legacy)

    if last_activity_from:
        filters.append(f"last_activity >= ${len(params)+1}")
        params.append(last_activity_from)

    if last_activity_to:
        filters.append(f"last_activity <= ${len(params)+1}")
        params.append(last_activity_to)

    if dp_e:
        if dp_e == "empty":
            filters.append("array_length(dp_email,1) IS NULL")
        elif dp_e == "some":
            filters.append("array_length(dp_email,1) > 0")
        elif dp_e.isdigit():
            filters.append(f"array_length(dp_email,1) = ${len(params)+1}")
            params.append(int(dp_e))
        else:
            raise HTTPException(400, "dp_e must be 'empty','some' or a number")

    if dp_m:
        if dp_m == "empty":
            filters.append("array_length(dp_mobile,1) IS NULL")
        elif dp_m == "some":
            filters.append("array_length(dp_mobile,1) > 0")
        elif dp_m.isdigit():
            filters.append(f"array_length(dp_mobile,1) = ${len(params)+1}")
            params.append(int(dp_m))
        else:
            raise HTTPException(400, "dp_m must be 'empty','some' or a number")

    if consent_count is not None:
        filters.append(f"consent_count = ${len(params)+1}")
        params.append(consent_count)

    if consent_status:
        filters.append(f"consent_status = ${len(params)+1}")
        params.append(consent_status)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    select_cols = """
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
        created_at_df,
        last_activity,
        added_by,
        added_with,
        is_deleted,
        consent_status,
        consent_count
    """
    query = f"SELECT {select_cols} FROM {table_name} {where_clause}"

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
    except Exception as e:
        raise HTTPException(500, f"Postgres query error: {e}")

    columns = [c.strip() for c in select_cols.split(",")]

    def iter_csv():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)

        for row in rows:
            writer.writerow([row[col] for col in columns])
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="data_principals.csv"'},
    )
