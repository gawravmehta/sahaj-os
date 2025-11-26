import hashlib
import json
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from jose import jwt
from app.db.session import get_postgres_pool
from app.schemas.consent_schema import TokenModel
from datetime import datetime, timedelta
from app.core.config import settings
from app.utils.verification_utils import otp_verified_key
from app.core.logger import get_logger


logger = get_logger("service.consent_artifact_service")


def get_expiry_timestamp(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).isoformat()


async def data_element_consent_creation(token_model: TokenModel, df_id: str, collection_point_id: str, gdb):

    collection_point = await gdb.cp_master.find_one({"_id": ObjectId(collection_point_id), "df_id": df_id})
    if not collection_point:
        raise HTTPException(status_code=404, detail="Collection point not found")

    notice_data_elements = collection_point.get("data_elements", [])

    consented_pairs = set()
    for data_element in token_model.data_elements:
        for consent_purpose in data_element.consents:
            consented_pairs.add((data_element.de_id, consent_purpose.purpose_id))

    data_elements_consents = []
    for notice_de in notice_data_elements:
        de_id = notice_de["de_id"]
        de_doc = await gdb.de_master.find_one({"_id": ObjectId(de_id), "df_id": df_id})
        if not de_doc:
            continue

        retention_days = de_doc.get("de_retention_period", 0)
        data_retention_period = get_expiry_timestamp(retention_days)

        consents_list = []
        for consent_purpose in notice_de["purposes"]:
            purpose_id = consent_purpose["purpose_id"]
            purpose_doc = await gdb.purpose_master.find_one({"_id": ObjectId(purpose_id), "df_id": df_id})
            if not purpose_doc:
                continue

            is_consented = (de_id, purpose_id) in consented_pairs

            data_processors = []
            for processor in purpose_doc.get("data_processor_details", []):
                data_processors.append(
                    {
                        "data_processor_id": str(processor.get("data_processor_id", "")),
                        "data_processor_name": processor.get("data_processor_name", ""),
                        "cross_border_data_transfer": processor.get("cross_border_data_transfer", False),
                        "consent_mode": "STORE",
                        "consent_expiry_period": processor.get("consent_period", 0),
                        "data_retention_period": processor.get("retention_period", 0),
                    }
                )

            purpose_data_elements = purpose_doc.get("data_elements", [])
            matched_de = next((de for de in purpose_data_elements if de.get("de_id") == de_id), None)

            if matched_de:
                is_service_mandatory = matched_de.get("service_mandatory", False)
                service_mandatory_message = matched_de.get("service_message", "")

                is_legal_mandatory = matched_de.get("legal_mandatory", False)
                legal_mandatory_message = matched_de.get("legal_message", "")
            else:
                is_service_mandatory = False
                service_mandatory_message = ""
                is_legal_mandatory = False
                legal_mandatory_message = ""

            consents_list.append(
                {
                    "purpose_id": str(purpose_doc["_id"]),
                    "purpose_hash_id": str(purpose_doc.get("purpose_hash_id", "")),
                    "purpose_title": purpose_doc.get("purpose_title", ""),
                    "description": purpose_doc.get("purpose_description", ""),
                    "consent_expiry_period": get_expiry_timestamp(purpose_doc.get("consent_time_period", 0)),
                    "consent_status": "approved" if is_consented else "denied",
                    "shared": False,
                    "consent_mode": "STORE",
                    "data_processors": data_processors,
                    "cross_border": any(proc["cross_border_data_transfer"] for proc in data_processors),
                    "consent_timestamp": (datetime.now().isoformat() if is_consented else ""),
                    "retention_timestamp": data_retention_period,
                    "is_legal_mandatory": is_legal_mandatory,
                    "legal_mandatory_message": legal_mandatory_message,
                    "is_service_mandatory": is_service_mandatory,
                    "service_mandatory_message": service_mandatory_message,
                    "reconsent": purpose_doc.get("reconsent", False),
                }
            )

        data_elements_consents.append(
            {
                "de_id": str(de_doc["_id"]),
                "de_hash_id": str(de_doc.get("de_hash_id", "")),
                "title": de_doc.get("de_name", "Unnamed Data Element"),
                "data_retention_period": data_retention_period,
                "de_status": "active",
                "consents": consents_list,
            }
        )
    return data_elements_consents


async def consent_artifact_creation(
    collection_point_name,
    collection_point_id,
    binded_ip,
    request_headers_hash,
    request_headers,
    data_principal,
    df_id,
    data_elements_consents,
    is_legacy=False,
    agreement_id: Optional[str] = None,
):

    artifact_dict = {
        "context": "https://consent.foundation/artifact/v1",
        "agreement_id": agreement_id or "",
        "cp_id": collection_point_id,
        "cp_name": collection_point_name,
        "agreement_version": 1,
        "metadata": {
            "ip_address": binded_ip,
            "request_header_hash": request_headers_hash,
        },
        "data_principal": data_principal,
        "data_fiduciary": {
            "df_id": df_id,
            "agreement_date": datetime.now().isoformat(),
        },
        "consent_scope": {
            "data_elements": data_elements_consents,
        },
    }

    artifact_json = json.dumps(artifact_dict, sort_keys=True, separators=(",", ":"))
    artifact_hash = hashlib.shake_256(artifact_json.encode()).hexdigest(32)

    consent_artifacts = {
        "artifact": artifact_dict,
        "request_header": request_headers,
        "agreement_hash_id": artifact_hash,
        "is_legacy": is_legacy,
    }
    return consent_artifacts


async def hash_headers(request_headers):

    headers = dict(request_headers)
    headers_str = "".join(f"{k}:{v}" for k, v in sorted(headers.items()))
    headers_bytes = headers_str.encode("utf-8")

    shake = hashlib.shake_256()
    shake.update(headers_bytes)

    headers_hash = shake.hexdigest(64)

    return headers_hash


async def validate_jwt_token(token):
    """Validate JWT token and return payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )
        return payload
    except Exception as e:
        logger.error(f"JWT decode failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_dp_info_from_postgres(dp_id: str, redis_client, payload, is_verification_required: bool = False):
    """
    Fetch DP info from Postgres (df_id-specific dpd table).
    """

    pool = await get_postgres_pool()

    table_name = f"dpd"
    query = f"""
        SELECT 
            dp_system_id,
            dp_country,
            dp_e,
            dp_m
        FROM {table_name}
        WHERE dp_id = $1 AND is_deleted = false
        LIMIT 1
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, dp_id)

        if not row:
            logger.warning(f"No DP found with dp_id: {dp_id}", extra={"dp_id": dp_id})
            return None

        dp_verification = not is_verification_required

        data_principal = {
            "dp_id": dp_id,
            "dp_df_id": row["dp_system_id"],
            "dp_residency": row["dp_country"] or "",
            "dp_e": row["dp_e"][0] if row["dp_e"] else "",
            "dp_m": row["dp_m"][0] if row["dp_m"] else "",
            "dp_vt": "",
            "dp_verification": dp_verification,
            "dp_child": False,
            "dp_parental": {
                "dp_df_id": "",
                "dp_public_key": "",
                "dp_e": "",
                "dp_m": "",
                "dp_vt": "",
            },
            "dp_attorney": {
                "dp_df_id": "",
                "dp_public_key": "",
                "dp_e": "",
                "dp_m": "",
                "dp_vt": "",
            },
        }

        logger.info("Data Principal Information", extra={"data_principal": data_principal})

        return data_principal

    except Exception as e:
        logger.error(f"Postgres query failed: {str(e)}", exc_info=True, extra={"dp_id": dp_id})
        raise RuntimeError(f"Postgres query failed: {str(e)}")


async def get_dp_email_and_mobile(dp_id: str):
    """
    Fetch DP email and mobile from postgres dpd table.
    """

    pool = await get_postgres_pool()

    table_name = f"dpd"
    query = f"""
        SELECT 
            dp_email,
            dp_mobile
        FROM {table_name}
        WHERE dp_id = $1 AND is_deleted = false
        LIMIT 1
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, dp_id)

        if not row:
            logger.warning(f"No DP found with dp_id: {dp_id}", extra={"dp_id": dp_id})
            return None

        return {
            "dp_email": row["dp_email"][0] if row["dp_email"] else "",
            "dp_mobile": row["dp_mobile"][0] if row["dp_mobile"] else "",
        }

    except Exception as e:
        logger.error(f"Postgres query failed: {str(e)}", exc_info=True, extra={"dp_id": dp_id})
        raise RuntimeError(f"Postgres query failed: {str(e)}")
