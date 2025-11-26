from pydantic import BaseModel
from typing import List, Optional


class KYCUploadResponse(BaseModel):
    message: str
    kyc_front_url: str
    kyc_back_url: str
    request_attachment_urls: Optional[List[str]] = None
