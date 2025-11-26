from datetime import datetime
import json
from typing import Literal, Optional, Dict, Any, List
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class WebhookEventInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    webhook_id: str
    df_id: str
    dp_id: str
    payload: Dict[str, Any]
    status: Literal["pending", "sent", "failed"] = "pending"
    attempts: int = 0
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
