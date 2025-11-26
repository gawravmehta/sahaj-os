from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.utils.common_classes import Pagination, LanguageCodes


class ConsentPurpose(BaseModel):
    purpose_id: str
    purpose_title: str


class DataElements(BaseModel):
    de_id: str
    de_name: str
    purposes: List[ConsentPurpose] = Field(default_factory=list)


class TranslatedAudio(BaseModel):
    audio_url: str
    audio_language: str


class CpCreate(BaseModel):
    cp_name: str
    cp_description: Optional[str] = None
    cp_type: Literal["new", "legacy"] = "new"
    notice_type: Literal["single", "multiple", "layered", "boxed"] = "single"
    redirection_url: str
    fallback_url: Optional[str] = None
    default_language: Optional[str] = "English"
    asset_id: Optional[str] = None
    is_verification_required: Optional[bool] = False
    verification_done_by: Optional[str] = None
    prefered_verification_medium: Optional[str] = None
    notice_popup_window_timeout: Optional[int] = None
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    translated_audio: Optional[List[TranslatedAudio]] = Field(default_factory=list)


class CollectionPointDB(BaseModel):
    cp_name: str
    cp_description: Optional[str] = None
    cp_type: Literal["new", "legacy"]
    notice_type: Literal["single", "multiple", "layered", "boxed"] = "single"
    cp_status: Literal["draft", "published", "archived"] = "draft"
    redirection_url: str
    fallback_url: Optional[str] = None
    default_language: Optional[str] = "English"
    asset_id: Optional[str] = None
    is_verification_required: Optional[bool] = False
    verification_done_by: Optional[str] = None
    prefered_verification_medium: Optional[str] = None
    notice_popup_window_timeout: Optional[int] = None
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    notice_url: str
    is_translation_done: bool = False
    notice_html: str
    df_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    translated_audio: Optional[List[TranslatedAudio]] = Field(default_factory=list)


class CpResponse(CollectionPointDB):
    cp_id: str = Field(..., alias="_id", serialization_alias="cp_id")


class CpPaginatedResponse(Pagination):
    collection_points: List[CpResponse]


class CpUpdate(BaseModel):
    cp_name: Optional[str] = None
    cp_description: Optional[str] = None
    cp_type: Optional[Literal["new", "legacy"]] = None
    notice_type: Optional[Literal["single", "multiple", "layered", "boxed"]] = None
    redirection_url: Optional[str] = None
    fallback_url: Optional[str] = None
    default_language: Optional[str] = "English"
    asset_id: Optional[str] = None
    data_elements: Optional[List[DataElements]] = Field(default_factory=list)
    translated_audio: Optional[List[TranslatedAudio]] = Field(default_factory=list)
