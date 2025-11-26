from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


class AddDP(BaseModel):
    dp_system_id: str
    dp_identifiers: List[str]
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[int]] = []
    dp_other_identifier: Optional[List[str]] = []
    dp_preferred_lang: Optional[str] = "eng"
    dp_country: Optional[str] = ""
    dp_state: Optional[str] = ""
    dp_tags: Optional[List[str]] = []
    dp_active_devices: Optional[List[str]] = []
    is_active: Optional[bool] = False
    is_legacy: Optional[bool] = True
    created_at_df: datetime
    last_activity: datetime

    @field_validator("dp_preferred_lang", "dp_tags", "dp_country", "dp_state", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("dp_email", "dp_active_devices", mode="before")
    def lowercase_list_fields(cls, v):
        if isinstance(v, list):
            return [item.lower() for item in v if isinstance(item, str)]
        return v

    @field_validator("dp_identifiers", mode="before")
    def validate_identifiers_not_empty(cls, v):
        if not v:
            raise ValueError("dp_identifiers must contain at least one identifier (e.g., 'email' or 'mobile')")
        return v


class UpdateDP(BaseModel):
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[int]] = []
    dp_preferred_lang: Optional[str] = None
    is_legacy: Optional[bool] = None
    is_active: Optional[bool] = None
    dp_country: Optional[str] = None
    dp_state: Optional[str] = None
    dp_tags: Optional[List[str]] = None
    dp_other_identifier: Optional[List[str]] = None
