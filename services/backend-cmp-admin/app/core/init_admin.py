from datetime import UTC, datetime
import json
import random
import string
import uuid
import secrets

from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.common import pwd_context
from app.db.session import get_postgres_pool
from app.core.security import rbac_enforcer
from app.constants.frontend_routes import frontend_routes
from app.core.logger import app_logger


def load_json_data(file_path):
    """Helper function to load JSON data from a file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        app_logger.error(f"Error: {file_path} file not found. Skipping loading data.")
        return []


department_and_role = {}
department_and_role["department_data"] = load_json_data("app/utils/department.json")
department_and_role["role_data"] = load_json_data("app/utils/roles.json")

get_started_data = load_json_data("app/utils/get_started.json")


def generate_keys_and_secret(key_size=16, secret_size=64) -> tuple[str, str]:
    key_chars = string.ascii_letters + string.digits
    secret_chars = string.ascii_letters + string.digits + "$@&?!#%^"

    key = "".join(random.choices(key_chars, k=key_size))
    secret = "".join(random.choices(secret_chars, k=secret_size))

    return key, secret


async def df_initialize(df_id: str, df_keys_collection, departments_collection, roles_collection):

    key, secret = generate_keys_and_secret()

    pool = await get_postgres_pool()

    async with pool.acquire() as conn:
        try:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "dpd" (
                    dp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    dp_system_id TEXT NOT NULL,
                    dp_identifiers TEXT[],
                    dp_email TEXT[],
                    dp_mobile TEXT[],
                    dp_other_identifier TEXT[],
                    dp_preferred_lang TEXT,
                    dp_country TEXT,
                    dp_state TEXT,
                    dp_active_devices TEXT[],
                    dp_tags TEXT[],
                    is_active BOOLEAN DEFAULT TRUE,
                    is_legacy BOOLEAN DEFAULT FALSE,
                    added_by TEXT,
                    added_with TEXT,
                    created_at_df TIMESTAMPTZ DEFAULT NOW(),
                    last_activity TIMESTAMPTZ,
                    dp_e TEXT[],
                    dp_m TEXT[],
                    is_deleted BOOLEAN DEFAULT FALSE,
                    consent_count INTEGER DEFAULT 0,
                    consent_status TEXT,
                    inserted_at TIMESTAMPTZ DEFAULT NOW(),
                    legacy_notification_ids TEXT[],
                    consent_artifacts TEXT[],
                    dpar_req TEXT[]
                );
            """
            )

            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "dpc" (
                    consent_id TEXT PRIMARY KEY,
                    dp_id UUID REFERENCES "dpd"(dp_id),
                    consent_status TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    agreement_id TEXT
                );
            """
            )

            await conn.execute(f'CREATE INDEX IF NOT EXISTS "dpd_system_id_idx" ON "dpd"(dp_system_id);')
            await conn.execute(f'CREATE INDEX IF NOT EXISTS "dpd_email_idx" ON "dpd" USING GIN(dp_email);')
            await conn.execute(f'CREATE INDEX IF NOT EXISTS "dpd_mobile_idx" ON "dpd" USING GIN(dp_mobile);')

            app_logger.info("PostgreSQL tables created successfully!")
        except Exception as e:
            app_logger.error(f"Error creating PostgreSQL tables: {e}")

    api_key = secrets.token_urlsafe(32)
    api_secret = secrets.token_urlsafe(64)

    user_name = f"{df_id}_" + secrets.token_urlsafe(8)
    user_password = secrets.token_urlsafe(32)

    vhost_name = f"sahaj_vhost"

    df_keys = {
        "df_id": df_id,
        "df_key": key,
        "df_secret": secret,
        "queue_configuration": {
            "queue_host_URL": f"http://{settings.RABBITMQ_HOST}/",
            "queue_port": settings.RABBITMQ_PORT,
            "queue_vhost": vhost_name,
            "production": {
                "queue_name": "prod",
                "queue_user": user_name,
                "queue_password": user_password,
            },
            "testing": {
                "queue_name": "testing",
                "queue_user": user_name,
                "queue_password": user_password,
            },
            "data_principal": {
                "queue_name": "data_principal",
                "queue_user": user_name,
                "queue_password": user_password,
            },
        },
        "api_keys": {"add_dp_key": api_key, "add_dp_secret": api_secret},
        "security_considerations": {"audit_logging": False},
        "cogniscan_keys": {"cogniscan_default_key": f"{secrets.token_urlsafe(16)}"},
    }

    existing_keys = await df_keys_collection.find_one({"df_id": df_id})
    if not existing_keys:
        await df_keys_collection.insert_one(df_keys)
        app_logger.info(f"Keys added for {df_id}")
    else:
        app_logger.info(f"Keys already exist for {df_id}")

    for dept in department_and_role["department_data"]:
        exists = await departments_collection.find_one({"df_id": df_id, "department_name": dept["department_name"]})
        if not exists:
            await departments_collection.insert_one(
                {
                    "df_id": df_id,
                    "department_name": dept["department_name"],
                    "department_description": dept["department_description"],
                    "department_users": [],
                    "department_admins": [],
                    "created_at": datetime.now(UTC),
                    "created_by": "sahaj",
                    "modules_accessible": [],
                    "routes_accessible": [],
                    "apis_accessible": [],
                    "is_deleted": False,
                }
            )
    app_logger.info(f"Departments checked/added for {df_id}")

    for role in department_and_role["role_data"]:
        exists = await roles_collection.find_one({"df_id": df_id, "role_name": role["role"]})
        if not exists:
            await roles_collection.insert_one(
                {
                    "df_id": df_id,
                    "role_name": role["role"],
                    "role_description": role["role_description"],
                    "role_users": [],
                    "created_at": datetime.now(UTC),
                    "created_by": "sahaj",
                    "modules_accessible": [],
                    "routes_accessible": [],
                    "apis_accessible": [],
                    "is_deleted": False,
                }
            )
    app_logger.info(f"Roles checked/added for {df_id}")


def seed_rbac(admin_role_id: str):

    rbac_enforcer.load_policy()

    default_policies = []
    for route in frontend_routes:
        default_policies.append((admin_role_id, route["href"], "write"))
        default_policies.append((admin_role_id, route["href"], "read"))

    seeded = False
    for policy in default_policies:
        if not rbac_enforcer.has_policy(*policy):
            rbac_enforcer.add_policy(*policy)
            seeded = True

    if seeded:
        rbac_enforcer.save_policy()
        app_logger.info("Seeding default RBAC policies...")
    else:
        app_logger.info("Default RBAC policies already exist, skipping seeding.")


async def create_initial_admin(client: AsyncIOMotorClient):

    db = client[settings.DB_NAME_CONCUR_MASTER]

    users_collection = db["cmp_users"]
    df_register_collection = db["df_register"]

    df_keys_collection = db["df_keys"]
    departments_collection = db["departments"]
    roles_collection = db["roles"]

    existing_admin = await users_collection.find_one({})
    if existing_admin:
        app_logger.info("Initial admin already exists, skipping creation.")
        return

    df_id = settings.DF_ID

    df_doc = {
        "df_id": df_id,
        "created_at": datetime.now(UTC),
    }

    await df_register_collection.insert_one(df_doc)

    hashed_password = pwd_context.hash(settings.TEMPORARY_PASSWORD)

    system_role = await roles_collection.insert_one(
        {
            "role_name": "system_admin",
            "description": "System Admin role with all permissions",
            "permissions": [
                {
                    "resource": "*",
                    "action": "*",
                    "effect": "allow",
                    "condition": None,
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(UTC),
            "is_deleted": False,
        }
    )

    SYSTEM_ADMIN_ROLE_ID = str(system_role.inserted_id)

    await db["app_config"].update_one(
        {"key": "SYSTEM_ADMIN_ROLE_ID"},
        {"$set": {"value": SYSTEM_ADMIN_ROLE_ID}},
        upsert=True,
    )

    inserted_admin = await users_collection.insert_one(
        {
            "email": settings.SUPERADMIN_EMAIL,
            "password": hashed_password,
            "df_id": df_id,
            "user_roles": [SYSTEM_ADMIN_ROLE_ID],
            "is_password_reseted": False,
            "is_org_configured": False,
        }
    )
    seed_rbac(str(SYSTEM_ADMIN_ROLE_ID))

    df_init = df_initialize(df_id, df_keys_collection, departments_collection, roles_collection)

    await df_init

    app_logger.critical(f"Initial Admin Created. Email: {settings.SUPERADMIN_EMAIL}, Password: {settings.TEMPORARY_PASSWORD}")
