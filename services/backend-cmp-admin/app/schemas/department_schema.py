from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class UserModel(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    designation: Optional[str]
    contact: Optional[int]
    df_id: str
    token: Optional[str]
    is_email_verified: bool
    user_roles: List[str]
    user_departments: List[str]
    user_plan: List[str]
    password: Optional[str]
    created_at: Optional[datetime]


class PaginatedUserResponse(BaseModel):
    data: List[UserModel]
    total_users: int
    current_page: int
    page_size: int
    total_pages: int


class AddDepartment(BaseModel):
    department_name: str
    department_description: str

    @field_validator("department_name", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v


class UpdateDepartmentRequest(BaseModel):
    department_name: Optional[str] = None
    department_description: Optional[str] = None

    @field_validator("department_name", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v


class UpdateDepartmentPermission(BaseModel):
    modules_accessible: List[str] = []
    routes_accessible: List[str] = []
    apis_accessible: List[str] = []


class UpdateDepartmentUsers(BaseModel):
    department_users: List[str] = []
    department_admins: List[str] = []
