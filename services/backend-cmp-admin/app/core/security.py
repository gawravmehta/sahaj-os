from datetime import datetime, timedelta, UTC
from typing import Optional
import casbin
from casbin_pymongo_adapter import Adapter
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def match_attribute(request_departments: str, policy_departments: str):
    req_depts = request_departments.split("&")
    pol_depts = policy_departments.split("&")
    return all(dept in req_depts for dept in pol_depts)


rbac_mongo_adapter = Adapter(settings.MONGO_URI, settings.DB_NAME_CONCUR_MASTER, "routes_rbac_policies")


rbac_enforcer = casbin.Enforcer("app/core/rbac/rbac_model.conf", adapter=rbac_mongo_adapter)

rbac_enforcer.enable_auto_save(False)

rbac_enforcer.add_function("match_attribute", match_attribute)
