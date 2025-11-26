from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, EmailStr, Field, GetJsonSchemaHandler
from typing import Annotated
from pydantic.json_schema import JsonSchemaValue


def validate_object_id(v: str | ObjectId) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)


class PyObjectIdMetadata(str):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.update({"type": "string", "example": "60c728a2a9a8d4a9d7b4e7c1"})
        return schema


PyObjectId = Annotated[str, BeforeValidator(validate_object_id), PyObjectIdMetadata]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    df_id: str
    access_token: str
    is_password_reseted: bool
    is_org_configured: bool
    is_invited_user: Optional[bool] = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    df_id: str
    user_roles: List[str]
    is_password_reseted: bool = False
    is_org_configured: bool = False
    is_invited_user: Optional[bool] = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
