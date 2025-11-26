import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
import re
from datetime import datetime, UTC
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status

executor = ThreadPoolExecutor(max_workers=10)


def generate_id(prefix: str = "GEN", length: int = 8) -> str:
    """
    Generates a unique ID with a specified prefix and a UUID4-based suffix.

    Args:
        prefix (str): A string prefix for the ID (e.g., "DET" for Data Element Template).
        length (int): The desired length of the UUID part of the ID. Max 32.

    Returns:
        str: The generated unique ID.
    """
    if not 0 < length <= 32:
        raise ValueError("Length for UUID part must be between 1 and 32.")

    unique_suffix = uuid.uuid4().hex[:length].upper()
    return f"{prefix}-{unique_suffix}"


def is_valid_email(email: str) -> bool:
    """
    Checks if a string is a valid email format.

    Args:
        email (str): The email string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """

    email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_regex.match(email))


def get_current_utc_timestamp() -> datetime:
    """
    Returns the current UTC datetime with timezone information.

    Returns:
        datetime: Current UTC datetime.
    """
    return datetime.now(UTC)


def convert_objectid_to_str(obj: Any) -> Any:
    """
    Recursively converts MongoDB ObjectIds in a dictionary or list to strings.
    Useful before returning data from the API if Pydantic's json_encoders isn't catching everything
    or for logging purposes.

    Args:
        obj (Any): The object (dict, list, or other) to process.

    Returns:
        Any: The processed object with ObjectIds converted.
    """
    from bson import ObjectId

    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(elem) for elem in obj]
    else:
        return obj


def validate_object_id(id_str: str) -> ObjectId:
    """
    Validates and returns a MongoDB ObjectId from a string.

    Args:
        id_str (str): The string to validate and convert.

    Returns:
        ObjectId: The valid ObjectId instance.

    Raises:
        ValueError: If the id_str is not a valid ObjectId.
    """

    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid ObjectId format: {id_str}",
        )
    return ObjectId(id_str)


async def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)
