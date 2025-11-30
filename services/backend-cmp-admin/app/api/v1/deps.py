import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from bson import ObjectId
from typing import Optional

from app.core.config import settings
from app.db.session import get_s3_client
from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from app.crud.consent_audit_crud import ConsentAuditCRUD
from app.crud.consent_validation_crud import ConsentValidationCRUD
from app.crud.data_principal_crud import DataPrincipalCRUD
from app.crud.department_crud import DepartmentCRUD
from app.crud.invite_crud import InviteCRUD
from app.crud.notice_notification_crud import NoticeNotificationCRUD
from app.crud.notification_crud import NotificationCRUD
from app.crud.role_crud import RoleCRUD
from app.crud.vendor_crud import VendorCRUD
from app.db.dependencies import (
    get_asset_collection,
    get_business_logs_collection,
    get_concur_master_db,
    get_consent_artifact_collection,
    get_consent_audit_collection,
    get_consent_purpose_collection,
    get_consent_validation_collection,
    get_consent_validation_files_collection,
    get_cp_master_collection,
    get_customer_notifications_collection,
    get_de_master_collection,
    get_de_master_translated_collection,
    get_de_template_collection,
    get_departments_collection,
    get_df_register_collection,
    get_notice_notification_collection,
    get_notifications_collection,
    get_purpose_master_translated_collection,
    get_purpose_template_collection,
    get_cookie_master,
    get_roles_collection,
    get_user_collection,
    get_user_invites_collection,
    get_vendor_collection,
    get_grievance_collection,
    get_dpar_collection,
    get_dpar_preflight_collection,
    get_dpar_rules_collection,
    get_dpar_settings_collection,
    get_dpar_report_collection,
    get_dpar_bulk_upload_collection,
    get_webhook_events_crud,
    get_webhooks_collection,
    get_incident_management_collection,
    get_df_keys_collection,
)
from app.crud.user_crud import UserCRUD
from app.db.session import get_postgres_pool
from app.schemas.auth_schema import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.crud.data_element_crud import DataElementCRUD
from app.crud.purpose_crud import PurposeCRUD
from app.crud.collection_point_crud import CollectionPointCrud
from app.crud.assets_crud import AssetCrud
from app.crud.cookie_crud import CookieCrud
from app.services.auth_service import AuthService
from app.services.consent_artifact_service import ConsentArtifactService
from app.services.consent_audit_service import ConsentAuditService
from app.services.consent_validation_service import ConsentValidationService
from app.services.dashboard_service import DashboardService
from app.services.data_element_service import DataElementService
from app.services.data_principal_service import DataPrincipalService
from app.services.department_service import DepartmentService
from app.services.invite_service import InviteService
from app.services.notice_notification_service import NoticeNotificationService
from app.services.notification_service import NotificationService
from app.services.purpose_service import PurposeService
from app.services.collection_point_service import CollectionPointService
from app.services.assets_service import AssetService
from app.services.notice_service import NoticeService
from app.services.cookie_scan_service import CookieScanService
from app.services.cookie_service import CookieManagementService
from app.services.cookie_widget_service import WidgetService
from app.services.role_service import RoleService
from app.services.translation_service import TranslationService
from app.services.data_fiduciary_service import DataFiduciaryService
from app.crud.data_fiduciary_crud import DataFiduciaryCRUD
from app.services.vendor_service import VendorService
from app.crud.grievance_crud import GrievanceCRUD
from app.services.grievance_service import GrievanceService
from app.crud.dpar_crud import DparCRUD
from app.services.dpar_service import DPARequestService
from app.services.webhooks_service import WebhooksService
from app.crud.webhooks_crud import WebhooksCrud
from app.crud.webhook_events_crud import WebhookEventCRUD
from app.crud.incident_management_crud import IncidentCRUD
from app.services.incident_management_service import IncidentService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_user_crud_for_deps(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
) -> UserCRUD:
    users_collection = db["cmp_users"]
    return UserCRUD(users_collection)


async def get_data_element_crud(
    de_template_collection: AsyncIOMotorCollection = Depends(get_de_template_collection),
    de_master_collection: AsyncIOMotorCollection = Depends(get_de_master_collection),
    de_master_translated_collection: AsyncIOMotorCollection = Depends(get_de_master_translated_collection),
) -> DataElementCRUD:
    return DataElementCRUD(de_template_collection, de_master_collection, de_master_translated_collection)


async def get_data_element_service(
    crud: DataElementCRUD = Depends(get_data_element_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> DataElementService:
    return DataElementService(crud, business_logs_collection)


async def get_purpose_crud(
    purpose_template_collection: AsyncIOMotorCollection = Depends(get_purpose_template_collection),
    purpose_master_collection: AsyncIOMotorCollection = Depends(get_consent_purpose_collection),
    purpose_master_translated_collection: AsyncIOMotorCollection = Depends(get_purpose_master_translated_collection),
) -> PurposeCRUD:
    return PurposeCRUD(
        purpose_template_collection,
        purpose_master_collection,
        purpose_master_translated_collection,
    )


async def get_purpose_service(
    crud: PurposeCRUD = Depends(get_purpose_crud),
    data_element_service: DataElementService = Depends(get_data_element_service),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> PurposeService:
    return PurposeService(crud, data_element_service, business_logs_collection)


async def get_notice_service():
    supported_languages_map = {
        "eng": "English",
        "asm": "Assamese",
        "mni": "Manipuri",
        "nep": "Nepali",
        "san": "Sanskrit",
        "urd": "Urdu",
        "hin": "Hindi",
        "mai": "Maithili",
        "tam": "Tamil",
        "mal": "Malayalam",
        "ben": "Bengali",
        "kok": "Konkani",
        "guj": "Gujarati",
        "kan": "Kannada",
        "snd": "Sindhi",
        "ori": "Odia",
        "sat": "Santali",
        "pan": "Punjabi",
        "mar": "Marathi",
        "tel": "Telugu",
        "kas": "Kashmiri",
        "brx": "Bodo",
    }

    STATIC_JSON_FILE = "app/constants/notice_static.json"
    CATEGORIES_TRANSLATION_FILE = "app/constants/category_trans.json"

    return NoticeService(
        supported_languages_map=supported_languages_map, static_json_file=STATIC_JSON_FILE, categories_translation_file=CATEGORIES_TRANSLATION_FILE
    )


async def get_translation_service(
    df_register_collection: AsyncIOMotorCollection = Depends(get_df_register_collection),
) -> TranslationService:
    return TranslationService(df_register_collection=df_register_collection)


async def get_cp_crud(
    cp_master: AsyncIOMotorCollection = Depends(get_cp_master_collection),
) -> CollectionPointCrud:
    return CollectionPointCrud(cp_master)


def get_df_crud(
    df_register_collection=Depends(get_df_register_collection),
) -> DataFiduciaryCRUD:
    return DataFiduciaryCRUD(df_register_collection)


def get_data_fiduciary_service(
    crud: DataFiduciaryCRUD = Depends(get_df_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    df_keys_collection: AsyncIOMotorCollection = Depends(get_df_keys_collection),
) -> DataFiduciaryService:
    return DataFiduciaryService(crud, business_logs_collection, user_collection, df_keys_collection)


async def get_cp_service(
    crud: CollectionPointCrud = Depends(get_cp_crud),
    data_element_service: DataElementService = Depends(get_data_element_service),
    purpose_service: PurposeService = Depends(get_purpose_service),
    notice_service: NoticeService = Depends(get_notice_service),
    data_fiduciary_service: DataFiduciaryService = Depends(get_data_fiduciary_service),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> CollectionPointService:

    return CollectionPointService(
        crud=crud,
        data_element_service=data_element_service,
        purpose_service=purpose_service,
        notice_service=notice_service,
        data_fiduciary_service=data_fiduciary_service,
        business_logs_collection=business_logs_collection,
    )


async def get_asset_crud(
    asset_master: AsyncIOMotorCollection = Depends(get_asset_collection),
) -> AssetCrud:
    return AssetCrud(asset_master)


async def get_asset_service(
    crud: AssetCrud = Depends(get_asset_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> AssetService:
    return AssetService(
        crud=crud,
        business_logs_collection=business_logs_collection,
    )


async def get_cookie_crud(
    cookie_master: AsyncIOMotorCollection = Depends(get_cookie_master),
) -> CookieCrud:
    return CookieCrud(cookie_master)


async def get_cookie_scan_service(
    df_register_collection: AsyncIOMotorCollection = Depends(get_df_register_collection),
) -> CookieScanService:
    return CookieScanService(df_register_collection=df_register_collection)


async def get_cookie_service(
    crud: CookieCrud = Depends(get_cookie_crud),
    asset_service: AssetService = Depends(get_asset_service),
    cookie_scan_service: CookieScanService = Depends(get_cookie_scan_service),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> CookieManagementService:
    return CookieManagementService(
        crud=crud,
        asset_service=asset_service,
        cookie_scan_service=cookie_scan_service,
        business_logs_collection=business_logs_collection,
    )


async def get_widget_service(
    cookie_service: CookieManagementService = Depends(get_cookie_service),
    df_service: DataFiduciaryService = Depends(get_data_fiduciary_service),
) -> WidgetService:
    return WidgetService(
        cookie_service=cookie_service,
        df_service=df_service,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_crud: UserCRUD = Depends(get_user_crud_for_deps),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_doc = await user_crud.get_user_by_id(ObjectId(user_id))

        if user_doc.df_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have an assigned df_id")

        return {"_id": str(user_doc.id), "email": user_doc.email, "user_roles": user_doc.user_roles, "df_id": user_doc.df_id}

    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred during user authentication: {e}",
        )


async def get_user_crud(
    users_collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> UserCRUD:

    return UserCRUD(users_collection)


async def get_auth_service(
    user_crud: UserCRUD = Depends(get_user_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    df_register_collection: AsyncIOMotorCollection = Depends(get_df_register_collection),
) -> AuthService:

    return AuthService(user_crud, business_logs_collection, user_collection, df_register_collection)


async def get_role_crud(
    roles_collection: AsyncIOMotorCollection = Depends(get_roles_collection),
) -> RoleCRUD:
    return RoleCRUD(roles_collection)


async def get_role_service(
    db: AsyncIOMotorDatabase = Depends(get_concur_master_db),
    role_crud: RoleCRUD = Depends(get_role_crud),
    user_crud: UserCRUD = Depends(get_user_crud),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> RoleService:

    return RoleService(role_crud, user_crud, user_collection, business_logs_collection)


async def get_invite_crud(
    invite_collection: AsyncIOMotorCollection = Depends(get_user_invites_collection),
) -> InviteCRUD:
    return InviteCRUD(invite_collection)


async def get_invites_service(
    user_crud: UserCRUD = Depends(get_user_crud),
    role_crud: RoleCRUD = Depends(get_role_crud),
    invite_crud: InviteCRUD = Depends(get_invite_crud),
    df_crud: DataFiduciaryCRUD = Depends(get_df_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
    df_register_collection: AsyncIOMotorCollection = Depends(get_df_register_collection),
) -> InviteService:

    return InviteService(user_crud, role_crud, invite_crud, df_crud, business_logs_collection, df_register_collection)


async def get_department_crud(
    department_collection: AsyncIOMotorCollection = Depends(get_departments_collection),
) -> DepartmentCRUD:
    return DepartmentCRUD(department_collection)


async def get_department_service(
    department_crud: DepartmentCRUD = Depends(get_department_crud),
    user_crud: UserCRUD = Depends(get_user_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> DepartmentService:

    return DepartmentService(department_crud, user_crud, business_logs_collection)


async def get_data_principal_crud(pool: asyncpg.Pool = Depends(get_postgres_pool)) -> DataPrincipalCRUD:
    return DataPrincipalCRUD(pool)


async def get_data_principal_service(
    data_principal_crud: DataPrincipalCRUD = Depends(get_data_principal_crud),
    consent_latest_artifacts: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> DataPrincipalService:
    return DataPrincipalService(data_principal_crud, consent_latest_artifacts, business_logs_collection)


async def get_notification_crud(
    notification_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
) -> NotificationCRUD:
    return NotificationCRUD(notification_collection)


async def get_notification_service(
    crud: NotificationCRUD = Depends(get_notification_crud),
) -> NotificationService:
    return NotificationService(crud)


async def get_vendor_crud(
    vendor_collection: AsyncIOMotorCollection = Depends(get_vendor_collection),
    purpose_collection: AsyncIOMotorCollection = Depends(get_consent_purpose_collection),
) -> VendorCRUD:
    return VendorCRUD(vendor_collection, purpose_collection)


async def get_vendor_service(
    crud: VendorCRUD = Depends(get_vendor_crud),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> VendorService:
    return VendorService(crud, user_collection, business_logs_collection)


async def get_consent_artifact_crud(
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
) -> ConsentArtifactCRUD:
    return ConsentArtifactCRUD(consent_artifact_collection)


async def get_consent_artifact_service(
    crud: ConsentArtifactCRUD = Depends(get_consent_artifact_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> ConsentArtifactService:
    return ConsentArtifactService(crud, business_logs_collection)


async def get_consent_audit_crud(
    consent_audit_collection: AsyncIOMotorCollection = Depends(get_consent_audit_collection),
) -> ConsentAuditCRUD:
    return ConsentAuditCRUD(consent_audit_collection)


async def get_public_key_pem() -> str:
    return settings.PUBLIC_KEY_PEM


async def get_consent_audit_service(
    crud: ConsentAuditCRUD = Depends(get_consent_audit_crud),
    public_key_pem: str = Depends(get_public_key_pem),
):
    return ConsentAuditService(crud=crud, public_key_pem=public_key_pem)


async def get_consent_validation_crud(
    consent_validation_collection: AsyncIOMotorCollection = Depends(get_consent_validation_collection),
    consent_validation_files_collection: AsyncIOMotorCollection = Depends(get_consent_validation_files_collection),
) -> ConsentValidationCRUD:
    return ConsentValidationCRUD(consent_validation_collection, consent_validation_files_collection)


async def get_consent_validation_service(
    consent_validation_crud: ConsentValidationCRUD = Depends(get_consent_validation_crud),
    consent_artifact_crud: ConsentArtifactCRUD = Depends(get_consent_artifact_crud),
    vendor_crud: VendorCRUD = Depends(get_vendor_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> ConsentValidationService:
    return ConsentValidationService(consent_validation_crud, consent_artifact_crud, vendor_crud, business_logs_collection)


async def get_grievance_crud(
    grievance_collection: AsyncIOMotorCollection = Depends(get_grievance_collection),
) -> GrievanceCRUD:
    return GrievanceCRUD(grievance_collection)


async def get_grievance_service(
    crud: GrievanceCRUD = Depends(get_grievance_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
    customer_notification_collection: AsyncIOMotorCollection = Depends(get_customer_notifications_collection),
) -> GrievanceService:
    return GrievanceService(crud, business_logs_collection, customer_notification_collection)


async def get_notice_notification_crud(
    notice_notification_collection: AsyncIOMotorCollection = Depends(get_notice_notification_collection),
    pool: asyncpg.Pool = Depends(get_postgres_pool),
) -> NoticeNotificationCRUD:
    return NoticeNotificationCRUD(notice_notification_collection, pool)


async def get_notice_notification_service(
    crud: NoticeNotificationCRUD = Depends(get_notice_notification_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> NoticeNotificationService:
    return NoticeNotificationService(crud, business_logs_collection)


async def get_dpar_crud(
    dpar_collection: AsyncIOMotorCollection = Depends(get_dpar_collection),
    dpar_report_collection: AsyncIOMotorCollection = Depends(get_dpar_report_collection),
    dpar_bulk_upload_collection: AsyncIOMotorCollection = Depends(get_dpar_bulk_upload_collection),
) -> DparCRUD:
    return DparCRUD(dpar_collection, dpar_report_collection, dpar_bulk_upload_collection)


async def get_dpar_service(
    crud: DparCRUD = Depends(get_dpar_crud),
    s3_client=Depends(get_s3_client),
    bucket_name: str = Depends(lambda: settings.UNPROCESSED_VERIFICATION_FILES_BUCKET),
    user_collection=Depends(get_user_collection),
    consent_artifact_crud=Depends(get_consent_artifact_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> DPARequestService:
    return DPARequestService(
        crud,
        user_collection,
        s3_client,
        bucket_name,
        consent_artifact_crud,
        business_logs_collection,
    )


async def get_webhooks_crud(
    webhooks_collection: AsyncIOMotorCollection = Depends(get_webhooks_collection),
) -> WebhooksCrud:
    return WebhooksCrud(webhooks_collection)


async def get_webhooks_service(
    crud: WebhooksCrud = Depends(get_webhooks_crud),
    webhookevent_crud=Depends(get_webhook_events_crud),
    business_logs_collection: str = Depends(get_business_logs_collection),
) -> WebhooksService:
    return WebhooksService(crud, business_logs_collection, webhook_event_crud=webhookevent_crud)


async def get_incident_crud(
    incident_collection: AsyncIOMotorCollection = Depends(get_incident_management_collection),
) -> IncidentCRUD:
    return IncidentCRUD(incident_collection)


async def get_incident_service(
    crud: IncidentCRUD = Depends(get_incident_crud),
    user_collection=Depends(get_user_collection),
    business_logs_collection: str = Depends(get_business_logs_collection),
    data_principal_service: DataPrincipalService = Depends(get_data_principal_service),
    customer_notifications_collection: AsyncIOMotorCollection = Depends(get_customer_notifications_collection),
) -> IncidentService:
    return IncidentService(
        crud,
        user_collection,
        business_logs_collection,
        data_principal_service,
        customer_notifications_collection,
    )


async def get_dashboard_service(
    departments_crud: DepartmentCRUD = Depends(get_department_crud),
    roles_crud: RoleCRUD = Depends(get_role_crud),
    users_crud: UserCRUD = Depends(get_user_crud),
    assets_crud: AssetCrud = Depends(get_asset_crud),
    data_principal_crud: DataPrincipalCRUD = Depends(get_data_principal_crud),
    data_elements_crud: DataElementCRUD = Depends(get_data_element_crud),
    purposes_crud: PurposeCRUD = Depends(get_purpose_crud),
    collection_points_crud: CollectionPointCrud = Depends(get_cp_crud),
    grievance_crud: GrievanceCRUD = Depends(get_grievance_crud),
    dpar_crud: DparCRUD = Depends(get_dpar_crud),
    vendor_crud: VendorCRUD = Depends(get_vendor_crud),
    consent_artifact_crud: ConsentArtifactCRUD = Depends(get_consent_artifact_crud),
    consent_artifact_service: ConsentArtifactService = Depends(get_consent_artifact_service),
) -> DashboardService:
    return DashboardService(
        departments_crud,
        roles_crud,
        users_crud,
        assets_crud,
        data_principal_crud,
        data_elements_crud,
        purposes_crud,
        collection_points_crud,
        grievance_crud,
        dpar_crud,
        vendor_crud,
        consent_artifact_crud,
        consent_artifact_service,
    )
