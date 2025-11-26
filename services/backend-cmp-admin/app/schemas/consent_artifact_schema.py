from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PurposeConsentExpiry(BaseModel):
    purpose_id: str
    purpose_title: str
    consent_expiry_period: datetime
    dp_id: str
    df_id: str


class ExpiringConsentsResponse(BaseModel):
    dp_id: str
    expiring_purposes: List[PurposeConsentExpiry]


class ExpiringConsentsByDpIdResponse(BaseModel):
    dp_id: str
    expiring_purposes: List[PurposeConsentExpiry]


class DFAckPayload(BaseModel):
    dp_id: str = Field(..., description="Data Principal ID")
    original_event_type: str = Field(..., description="The event being acknowledged (consent_expired/withdrawn)")
    ack_status: str = Field(..., description="Status of action taken by DF (e.g., HALTED)")
    ack_timestamp: str = Field(..., description="ISO8601 Timestamp of the ACK")
    message: str = Field(None, description="Optional message")
    de_id: str = Field(..., description="Data Element ID")
    purpose_id: str = Field(..., description="Purpose ID")
