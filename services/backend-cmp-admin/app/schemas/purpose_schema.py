from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.utils.common_classes import Pagination, LanguageCodes


class DataElements(BaseModel):
    de_id: str
    de_name: str
    service_mandatory: Optional[bool] = False
    service_message: Optional[str] = None
    legal_mandatory: Optional[bool] = False
    legal_message: Optional[str] = None


class CollectionPoint(BaseModel):
    cp_id: str
    cp_name: str


class PurposeCreate(BaseModel):
    purpose_title: str = Field(..., min_length=4, description="Name shown in notice")
    purpose_description: str = Field(..., description="Name shown in system")
    purpose_category: Optional[str] = None
    purpose_sub_category: Optional[str] = None
    purpose_priority: Literal["low", "medium", "high"]
    review_frequency: Literal["monthly", "quarterly", "half-yearly"]
    consent_time_period: int
    reconsent: bool
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    translations: Optional[Dict[LanguageCodes, str]] = None


class PurposeUpdate(BaseModel):
    purpose_title: Optional[str] = Field(None, min_length=4, description="Name shown in notice")
    purpose_description: Optional[str] = Field(None, description="Name shown in system")
    purpose_priority: Optional[Literal["low", "medium", "high"]] = None
    purpose_category: Optional[str] = None
    purpose_sub_category: Optional[str] = None
    review_frequency: Optional[Literal["monthly", "quarterly", "half-yearly"]] = None
    consent_time_period: Optional[int] = Field(None, gt=0)
    reconsent: Optional[bool] = None
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    translations: Optional[Dict[LanguageCodes, str]] = None


class PurposeInDB(BaseModel):
    purpose_title: str
    purpose_description: str
    purpose_priority: Literal["low", "medium", "high"]
    purpose_category: Optional[str] = None
    purpose_sub_category: Optional[str] = None
    review_frequency: Literal["monthly", "quarterly", "half-yearly"]
    consent_time_period: int = Field(..., gt=0, description="Number of days")
    reconsent: bool
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    translations: Dict[str, Any]
    collection_points: Optional[List[CollectionPoint]] = Field(default_factory=list)
    purpose_status: Optional[Literal["draft", "published", "archived"]] = "draft"
    df_id: str
    created_by: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    purpose_hash_id: Optional[str] = None
    data_processor_details: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class PurposeResponse(PurposeInDB):
    purpose_id: str = Field(..., alias="_id", serialization_alias="purpose_id")


class PurposePaginatedResponse(Pagination):
    purposes: List[PurposeResponse]


class PurposeTemplate(BaseModel):
    purpose_id: str
    industry: str
    sub_category: str
    data_elements: Optional[List[str]] = Field(default_factory=list)
    translations: Dict[str, str]


class PurposeTemplatePaginatedResponse(Pagination):
    purposes: List[PurposeTemplate] = Field(..., validation_alias="data", serialization_alias="purposes")
    model_config = ConfigDict(validate_by_alias=True)
