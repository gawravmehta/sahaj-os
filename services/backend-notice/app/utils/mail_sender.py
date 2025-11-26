import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.logger import get_logger


logger = get_logger("utils.mail_sender")


async def mail_sender(destination_email: str, subject: str, email_template: str, df_register_collection: AsyncIOMotorClient = None):
    logger.info(f"Preparing to send email to {destination_email} with subject '{subject}'", extra={"destination_email": destination_email, "subject": subject})

    df_details = await df_register_collection.find_one({})
    smtp_credentials = df_details.get("communication", {}).get("smtp", {}).get("credentials", {})

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_credentials.get("from_email")
    msg["To"] = destination_email
    msg["Subject"] = subject

    html_part = MIMEText(email_template, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP(smtp_credentials.get("host"), smtp_credentials.get("port"))
        server.starttls()
        server.login(smtp_credentials.get("username"), smtp_credentials.get("password"))
        server.sendmail(smtp_credentials.get("from_email"), destination_email, msg.as_string())
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
    finally:
        server.quit()
