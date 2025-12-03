from fastapi import APIRouter
from app.api.v1.endpoints import (
    consent_artifact,
    consent_validation_external,
    consent_validation_internal,
    data_element,
    auth,
    data_fiduciary,
    data_principal,
    departments,
    dp_bulk_external,
    dp_bulk_internal,
    invite,
    notice_notification,
    notifications,
    purpose,
    collection_point,
    assets,
    cookies,
    roles,
    translation,
    vendor,
    grievance,
    dpar,
    webhooks,
    incident_management,
    dashboard,
    consent_audit,
    minio_proxy,
    logs,
)


api_router = APIRouter()

api_router.include_router(minio_proxy.router, prefix="/v1/minio-proxy", tags=["Minio Proxy"])
api_router.include_router(consent_audit.router, prefix="/v1/consent_audit", tags=["Audit"])
api_router.include_router(logs.router, prefix="/v1/business-logs", tags=["Business-logs"])
api_router.include_router(dashboard.router, prefix="/v1/dashboard", tags=["Dashboard"])
api_router.include_router(webhooks.router, prefix="/v1/webhooks", tags=["Webhooks Management"])
api_router.include_router(data_fiduciary.router, prefix="/v1/data-fiduciary", tags=["Data Fiduciary"])
api_router.include_router(roles.router, prefix="/v1/roles", tags=["Roles"])
api_router.include_router(departments.router, prefix="/v1/departments", tags=["Departments"])
api_router.include_router(data_principal.router, prefix="/v1/data-principal", tags=["Data Principal"])
api_router.include_router(dp_bulk_internal.router, prefix="/v1/dp-bulk-internal", tags=["DP Bulk Internal"])
api_router.include_router(dp_bulk_external.router, prefix="/v1/dp-bulk-external", tags=["DP Bulk External"])
api_router.include_router(notice_notification.router, prefix="/v1/notice-notification", tags=["Notice Notification"])
api_router.include_router(consent_validation_internal.router, prefix="/v1/consent-validation", tags=["Consent Validation Internal"])
api_router.include_router(consent_validation_external.router, prefix="/v1/consent-validation", tags=["Consent Validation External"])
api_router.include_router(consent_artifact.router, prefix="/v1/consent-artifact", tags=["Consent Artifact"])
api_router.include_router(vendor.router, prefix="/v1/vendor", tags=["Vendor"])
api_router.include_router(notifications.router, prefix="/v1/notifications", tags=["Notifications"])
api_router.include_router(invite.router, prefix="/v1/invite", tags=["Invite"])
api_router.include_router(assets.router, prefix="/v1/assets", tags=["Assets"])
api_router.include_router(data_element.router, prefix="/v1/data-elements", tags=["Data Elements"])
api_router.include_router(purpose.router, prefix="/v1/purposes", tags=["Purposes"])
api_router.include_router(collection_point.router, prefix="/v1/cp", tags=["Collection Point"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Users"])
api_router.include_router(cookies.router, prefix="/v1/cookie", tags=["Cookies"])
api_router.include_router(translation.router, prefix="/v1/translation", tags=["Translation"])
api_router.include_router(grievance.router, prefix="/v1/grievances", tags=["Grievances"])
api_router.include_router(dpar.router, prefix="/v1/dpar", tags=["DPAR"])
api_router.include_router(incident_management.router, prefix="/v1/incidents", tags=["Incident Management"])
