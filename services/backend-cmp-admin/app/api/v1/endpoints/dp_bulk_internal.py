import json
import os
import time
import asyncpg
from fastapi import APIRouter, Request, UploadFile, File, Query, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.deps import get_current_user
from typing import Literal, Optional, List

from bson import json_util
import pandas as pd

from app.core.config import settings
from app.db.dependencies import get_dp_file_processing_collection
from app.db.rabbitmq import publish_message
from app.db.session import get_postgres_pool, get_s3_client
from datetime import datetime, UTC

import io

from app.utils.common import count_rows_in_file

router = APIRouter()


@router.post("/bulk-import-data-principal")
async def bulk_import_data_principal(
    request: Request,
    file: UploadFile = File(...),
    is_legacy: bool = Query(False, description="Is legacy"),
    dp_tags: Optional[List[str]] = Query(None, description="Tags associated with the data principal"),
    current_user: dict = Depends(get_current_user),
    s3_client=Depends(get_s3_client),
    dp_file_processing_collection=Depends(get_dp_file_processing_collection),
):
    df_id = current_user.get("df_id")
    if not df_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    genie_user_id = str(current_user.get("_id"))
    if not genie_user_id:
        raise HTTPException(status_code=401, detail="Genie user id is missing")
    contents = await file.read()
    file_type = file.filename.rsplit(".", 1)[-1].lower()
    if file_type not in ("csv", "xlsx"):
        raise HTTPException(415, "Unsupported file type")

    filename = f"{df_id}_{genie_user_id}_{int(time.time())}.{file_type}"
    local_path = f"app/uploads/{file.filename}"
    with open(local_path, "wb") as buf:
        buf.write(contents)

    try:
        s3_client.fput_object(
            settings.UNPROCESSED_FILES_BUCKET,
            filename,
            local_path,
            file.content_type,
        )
        os.remove(local_path)

        await dp_file_processing_collection.insert_one(
            {
                "filename": filename,
                "df_id": df_id,
                "genie_user_id": genie_user_id,
                "status": "pending",
                "created_at": datetime.now(UTC),
            }
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to upload file to S3: {e}")

    try:
        message = json.dumps(
            {
                "filename": filename,
                "df_id": df_id,
                "genie_user_id": genie_user_id,
                "is_legacy": is_legacy,
                "file_type": file_type,
                "dp_tags": dp_tags or [],
            }
        )
        await publish_message("dp_processing", message)
    except Exception as e:
        raise HTTPException(500, f"Failed to publish message to queue: {e}")

    row_count = count_rows_in_file(contents, file_type) - 1

    return JSONResponse(
        {
            "status": "processing_started",
            "message": "File accepted; processing in background.",
            "files_received": file.filename,
            "row_count": row_count,
        }
    )


@router.get("/bulk-export-data-principal")
async def bulk_export_data_principal(
    request: Request,
    format: Optional[str] = Query("csv", description="Specifies the format of the exported file (csv or excel)"),
    filter: Optional[str] = Query(None, description="JSON-encoded filter criteria to apply"),
    tags: Optional[List[str]] = Query(None, description="List of tags to filter data principals"),
    match_type: Literal["contains all", "contains any"] = Query(
        ...,
        description="Match type: either 'contains all' (delete only if all tags are present) or 'contains any' (delete if any tag is present)",
    ),
    current_user: dict = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
):
    df_id = current_user.get("df_id")
    if not df_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if format not in ["csv", "xlsx"]:
        raise HTTPException(status_code=415, detail="File is not in format of CSV/xlsx")

    query_filter = {}
    if filter:
        try:
            query_filter = json.loads(filter, object_hook=json_util.object_hook)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid filter Parameter")

    try:
        table_name = f"dpd"
        conditions = ["is_deleted = FALSE"]
        params = {}

        for idx, (key, value) in enumerate(query_filter.items(), start=1):
            if isinstance(value, bool):
                value = 1 if value else 0
            conditions.append(f"{key} = ${idx}")
            params[idx] = value

        if tags:
            mt = match_type.strip().lower()
            if mt not in ["contains all", "contains any"]:
                raise HTTPException(status_code=400, detail="Invalid match_type provided")

            if mt == "contains all":
                conditions.append(f"dp_tags @> ${len(params) + 1}::text[]")
            elif mt == "contains any":
                conditions.append(f"dp_tags && ${len(params) + 1}::text[]")

            params[len(params) + 1] = tags

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = "WHERE " + where_clause

        query = f"SELECT * FROM {table_name} {where_clause}"
        values = list(params.values())

        rows = await pool.fetch(query, *values)
        if not rows:
            raise HTTPException(status_code=404, detail="No data principal was found")

        data_principals = [dict(row) for row in rows]
        df = pd.DataFrame(data_principals)

        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

        output = io.BytesIO()
        if format == "csv":
            df.to_csv(output, index=False)
            output.seek(0)
            file_name = "data_principals_exports.csv"
            content_type = "text/csv"
        else:
            for col in df.select_dtypes(include=["datetime64[ns, UTC]", "datetime64[ns]"]).columns:
                df[col] = df[col].dt.tz_localize(None)

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Data Principals")

            output.seek(0)
            file_name = "data_principals_exports.xlsx"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        headers = {"Content-Disposition": f"attachment; filename={file_name}"}
        return StreamingResponse(output, media_type=content_type, headers=headers)

    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete("/delete-data-principals-by-tags", tags=["Data Principal Management"])
async def delete_data_principals_by_tags(
    request: Request,
    tags: List[str] = Query(..., description="List of tags to match"),
    match_type: Literal["contains all", "contains any"] = Query(
        ...,
        description="Match type: either 'contains all' (delete only if all tags are present) or 'contains any' (delete if any tag is present)",
    ),
    current_user: dict = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
):
    df_id = current_user.get("df_id")
    user_id = str(current_user.get("_id"))

    if not df_id:
        raise HTTPException(status_code=400, detail="Missing df_id for current user")

    if not tags:
        raise HTTPException(status_code=400, detail="Tags list cannot be empty")

    table_name = "dpd"
    mt = match_type.strip().lower()

    if mt == "contains all":

        tag_condition = f"dp_tags @> $1::text[]"
    elif mt == "contains any":

        tag_condition = f"dp_tags && $1::text[]"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid match type. Use 'contains all' or 'contains any'.",
        )

    consent_filter = "lower(coalesce(consent_status, '')) IN ('', 'unsent') AND consent_count = 0"
    full_condition = f"{tag_condition} AND {consent_filter}"

    async with pool.acquire() as conn:
        try:

            count_query = f"SELECT COUNT(*) FROM {table_name} WHERE {full_condition}"
            deleted_rows = await conn.fetchval(count_query, tags)

            update_query = f"""
                UPDATE {table_name}
                SET is_deleted = TRUE
                WHERE {full_condition}
            """
            await conn.execute(update_query, tags)

            return {
                "message": "Deletion completed",
                "deleted_tags": tags,
                "match_type": match_type,
                "deleted_rows": deleted_rows,
                "note": "Only principals with empty or 'unsent' consent_status were deleted",
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
