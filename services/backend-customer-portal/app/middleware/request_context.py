from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.request_context import set_request

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        set_request(request)
        response = await call_next(request)
        return response
