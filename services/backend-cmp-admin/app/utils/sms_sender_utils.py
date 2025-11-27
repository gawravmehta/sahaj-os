from urllib.parse import quote_plus
from app.core.config import settings
import requests


async def send_sms_notification(phone_number, token, df_register_collection, sms_template_name):
    df_details = await df_register_collection.find_one({})

    sms_credentials = df_details.get("communication", {}).get("sms", {}).get("credentials", {})

    user_name = df_details.get("org_info", {}).get("name", "Data Fiduciary")
    consent_link = f"{settings.CMP_NOTICE_WORKER_URL}/{sms_credentials.get('sender_id')}?{token}"

    sms_content = df_details.get("communication", {}).get("sms", {}).get("templates", [])
    sms_template = next((template for template in sms_content if template.get("name") == sms_template_name), None)

    sms_text = sms_template.get("content", "").replace("{user_name}", user_name).replace("{consent_link}", consent_link)

    encoded_text = quote_plus(sms_text)

    api_url = (
        f"{sms_credentials.get('base_url')}"
        f"?username={sms_credentials.get('username')}"
        f"&password={sms_credentials.get('password')}"
        f"&unicode={sms_credentials.get('unicode', False)}"
        f"&from={sms_credentials.get('sender_id')}"
        f"&to={phone_number}"
        f"&text={encoded_text}"
    )

    response = requests.get(api_url)

    return True
