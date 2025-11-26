from typing import Optional
from pydantic import BaseModel, Field


class AuthRequestSchema(BaseModel):
    cp_id: str = Field(..., description="Collection Point ID")
    dp_id: Optional[str] = Field(None, description="Data Principal ID")
    dp_e: Optional[str] = Field(None, description="Data Principal Email")
    dp_m: Optional[str] = Field(None, description="Data Principal Phone")
    dp_email: Optional[str] = Field(None, description="Data Principal Email")
    dp_mobile: Optional[str] = Field(None, description="Data Principal Phone")
    pref_lang: Optional[str] = Field(None, description="Language")
