from enum import Enum
import re
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator
from typing import Dict, List, Optional
import uuid
from datetime import datetime, UTC


class DPARCreateRequest(BaseModel):
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    core_identifier: Optional[str] = Field(None, description="Core identifier")
    secondary_identifier: Optional[str] = Field(None, description="Secondary identifier")
    dp_type: Optional[str] = Field(None, description="Data Processing type")
    country: Optional[str] = None
    request_priority: Optional[str] = None
    request_type: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    kyc_document: Optional[str] = None
    related_request: Optional[str] = None
    related_request_type: Optional[str] = None

    @model_validator(mode="after")
    def validate_identifiers(self):
        if not self.core_identifier and not self.secondary_identifier:
            raise ValueError("Either core_identifier or secondary_identifier must be provided")
        return self


class DPARResponse(BaseModel):
    dpar_request_id: str
    status: str
    created_timestamp: datetime


class ClarificationModel(BaseModel):
    clarification_type: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    deadline: Optional[str] = None
    action: Optional[str] = None


class ReportTypeEnum(str, Enum):
    message = "message"
    acknowledgement = "acknowledgement"
    completion = "completion"
    request = "request"
    rejection = "rejection"


class SendToEnum(str, Enum):
    core = "core"
    secondary = "secondary"


class DPARReportCreate(BaseModel):
    report_type: ReportTypeEnum
    template_id: str
    send_to: SendToEnum
    subject: str
    message: str


class RemindersModel(BaseModel):
    """Reminders configuration for deadlines"""

    reminder_1: Optional[Dict] = {}
    reminder_2: Optional[Dict] = {}


class KycDeadlineModel(BaseModel):
    """Deadline settings for KYC verification"""

    deadline_for_kyc: str
    kyc_reminders: RemindersModel

    @field_validator("deadline_for_kyc")
    def check_deadline_for_kyc(cls, v: str) -> str:
        """
        Validate that deadline_for_kyc is in the correct format (e.g., 'n days', 'n weeks', etc.).
        """
        pattern = r"^\d+\s(day|week|month|year)s?$"
        if not re.match(pattern, v, re.IGNORECASE):
            raise ValueError("deadline_for_kyc must be in the format 'n days', 'n weeks', 'n months', or 'n years'")
        return v

    @computed_field
    @property
    def deadline_seconds(self) -> int:
        """
        Convert deadline_for_kyc into seconds.
        """
        num, unit = self.deadline_for_kyc.split()
        num = int(num)
        unit = unit.lower()
        ans = 0

        if unit.startswith("day"):
            ans = num * 86400
        elif unit.startswith("week"):
            ans = num * 604800
        elif unit.startswith("month"):
            ans = num * 2592000
        elif unit.startswith("year"):
            ans = num * 31536000

        if ans < 604800:
            raise ValueError("deadline_for_kyc must be at least 7 days")

        return ans


class ClarificationDeadlineModel(BaseModel):
    """Deadline & reminders for clarification"""

    clarification_reminders: RemindersModel


class KycIdentifierEnum(str, Enum):
    """Allowed KYC identifiers"""

    AADHAR = "aadhar_card"
    PAN = "pan_card"
    DRIVING_LICENSE = "driving_license"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"
    RATION_CARD = "ration_card"


class DparEmailRulesModel(BaseModel):
    """Rules related to email notifications (dummy for now, expand as needed)"""

    send_email_on_creation: bool = True
    send_email_on_completion: bool = True
    escalation_emails: Optional[List[str]] = []


class DparRulesModel(BaseModel):
    """
    Settings for DF’s DPAR rules
    """

    email_rules: DparEmailRulesModel
    kyc_identifiers: List[KycIdentifierEnum]
    kyc_deadline: KycDeadlineModel
    clarification_deadline: ClarificationDeadlineModel
    dpar_default_deadline: int
