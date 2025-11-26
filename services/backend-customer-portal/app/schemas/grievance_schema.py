import re
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator

MOBILE_REGEX = re.compile(r"^\+?\d{10,15}$")


class GrievanceCreateRequest(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    subject: str
    message: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    dp_type: List[
        Literal[
            "Customer",
            "Employee",
            "Platform User",
            "App User",
            "Job Applicant",
            "Marketing Recipient",
            "Nominee",
            "Guardian",
            "Parent",
            "Legal",
        ]
    ]

    @field_validator("mobile_number")
    def validate_mobile(cls, v):
        if v and not MOBILE_REGEX.match(v):
            raise ValueError("Invalid mobile number format")
        return v

    @field_validator("message")
    def validate_message_length(cls, v):
        if len(v.strip()) < 20:
            raise ValueError("Message must be at least 20 characters long")
        return v

    @field_validator("email")
    def validate_contact_fields(cls, v, info):
        values = info.data
        mobile = values.get("mobile_number")
        if not v and not mobile:
            raise ValueError("Either email or mobile_number must be provided")
        return v
