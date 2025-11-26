from datetime import datetime
from pydantic import BaseModel, model_validator
from typing import Any, List, Optional


class DPARCreateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    core_identifier: Optional[str] = None
    secondary_identifier: Optional[str] = None
    dp_type: Optional[str] = None
    country: Optional[str] = None
    request_priority: Optional[str] = None
    request_type: Optional[str] = None
    data_element_id: Optional[str] = None
    data_element_updated_value: Optional[str] = None
    request_message: Optional[str] = None
    kyc_document: Optional[str] = None
    related_request: Optional[bool] = False
    related_request_id: Optional[str] = None
    related_request_type: Optional[str] = None

    @model_validator(mode="after")
    def validate_identifiers(self):
        if not self.core_identifier and not self.secondary_identifier:
            raise ValueError("Either core_identifier or secondary_identifier must be provided")
        return self


class DPARRequestResponse(BaseModel):
    dpar_request_id: str
    status: str
    created_timestamp: datetime


class DPARRequestOut(BaseModel):
    dpar_id: str
    dp_id: Optional[str] = None
    status: Optional[str] = None
    created_timestamp: datetime
    last_updated: Optional[datetime] = None
    request_type: Optional[str] = None
    request_priority: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    core_identifier: Optional[str] = None
    secondary_identifier: Optional[str] = None
    dp_type: Optional[str] = None
    country: Optional[str] = None
    request_message: Optional[str] = None
    kyc_document: Optional[str] = None
    kyc_front: Optional[str] = None
    kyc_back: Optional[str] = None
    related_request: Optional[bool | str] = None
    related_request_id: Optional[str] = None
    related_request_type: Optional[str] = None
    request_attachments: Optional[List[Any]] = []
    deadline: Optional[datetime] = None
    is_deleted: Optional[bool] = False


class GetMyRequestsQueryParams(BaseModel):
    core_identifier: Optional[str]
    secondary_identifier: Optional[str]
