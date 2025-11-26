from datetime import UTC, datetime
from fastapi import BackgroundTasks
from app.utils.mail_sender import mail_sender
from app.utils.verification_utils import OTP_TTL_SECONDS, gen_otp, otp_key, redis_json_encode
from app.core.logger import get_logger


logger = get_logger("service.otp_service")


def _otp_email_html(otp: str) -> str:
    return f"""
    <html>
      <body>
        <h1>Verification OTP</h1>
        <p>OTP: <strong>{otp}</strong></p>
        <p>Do not share this OTP with anyone.</p>
      </body>
    </html>
    """


async def _send_verification_otp_email(background_tasks: BackgroundTasks, email: str, html: str, df_register_collection):
    logger.info("Sending verification email", extra={"email": email})
    background_tasks.add_task(mail_sender, email, "Verification OTP", html, df_register_collection)


async def _send_verification_sms(background_tasks: BackgroundTasks, mobile: str, otp: str):
    async def _fake_sms():
        logger.info(f"[SMS] to {mobile}: OTP {otp}", extra={"mobile": mobile, "otp": otp})

    background_tasks.add_task(_fake_sms)


async def send_otp_if_required(
    redis_client, background_tasks: BackgroundTasks, payload: dict, cp: dict, dp_email: str = None, dp_mobile: str = None, db=None
):
    """
    Generates and sends an OTP if required.
    Returns True if OTP was sent, False otherwise.
    """

    otp = gen_otp()
    otp_obj = {
        "otp": otp,
        "attempts": 0,
        "created_at": str(datetime.now(UTC)),
        "last_sent_at": 0,
        "ttl": OTP_TTL_SECONDS,
        "locked": False,
    }
    await redis_client.setex(otp_key(payload), OTP_TTL_SECONDS, redis_json_encode(otp_obj))

    medium = cp.get("prefered_verification_medium", "email")
    if medium == "email" and dp_email:
        await _send_verification_otp_email(background_tasks, dp_email, _otp_email_html(otp), db["df_register"])
    elif medium == "sms" and dp_mobile:
        await _send_verification_sms(background_tasks, dp_mobile, otp)
    else:
        logger.warning(f"No contact to send OTP; printing: {otp}", extra={"otp": otp})

    return True
