import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import BaseModel
import secrets
from app.core.logger import app_logger


class EmailSenderCredentials(BaseModel):
    username: str
    password: str
    server_addr: str
    server_port: int
    sender_email: str
    subject: str = "Welcome to Our Application"


async def get_email_credentials(df_id: str, collection) -> EmailSenderCredentials:
    """Fetch email credentials from the database based on df_id."""
    if not df_id:
        app_logger.info("Error: df_id is missing for email credentials fetch.")
        return None

    try:
        org_data = await collection.find_one({"df_id": df_id})

        if not org_data:
            app_logger.info(f"Error: Organization with df_id {df_id} not found.")
            return None

        smtp_config = org_data.get("communication", {}).get("smtp", {}).get("credentials", {})

        if not smtp_config:
            app_logger.info(f"Error: SMTP credentials not found for df_id {df_id}.")
            return None

        return EmailSenderCredentials(
            username=smtp_config.get("username"),
            password=smtp_config.get("password"),
            server_addr=smtp_config.get("host"),
            server_port=int(smtp_config.get("port", 587)),
            sender_email=smtp_config.get("from_email"),
            subject="Welcome to Our Application",
        )

    except Exception as e:
        app_logger.info(f"Failed to fetch email credentials: {e}")
        return None


async def mailSender(destination_email: str, subject: str, email_template: str, credentials: EmailSenderCredentials):
    if not credentials:
        app_logger.info("Error: Missing email credentials. Cannot send email.")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = credentials.sender_email
    msg["To"] = destination_email
    msg["Subject"] = subject

    html_part = MIMEText(email_template, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP(credentials.server_addr, credentials.server_port)
        server.starttls()
        server.login(credentials.username, credentials.password)
        server.sendmail(credentials.sender_email, destination_email, msg.as_string())
        app_logger.info("Email sent successfully!")
    except Exception as e:
        app_logger.error(f"Failed to send email: {e}")
    finally:
        try:
            server.quit()
        except:
            pass


def GenereateInviteToken(prefix: str = "", length: int = 32):
    token = secrets.token_urlsafe(length)
    return f"{prefix}-{token}"
