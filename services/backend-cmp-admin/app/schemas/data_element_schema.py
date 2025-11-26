from typing import Annotated, Optional, List, Dict, Any, Literal
from datetime import timezone, datetime
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from enum import Enum
from app.utils.common_classes import Pagination, LanguageCodes


def validate_object_id(v: str | ObjectId) -> str:
    """Validator to ensure ObjectId is valid and returns it as string."""
    if isinstance(v, ObjectId):
        return str(v)
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)


class PyObjectIdMetadata(str):
    """For OpenAPI schema docs."""

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.update({"type": "string", "example": "60c728a2a9a8d4a9d7b4e7c1"})
        return schema


PyObjectId = Annotated[str, BeforeValidator(validate_object_id), PyObjectIdMetadata]


class CollectionPoint(BaseModel):
    cp_id: str
    cp_name: str


class ConsentPurpose(BaseModel):
    purpose_id: str
    purpose_name: str


class DETemplateOut(BaseModel):
    id: str
    title: str
    description: str
    aliases: List[str]
    domain: str
    translations: Dict[str, str]


class DETemplatePaginatedResponse(Pagination):
    data_elements: List[DETemplateOut] = Field(..., validation_alias="data", serialization_alias="data_elements")

    model_config = ConfigDict(validate_by_alias=True)


class DataElementCreate(BaseModel):
    de_name: str = Field(..., description="Name shown in system")
    de_description: str
    de_original_name: str = Field(..., description="Name shown in notice")
    de_data_type: Literal["string", "number", "boolean", "date"] = Field(..., description="Data element data type stored with df")
    de_sensitivity: Literal["high", "medium", "low"]
    is_core_identifier: bool
    de_retention_period: int = Field(..., gt=0, description="Number of days")
    translations: Optional[Dict[LanguageCodes, str]] = None


class DataElementUpdate(BaseModel):
    de_name: Optional[str] = Field(None, min_length=2)
    de_description: Optional[str] = None
    de_original_name: Optional[str] = None
    de_data_type: Optional[Literal["string", "number", "boolean", "date"]] = None
    de_sensitivity: Optional[Literal["high", "medium", "low"]] = None
    is_core_identifier: Optional[bool] = None
    de_retention_period: Optional[int] = Field(None, gt=0)
    translations: Optional[Dict[LanguageCodes, str]] = None
    collection_points: Optional[List[CollectionPoint]] = Field(default_factory=list)
    purposes: Optional[List[ConsentPurpose]] = Field(default_factory=list)


class DataElementDB(BaseModel):
    de_name: str = Field(..., description="Name shown in system")
    de_description: str
    de_original_name: str = Field(..., description="Name shown in notice")
    de_data_type: Literal["string", "number", "boolean", "date"] = Field(..., description="Data element data type stored with df")
    de_sensitivity: Literal["high", "medium", "low"]
    is_core_identifier: bool
    de_retention_period: int = Field(..., gt=0, description="Number of days")
    de_status: Optional[Literal["draft", "published", "archived"]] = "draft"
    translations: Dict[str, Any]
    collection_points: Optional[List[CollectionPoint]] = Field(default_factory=list)
    purposes: Optional[List[ConsentPurpose]] = Field(default_factory=list)
    df_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    de_hash_id: Optional[str] = None


class DataElementResponse(DataElementDB):
    de_id: str = Field(..., alias="_id", serialization_alias="de_id")


class DEPaginatedResponse(Pagination):
    data_elements: List[DataElementResponse]
