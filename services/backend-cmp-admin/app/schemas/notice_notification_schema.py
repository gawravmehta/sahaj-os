from pydantic import BaseModel
from typing import List, Literal


class NoticeNotification(BaseModel):
    cp_id: str
    sending_medium: List[Literal["email", "sms", "in-app"]]
    dp_tags: List[str] = []
    sms_template_name: str = None
    in_app_template_name: str = None
