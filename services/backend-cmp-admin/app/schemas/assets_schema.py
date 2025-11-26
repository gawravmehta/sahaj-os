from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.utils.common_classes import Pagination


class MetaCookies(BaseModel):
    scan_frequency: Optional[Literal["manual", "daily", "weekly"]] = Field(
        default="manual", description="Frequency of cookie scans (manual/daily/weekly)"
    )
    next_scan_date: Optional[datetime] = Field(default=None, description="Next scheduled scan date")
    scan_status: Optional[Literal["pending", "running", "failed", "completed"]] = Field(
        default="pending", description="Status of last scan: pending/running/completed/failed"
    )
    cookies_count: Optional[int] = Field(default=0, description="Total cookies found during last scan")
    script_url: Optional[str] = Field(default=None, description="URL of the deployed cookie consent widget script")


class AssetCategory(str, Enum):
    CTV = "CTV (Connected TV)"
    WEARABLE_TECHNOLOGY = "Wearable Technology"
    VEHICLES = "Vehicles"
    BIOMETRIC_SYSTEMS = "Biometric Systems"
    MOBILE = "Mobile"
    WEBSITE = "Website"
    POINT_OF_SALE = "Point of Sale"
    HARDWARE = "Hardware"
    IOT = "IoT"
    HEALTH = "Health"


class AssetCreate(BaseModel):
    asset_name: str
    category: AssetCategory
    description: Optional[str] = None
    image: Optional[str] = None
    asset_status: Optional[Literal["draft", "published", "archived"]] = "draft"
    usage_url: str


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    category: Optional[AssetCategory] = None
    description: Optional[str] = None
    image: Optional[str] = None
    asset_status: Optional[Literal["draft", "published", "archived"]] = "draft"
    usage_url: Optional[str] = None


class AssetInDB(BaseModel):
    asset_name: str
    category: AssetCategory
    description: Optional[str] = None
    image: Optional[str] = None
    asset_status: Optional[Literal["draft", "published", "archived"]] = "draft"
    usage_url: str
    df_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class AssetResponse(AssetInDB):
    asset_id: str = Field(..., alias="_id", serialization_alias="asset_id")
    meta_cookies: Optional[MetaCookies] = None


class AssetPaginatedResponse(Pagination):
    assets: List[AssetResponse]


class LogStatistics(BaseModel):
    total_logs: int
    errors: int
    warnings: int
    info: int


class LogFilters(BaseModel):
    events: List[str]
    user_emails: List[str]


class LogPaginationMeta(BaseModel):
    current_page: int
    data_per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class BusinessLogsResponse(BaseModel):
    statistics: LogStatistics
    available_filters: LogFilters
    pagination: LogPaginationMeta
    logs: List[dict]
