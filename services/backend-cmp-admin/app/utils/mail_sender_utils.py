import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import app_logger


async def mail_sender(destination_email: str, subject: str, email_template: str, df_register_collection: AsyncIOMotorClient = None):
    app_logger.info(f"Attempting to send email to {destination_email} with subject: {subject}")

    df_details = await df_register_collection.find_one({})
    if not df_details:
        app_logger.error("DF details not found in collection. Cannot send email.")
        return

    smtp_credentials = df_details.get("communication", {}).get("smtp", {}).get("credentials", {})
    if not smtp_credentials:
        app_logger.error("SMTP credentials not found in DF details. Cannot send email.")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_credentials.get("from_email")
    msg["To"] = destination_email
    msg["Subject"] = subject

    html_part = MIMEText(email_template, "html")
    msg.attach(html_part)

    server = None
    try:
        app_logger.debug(f"Connecting to SMTP server: {smtp_credentials.get('host')}:{smtp_credentials.get('port')}")
        server = smtplib.SMTP(smtp_credentials.get("host"), smtp_credentials.get("port"))
        server.starttls()
        server.login(smtp_credentials.get("username"), smtp_credentials.get("password"))
        server.sendmail(smtp_credentials.get("from_email"), destination_email, msg.as_string())
        app_logger.info(f"Email successfully sent to {destination_email}")
    except Exception as e:
        app_logger.error(f"Failed to send email to {destination_email}: {e}", exc_info=True)
    finally:
        if server:
            server.quit()
            app_logger.debug("SMTP server connection closed.")
