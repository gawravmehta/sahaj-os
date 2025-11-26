from typing import List, Optional
from pydantic import BaseModel


class ConsentPurpose(BaseModel):
    purpose_id: Optional[str] = None


class ConsentScope(BaseModel):
    de_id: Optional[str] = None
    consent_purposes: Optional[List[ConsentPurpose]] = None


class UpdateConsent(BaseModel):
    consent_scope: List[ConsentScope] = None
