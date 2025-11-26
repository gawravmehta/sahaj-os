from typing import List, Optional
from pydantic import BaseModel, EmailStr


class InviteModel(BaseModel):
    invited_user_id: Optional[str] = None
    invited_user_email: EmailStr
    invited_user_name: Optional[str] = None
    invited_user_roles: Optional[List[str]] = []
