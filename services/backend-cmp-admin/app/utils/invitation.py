import secrets
from app.core.config import settings


def generate_invite_token(prefix: str = "", length: int = 32):
    token = secrets.token_urlsafe(length)
    return f"{prefix}-{token}"


def get_invitation_html(invited_user_name: str, invite_token: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>You're Invited to Join Concur</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
    </head>
    <body style="font-family: 'Inter', Arial, sans-serif; color: #333; background-color: #f0f2f5; padding: 20px; margin: 0;">
        <div style="max-width: 650px; margin: 40px auto; background: white; padding: 40px 30px; border-radius: 10px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08); border: 1px solid #e5e7eb;">
        
        <!-- Brand Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="org" alt="org Logo" style="max-height: 60px; margin-bottom: 10px;" />
            <h2 style="margin: 5px 0 25px 0; font-weight: 600; font-size: 20px;">org</h2>
        </div>

        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: rgb(0, 28, 100); font-size: 28px; margin: 0; padding-bottom: 10px; border-bottom: 2px solid #e0e0e0; display: inline-block;">
                Welcome to Concur - India's DPDPA-Ready Consent Platform
            </h1>
            <p style="color: #666; font-size: 15px; margin-top: 10px;">Empowering Responsible Data Handling Under the Digital Personal Data Protection Act</p>
        </div>

        <p style="font-size: 16px;">Dear <strong>{invited_user_name}</strong>,</p>

        <p style="font-size: 16px;">
            <strong>first name</strong> has invited you to collaborate on <strong>Concur</strong>, a purpose-built consent management platform aligned with India's <strong>Digital Personal Data Protection Act (DPDPA), 2023</strong>.
        </p>

        <p style="font-size: 16px;">
            Concur helps Data Fiduciaries like you ensure lawful processing of personal data by offering tools to:
        </p>

        <ul style="margin-top: 10px; font-size: 16px;">
            <li>✅ Manage and audit user consent with full traceability</li>
            <li>✅ Define collection points, data elements, and purposes with granularity</li>
            <li>✅ Maintain purpose limitation and data minimization</li>
            <li>✅ Generate compliance reports and fulfill user rights requests</li>
        </ul>

        <p style="font-size: 16px;">
            To activate your Concur account and begin fulfilling your obligations under DPDPA, please click the secure invitation link below:
        </p>

        <div style="text-align: center; margin: 40px 0;">
            <a href="http://localhost:3000/accept-invite/{invite_token}" style="background-color: rgb(0, 28, 100); color: white; padding: 15px 35px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);">
                Accept Invitation & Comply with DPDPA
            </a>
        </div>

        <p style="font-size: 15px; text-align: center; color: #666;">This invitation is valid for 30 days from the date of issue.</p>

        <p style="font-size: 15px; margin-top: 30px;">
            If the button does not work, copy and paste the following URL into your browser:
        </p>
        <p style="word-break: break-all; font-size: 15px;">
            <a href="{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}" style="color: #007bff;">
                {settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}
            </a>
        </p>

        <hr style="border: 0; border-top: 1px solid #e0e0e0; margin: 45px 0 25px 0;" />

        <p style="font-size: 13px; color: #777; text-align: center; margin-bottom: 5px;">
            If you received this email by mistake, you can safely ignore it.
        </p>
        <p style="font-size: 13px; color: #777; text-align: center;">
            For help, contact your organization's Data Protection Officer or admin.
        </p>

        <p style="font-size: 11px; color: #bbb; text-align: center; margin-top: 25px;">
            Internal development link:
            <a href="{settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}" style="color: #bbb; text-decoration: none;">
                {settings.CMP_ADMIN_FRONTEND_URL}/accept-invite/{invite_token}
            </a>
        </p>
        </div>
    </body>
    </html>
    """
