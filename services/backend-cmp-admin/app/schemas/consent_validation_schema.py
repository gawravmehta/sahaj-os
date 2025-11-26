from typing import List, Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import UTC, datetime


class VerificationRequest(BaseModel):
    dp_id: Optional[str] = None
    dp_system_id: Optional[str] = None
    dp_e: Optional[str] = None
    dp_m: Optional[str] = None
    data_elements_hash: Optional[List[str]] = None
    purpose_hash: Optional[str] = None


class VerificationRecord(BaseModel):
    dp_id: Optional[str] = None
    dp_system_id: Optional[str] = None
    dp_e: Optional[str] = None
    dp_m: Optional[str] = None
    data_elements_hash: List[str] = []
    purpose_hash: Optional[str] = None

    @field_validator("data_elements_hash", mode="before")
    @classmethod
    def validate_data_elements(cls, v):
        if not v or len(v) < 1:
            raise ValueError("At least one data element hash is required")
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_purpose(cls, values):
        if not values.get("purpose_hash"):
            raise ValueError("purpose_hash is required")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_identifiers(cls, values):
        identifiers_provided = any(
            [
                values.get("dp_id"),
                values.get("dp_system_id"),
                values.get("dp_e"),
                values.get("dp_m"),
            ]
        )
        if not identifiers_provided:
            raise ValueError("At least one DP identifier is required")
        return values


class VerificationResult(BaseModel):
    record: VerificationRecord
    verified: bool
    consented_data_elements: List[str] = []
    verification_request_id: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
