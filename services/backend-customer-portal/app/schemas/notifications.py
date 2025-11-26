from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: str
    artifact_id: str
    data_element_id: str
    data_element_title: str
    purpose_id: str
    purpose_title: str
    expiry_date: datetime
    cp_name: Optional[str] = None
    agreement_id: Optional[str] = None


class NotificationOut(BaseModel):
    id: str = Field(alias="_id")
    dp_id: str
    type: str
    title: str
    message: str
    status: str
    created_at: datetime
    expiry_date: datetime | None = None
    artifact_id: Optional[str] = None
    data_element_id: Optional[str] = None
    data_element_title: Optional[str] = None
    purpose_id: Optional[str] = None
    purpose_title: Optional[str] = None
    cp_name: Optional[str] = None
    agreement_id: Optional[str] = None
    mitigation_steps: Optional[list] = None
    data_elements: Optional[list] = None

    class Config:
        populate_by_name = True

    @classmethod
    def model_validate(cls, data):
        """Convert ObjectId to str before validation"""
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return super().model_validate(data)


class PaginatedNotifications(BaseModel):
    total: int
    page: int
    size: int
    items: List[NotificationOut]
