from app.crud.assets_crud import AssetCrud
from app.crud.collection_point_crud import CollectionPointCrud
from app.crud.data_element_crud import DataElementCRUD
from app.crud.data_principal_crud import DataPrincipalCRUD
from app.crud.department_crud import DepartmentCRUD
from app.crud.dpar_crud import DparCRUD
from app.crud.grievance_crud import GrievanceCRUD
from app.crud.purpose_crud import PurposeCRUD
from app.crud.role_crud import RoleCRUD
from app.crud.user_crud import UserCRUD
from app.crud.vendor_crud import VendorCRUD
from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from app.services.consent_artifact_service import ConsentArtifactService


class DashboardService:
    def __init__(
        self,
        departments_crud: DepartmentCRUD,
        roles_crud: RoleCRUD,
        users_crud: UserCRUD,
        assets_crud: AssetCrud,
        data_principal_crud: DataPrincipalCRUD,
        data_elements_crud: DataElementCRUD,
        purposes_crud: PurposeCRUD,
        collection_points_crud: CollectionPointCrud,
        grievance_crud: GrievanceCRUD,
        dpar_crud: DparCRUD,
        vendor_crud: VendorCRUD,
        consent_artifact_crud: ConsentArtifactCRUD,
        consent_artifact_service: ConsentArtifactService,
    ):
        self.departments_crud = departments_crud
        self.roles_crud = roles_crud
        self.users_crud = users_crud
        self.assets_crud = assets_crud
        self.data_principal_crud = data_principal_crud
        self.data_elements_crud = data_elements_crud
        self.purposes_crud = purposes_crud
        self.collection_points_crud = collection_points_crud
        self.grievance_crud = grievance_crud
        self.dpar_crud = dpar_crud
        self.vendor_crud = vendor_crud
        self.consent_artifact_crud = consent_artifact_crud
        self.consent_artifact_service = consent_artifact_service

    async def get_dashboard_detail(self, current_user: dict):

        total_departments = await self.departments_crud.count_departments(current_user.get("df_id"))
        total_roles = await self.roles_crud.count_roles(current_user.get("df_id"))
        total_users = await self.users_crud.count_users(current_user.get("df_id"))

        total_assets = await self.assets_crud.count_assets(current_user.get("df_id"))
        list_of_assets_categories = await self.assets_crud.get_assets_categories(current_user.get("df_id"))
        total_cookies = await self.assets_crud.get_total_cookie_count(current_user.get("df_id"))

        total_legacy_data_principals = await self.data_principal_crud.count(table_name="dpd", where_clause="is_legacy = $1", values=[True])

        total_new_data_principals = await self.data_principal_crud.count(table_name="dpd", where_clause="is_legacy = $1", values=[False])

        total_data_elements = await self.data_elements_crud.count_data_elements(current_user.get("df_id"))
        total_collected_data_elements = await self.consent_artifact_crud.count_collected_data_elements({})

        total_purposes = await self.purposes_crud.count_consent_purposes(current_user.get("df_id"))
        total_collected_purposes = await self.consent_artifact_crud.count_collected_purposes({})

        total_collection_points = await self.collection_points_crud.count_collection_points(current_user.get("df_id"))
        total_collected_collection_points = await self.consent_artifact_crud.count_collected_collection_points({})

        active_grievances = await self.grievance_crud.count_grievances()
        closed_grievances = 0
        active_dpar_requests = await self.dpar_crud.count_requests({"status": {"$ne": "complete"}})
        closed_dpar_requests = await self.dpar_crud.count_requests({"status": "complete"})
        total_data_processors = await self.vendor_crud.count_vendors({"df_id": current_user.get("df_id"), "status": {"$ne": "archived"}})

        total_consent_artifacts = await self.consent_artifact_crud.count_filtered_consent_artifacts({})

        expiring_consents_seven_days = await self.consent_artifact_service.get_expiring_consents(df_id=current_user.get("df_id"), days_to_expire="7")
        total_expiring_consent_in_seven_days = len(expiring_consents_seven_days)

        expiring_consents_fifteen_days = await self.consent_artifact_service.get_expiring_consents(
            df_id=current_user.get("df_id"), days_to_expire="15"
        )
        total_expiring_consent_in_fifteen_days = len(expiring_consents_fifteen_days)

        expiring_consents_thirty_days = await self.consent_artifact_service.get_expiring_consents(
            df_id=current_user.get("df_id"), days_to_expire="30"
        )
        total_expiring_consent_in_thirty_days = len(expiring_consents_thirty_days)

        return {
            "total_departments": total_departments,
            "total_roles": total_roles,
            "total_users": total_users,
            "total_assets": total_assets,
            "list_of_assets_categories": list_of_assets_categories,
            "total_legacy_data_principals": total_legacy_data_principals,
            "total_cookies": total_cookies,
            "total_new_data_principals": total_new_data_principals,
            "total_data_elements": total_data_elements,
            "total_collected_data_elements": total_collected_data_elements,
            "total_purposes": total_purposes,
            "total_collected_purposes": total_collected_purposes,
            "total_collection_points": total_collection_points,
            "total_collected_collection_points": total_collected_collection_points,
            "active_grievances": active_grievances,
            "closed_grievances": closed_grievances,
            "active_dpar_requests": active_dpar_requests,
            "closed_dpar_requests": closed_dpar_requests,
            "total_data_processors": total_data_processors,
            "total_consent_artifacts": total_consent_artifacts,
            "total_expiring_consent_in_seven_days": total_expiring_consent_in_seven_days,
            "total_expiring_consent_in_fifteen_days": total_expiring_consent_in_fifteen_days,
            "total_expiring_consent_in_thirty_days": total_expiring_consent_in_thirty_days,
        }
