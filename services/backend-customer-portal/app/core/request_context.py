from contextvars import ContextVar
from fastapi import Request

_request_var: ContextVar[Request | None] = ContextVar("request", default=None)

def set_request(request: Request) -> None:
    """Store the current request in context var."""
    _request_var.set(request)

def get_request() -> Request | None:
    """Get the current request from context var."""
    return _request_var.get()
