from typing import List
from pydantic import BaseModel


class ConsentPurpose(BaseModel):
    purpose_id: str


class DataElement(BaseModel):
    de_id: str
    consents: List[ConsentPurpose]


class TokenModel(BaseModel):
    token: str
    data_elements: List[DataElement]
