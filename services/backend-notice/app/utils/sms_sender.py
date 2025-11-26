from urllib.parse import quote_plus
import requests
from app.core.logger import get_logger


logger = get_logger("utils.sms_sender")


async def send_sms_notification(phone_number, token, df_register_collection, sms_template_name):
    df_details = await df_register_collection.find_one({})

    sms_credentials = df_details.get("communication", {}).get("sms", {}).get("credentials", {})

    user_name = df_details.get("org_info", {}).get("name", "Some Company")

    sms_content = df_details.get("communication", {}).get("sms", {}).get("templates", [])
    sms_template = next((template for template in sms_content if template.get("name") == sms_template_name), None)

    sms_text = "Sample text"

    encoded_text = quote_plus(sms_text)

    logger.info("Sending SMS to: %s with text: %s", phone_number, sms_text, extra={"phone_number": phone_number, "sms_text": sms_text})

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
    logger.info("SMS API Response: %s", response.json())

    return True
