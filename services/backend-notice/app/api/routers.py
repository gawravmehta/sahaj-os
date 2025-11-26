from fastapi import APIRouter
from app.api.v1.endpoints import authentication, legacy_notice, notice

api_router = APIRouter()

api_router.include_router(authentication.router, prefix="/v1", tags=["Authentication"])
api_router.include_router(notice.router, prefix="/v1/n", tags=["Notice"])
api_router.include_router(legacy_notice.router, prefix="/v1/ln", tags=["Legacy Notice"])
