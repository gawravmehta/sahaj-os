from enum import Enum
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.utils.common_classes import Pagination, LanguageCodes


class CookieCategory(str, Enum):
    ESSENTIAL = "essential"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UNKNOWN = "unknown"


class CookieCreate(BaseModel):
    cookie_name: str = Field(..., description="The name of the cookie, e.g., 'session_id'.")
    description: Optional[str] = Field(None, description="A brief explanation of the cookie's purpose.")
    hostname: str = Field(..., description="The domain the cookie is set on, e.g., 'example.com'.")
    category: CookieCategory = Field(..., description="The classification category, using a standardized Enum.")
    lifespan: Optional[str] = Field(None, description="The cookie's lifespan (e.g., 'session' or '30 days').")
    path: Optional[str] = Field("/", description="The path for which the cookie is valid.")
    http_only: Optional[bool] = Field(None, description="Indicates if the cookie is accessible only via HTTP.")
    secure: Optional[bool] = Field(None, description="Indicates if the cookie is sent only over secure channels (HTTPS).")
    same_site: Optional[str] = Field(None, description="The SameSite attribute of the cookie.")
    is_third_party: Optional[bool] = Field(None, description="Indicates if the cookie is set by a third party.")
    cookie_status: Literal["draft", "published", "archived"] = Field(..., description="The status of the cookie.")
    translations: Optional[Dict[LanguageCodes, str]] = None


class CookieInDB(BaseModel):
    cookie_name: str
    description: Optional[str] = None
    hostname: str
    category: CookieCategory
    lifespan: Optional[str] = None
    path: Optional[str] = None
    http_only: Optional[bool] = None
    secure: Optional[bool] = None
    same_site: Optional[str] = None
    is_third_party: Optional[bool] = None
    cookie_status: Literal["draft", "published", "archived"]
    translations: Optional[Dict[LanguageCodes, str]] = None

    source: Optional[Literal["manual", "scan"]] = "manual"
    expiry: Optional[datetime] = Field(None, description="The calculated expiry date of the cookie.")
    website_id: str = Field(..., description="The ID of the website this cookie belongs to.")
    df_id: str = Field(..., description="The data flow ID associated with the user.")
    created_by: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = Field(None, description="The timestamp when the cookie entry was last updated.")


class CookieResponse(CookieInDB):
    cookie_id: str = Field(..., alias="_id", serialization_alias="cookie_id")


class CookieUpdate(BaseModel):
    cookie_name: Optional[str] = None
    description: Optional[str] = None
    hostname: Optional[str] = None
    category: Optional[CookieCategory] = None
    lifespan: Optional[str] = None
    path: Optional[str] = None
    http_only: Optional[bool] = None
    secure: Optional[bool] = None
    same_site: Optional[str] = None
    is_third_party: Optional[bool] = None
    cookie_status: Optional[Literal["draft", "published", "archived"]] = None
    translations: Optional[Dict[LanguageCodes, str]] = None


class CookiesPaginatedResponse(Pagination):
    cookies: List[CookieResponse]
