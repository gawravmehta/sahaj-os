from encodings import unicode_escape
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class AuditInfo(BaseModel):
    last_updated_by: Optional[str] = None
    last_updated_at: Optional[datetime] = None


class OrgInfo(BaseModel):
    name: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    country: Optional[str] = None
    cookie_policy_url: Optional[HttpUrl] = None
    privacy_policy_url: Optional[HttpUrl] = None
    df_logo_url: Optional[HttpUrl] = None
    address: Optional[str] = None


class SMTPCredentials(BaseModel):
    provider: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    tls: bool = True
    encryption_type: Optional[str] = "TLS"


class SMTPSystemConfig(BaseModel):
    max_email_allowed: int = 10000
    daily_email_limit: int = 500
    is_active: bool = True
    is_blocked: bool = False
    is_sandbox_mode: bool = False
    email_blacklist: Optional[List[EmailStr]] = []
    is_two_factor_enabled: bool = False
    ip_restrictions: Optional[List[str]] = []
    spam_rate: float = 0.0
    bounce_rate: float = 0.0
    delivery_rate: float = 0.0
    last_email_sent_time: Optional[datetime] = None


class SMTPConfig(BaseModel):
    credentials: Optional[SMTPCredentials] = None
    system: Optional[SMTPSystemConfig] = SMTPSystemConfig()
    audit: Optional[AuditInfo] = AuditInfo()


class SMSCredentials(BaseModel):
    provider: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    sender_id: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    region: Optional[str] = "IN"
    unicode: bool = False


class SMSSystemConfig(BaseModel):
    max_sms_allowed: int = 5000
    daily_sms_limit: int = 300
    is_active: bool = True
    is_blocked: bool = False
    is_sandbox_mode: bool = False
    sms_blacklist: Optional[List[str]] = []
    last_sms_sent_time: Optional[datetime] = None
    delivery_rate: float = 0.0
    failure_rate: float = 0.0


class NotificationTemplate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


class SMSConfig(BaseModel):
    credentials: Optional[SMSCredentials] = None
    system: Optional[SMSSystemConfig] = SMSSystemConfig()
    audit: Optional[AuditInfo] = AuditInfo()
    templates: Optional[List[NotificationTemplate]] = None


class AIConfig(BaseModel):
    openrouter_api_key: Optional[str] = None
    bhashini_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    custom_models: Optional[Dict[str, str]] = None
    audit: Optional[AuditInfo] = AuditInfo()


class CommunicationConfig(BaseModel):
    smtp: Optional[SMTPConfig] = None
    sms: Optional[SMSConfig] = None
    in_app: Optional[List[NotificationTemplate]] = None


class UserBasicInfo(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None


class DPOBasicInfo(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None


class UpdateDataFiduciary(BaseModel):
    user_basic_info: Optional[UserBasicInfo] = None
    org_info: Optional[OrgInfo] = None
    communication: Optional[CommunicationConfig] = None
    ai: Optional[AIConfig] = None
    dpo_information: Optional[DPOBasicInfo] = None
