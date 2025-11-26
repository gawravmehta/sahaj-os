from pydantic import BaseModel
from typing import List, Literal, Optional


class AddRole(BaseModel):
    role_name: str
    role_description: Optional[str] = None


class UpdateRoleUser(BaseModel):
    users_list: list


class AssignRolesToUser(BaseModel):
    roles_list: List[str]


class RoutePermission(BaseModel):
    path: str
    actions: List[Literal["read", "write"]] = []


class UpdateRolePermissions(BaseModel):
    routes_accessible: List[RoutePermission] = []


class UpdateRole(BaseModel):
    role_name: Optional[str] = None
    role_description: Optional[str] = None
