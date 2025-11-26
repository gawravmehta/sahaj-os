from typing import List, Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, Field, model_validator
from app.utils.common_classes import ConsentEvent


class AuthConfig(BaseModel):
    type: Literal["header", "query", "none"] = "none"
    key: Optional[str] = "X-Consent-Signature"
    secret: Optional[str] = None


class RetryPolicy(BaseModel):
    max_retries: int = 3
    retry_interval_sec: int = 10
    backoff_strategy: Literal["exponential", "fixed", "none"] = "exponential"


class WebhookMetrics(BaseModel):
    delivered: int = 0
    failed: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


class WebhookCreate(BaseModel):
    url: HttpUrl
    webhook_for: Literal["df", "dpr"] = "df"
    dpr_id: Optional[str] = None
    environment: Literal["testing", "production"] = "testing"

    @model_validator(mode="before")
    def check_dpr_id_if_needed(cls, values):
        webhook_for = values.get("webhook_for")
        dpr_id = values.get("dpr_id")
        if webhook_for == "dpr" and not dpr_id:
            raise ValueError("dpr_id is required when webhook_for is 'dpr'")
        return values


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    webhook_for: Optional[Literal["df", "dpr"]] = None
    dpr_id: Optional[str] = None
    environment: Optional[Literal["testing", "production"]] = None
    status: Optional[Literal["active", "inactive", "archived"]] = None

    @model_validator(mode="before")
    def check_dpr_id_if_needed(cls, values):
        webhook_for = values.get("webhook_for")
        dpr_id = values.get("dpr_id")
        if webhook_for == "dpr" and not dpr_id:
            raise ValueError("dpr_id is required when webhook_for is 'dpr'")
        return values


class WebhookInDB(BaseModel):
    url: str
    subscribed_events: List[str] = Field(default_factory=lambda: [e.value for e in ConsentEvent])
    webhook_for: Literal["df", "dpr"]
    dpr_id: Optional[str] = None
    environment: Literal["testing", "production"] = "testing"
    df_id: str
    status: Literal["active", "inactive", "archived"] = "inactive"
    auth: AuthConfig
    retry_policy: RetryPolicy
    metrics: WebhookMetrics = Field(default_factory=WebhookMetrics)
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="before")
    def check_dpr_id_if_needed(cls, values):
        webhook_for = values.get("webhook_for")
        dpr_id = values.get("dpr_id")
        if webhook_for == "dpr" and not dpr_id:
            raise ValueError("dpr_id is required when webhook_for is 'dpr'")
        return values


class WebhookOut(BaseModel):
    url: str
    subscribed_events: List[str]
    webhook_for: Literal["df", "dpr"]
    dpr_id: Optional[str] = None
    environment: Literal["testing", "production"] = "testing"
    df_id: str
    status: Literal["active", "inactive", "archived"] = "active"
    auth: AuthConfig
    retry_policy: RetryPolicy
    metrics: WebhookMetrics
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookResponse(WebhookOut):
    webhook_id: str = Field(..., alias="_id", serialization_alias="webhook_id")


class WebhookPaginatedResponse(BaseModel):
    current_page: int
    data_per_page: int
    total_items: int
    total_pages: int
    webhooks: List[WebhookResponse]
