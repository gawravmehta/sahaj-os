from datetime import UTC, datetime, timedelta
from typing import Union
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_jwt_token(data: dict, expires_delta: Union[int, timedelta] = 15):
    if isinstance(expires_delta, int):
        expire = datetime.now(UTC) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(UTC) + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired JWT token")
