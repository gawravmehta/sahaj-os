from fastapi import APIRouter

from app.api.v1.endpoints import consents, dpar, grievance, kyc, notifications, preferences, auth


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/v1/auth", tags=["Users"])
api_router.include_router(preferences.router, prefix="/v1/preferences", tags=["Preferences"])
api_router.include_router(notifications.router, prefix="/v1/notifications", tags=["Notifications"])
api_router.include_router(consents.router, prefix="/v1/consents", tags=["Consents"])
api_router.include_router(dpar.router, prefix="/v1/dpar", tags=["DPAR"])
api_router.include_router(kyc.router, prefix="/v1/kyc", tags=["KYC"])
api_router.include_router(grievance.router, prefix="/v1/grievance", tags=["Grievance"])
