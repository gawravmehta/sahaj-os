from io import BytesIO
import json
from fastapi import HTTPException
from bson import ObjectId
from minio import Minio
from app.tasks.translate_cp import translate_notice_structure
from app.config.mongodb import (
    notice_languages_collection,
    de_master_translated,
    purpose_master_translated,
    df_register_collection,
)


def generate_notice_html(
    cp_id: str,
    notice_id: str,
    df_id: str,
    cp_master,
    notice_master_collection,
    consent_purpose_collection,
    de_master,
):
    collection_point_doc = cp_master.find_one({"_id": ObjectId(cp_id)})
    if not collection_point_doc:
        raise HTTPException(status_code=404, detail="Collection point not found")

    notice_details = notice_master_collection.find_one({"_id": ObjectId(notice_id), "df_id": df_id})
    if not notice_details:
        raise HTTPException(status_code=404, detail="Notice not found")

    notice_html = notice_details.get("notice_html")
    if not notice_html:
        raise HTTPException(status_code=404, detail="Notice HTML not found")

    df_docs = df_register_collection.find_one({"df_id": df_id})

    df_name = df_docs.get("organization", "Data Fiduciary")

    supported_languages = [
        "eng",
        "asm",
        "mni",
        "nep",
        "san",
        "urd",
        "hin",
        "mai",
        "tam",
        "mal",
        "ben",
        "kok",
        "guj",
        "kan",
        "snd",
        "ori",
        "sat",
        "pan",
        "mar",
        "tel",
        "kas",
        "brx",
    ]

    language_translations = {}
    for lang in supported_languages:
        translation_doc = notice_languages_collection.find_one({"language": lang})
        if not translation_doc:
            continue

        translation_doc.pop("_id", None)
        translation_doc.pop("language", None)

        formatted = json.loads(json.dumps(translation_doc).replace("{df_name}", df_name))
        language_translations[lang] = formatted

    notice_structure = {}

    if notice_details.get("notice_type") == "simple":
        data_elements_list = []

        for element in collection_point_doc["notice_details"]["data_elements"]:
            de_doc = de_master.find_one({"_id": ObjectId(element["de_id"])})
            if not de_doc:
                continue

            consents_list = []
            for purpose in element.get("consent_purposes", []):
                consent_doc = consent_purpose_collection.find_one({"_id": ObjectId(purpose["consent_purpose_id"])})
                if not consent_doc:
                    continue

                consents_list.append(
                    {
                        "purpose_id": str(consent_doc["_id"]),
                        "description": consent_doc.get("consent_purpose_title", ""),
                        "consent_expiry_period": consent_doc.get("consent_purpose_consent_time_period", ""),
                    }
                )

            data_elements_list.append(
                {
                    "de_id": str(de_doc["_id"]),
                    "title": de_doc.get("data_element_name", "Unknown Data Element"),
                    "data_retention_period": de_doc.get("compliance", {}).get("de_data_retention_period", "Unknown Period"),
                    "consents": consents_list,
                }
            )

        notice_structure = {lang: {**language_translations[lang], "data_elements": data_elements_list} for lang in language_translations}

    elif notice_details.get("notice_type") == "complex":
        purpose_map = {}

        for element in collection_point_doc.get("notice_details", {}).get("data_elements", []):
            for purpose in element.get("consent_purposes", []):
                purpose_id = purpose["consent_purpose_id"]

                if purpose_id not in purpose_map:
                    consent_doc = consent_purpose_collection.find_one({"_id": ObjectId(purpose_id)})
                    if not consent_doc:
                        continue

                    purpose_map[purpose_id] = {
                        "title": "bp_123 Banking Services & Account Management",
                        "consents": [
                            {
                                "purpose_id": str(consent_doc["_id"]),
                                "title": consent_doc.get("consent_purpose_title", ""),
                                "description": consent_doc.get("consent_purpose_description", ""),
                                "duration": consent_doc.get("consent_purpose_consent_time_period", ""),
                                "dataElements": [],
                            }
                        ],
                    }

                de_doc = de_master.find_one({"_id": ObjectId(element.get("de_id"))})
                if not de_doc:
                    continue

                data_element_info = {
                    "de_id": str(de_doc["_id"]),
                    "de_name": de_doc.get("data_element_name", "Unknown"),
                    "data_retention_period": de_doc.get("compliance", {}).get("de_data_retention_period", "Unknown"),
                }

                purpose_map[purpose_id]["consents"][0]["dataElements"].append(data_element_info)

        purpose_list = list(purpose_map.values())
        notice_structure = {lang: {**language_translations[lang], "purposes": purpose_list} for lang in language_translations}

    else:
        raise HTTPException(status_code=400, detail="Invalid notice type")

    response = translate_notice_structure(
        notice_structure,
        supported_languages,
        de_master_translated,
        purpose_master_translated,
    )

    html_content = notice_html

    notice_json = json.dumps(response, indent=2, ensure_ascii=False)
    html_content = html_content.replace("{{ NOTICE_DATA }}", notice_json)

    return html_content


def upload_html_to_minio(
    s3_client: Minio,
    file_content: str,
    file_name: str,
    bucket: str,
    df_id: str,
    cp_id: str,
    notice_id: str,
) -> str:
    if not s3_client.bucket_exists(bucket):
        s3_client.make_bucket(bucket)

    file_path = f"notices/{df_id}/{cp_id}_{notice_id}.html"
    html_bytes = BytesIO(file_content.encode("utf-8"))

    s3_client.put_object(
        bucket_name=bucket,
        object_name=file_path,
        data=html_bytes,
        length=len(html_bytes.getvalue()),
        content_type="text/html",
    )

    url = s3_client.presigned_get_object(bucket, file_path)
    return url
