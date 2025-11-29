import asyncio
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.main import app as fastapi_app  # Import the main FastAPI app
from app.core.config import settings
from app.db.dependencies import (
    get_concur_master_db,
    get_concur_logs_db,
)
from app.db.session import get_postgres_pool
from app.api.v1.deps import get_current_user

# Adjust settings for testing
settings.ENVIRONMENT = "test"
settings.DB_NAME_CONCUR_MASTER = "concur_master_test_db"
settings.DB_NAME_COOKIE_MANAGEMENT = "cookie_management_test_db"
settings.DB_NAME_CONCUR_LOGS = "concur_logs_test_db"
# You might want to use a different, isolated MongoDB URI for actual integration tests if running a dedicated test MongoDB
# For now, let's assume a local MongoDB instance and a test database name prefix.


@pytest.fixture(scope="module")  # Changed scope to module as TestClient is synchronous
def client():
    """Fixture for the FastAPI test client."""
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture(scope="session")
async def mongo_client() -> AsyncIOMotorClient:
    """Fixture for the MongoDB client."""
    # Connect to a dedicated test MongoDB instance or use a test database name
    client = AsyncIOMotorClient(settings.MONGO_URI, port=27017)
    yield client
    # Clean up test databases after all tests are done
    await client.drop_database(settings.DB_NAME_CONCUR_MASTER)
    await client.drop_database(settings.DB_NAME_COOKIE_MANAGEMENT)
    await client.drop_database(settings.DB_NAME_CONCUR_LOGS)
    client.close()


@pytest.fixture(scope="session")
async def concur_master_db(mongo_client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Fixture for the concur master database."""
    return mongo_client[settings.DB_NAME_CONCUR_MASTER]


@pytest.fixture(scope="session")
async def cookie_management_db(mongo_client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Fixture for the cookie management database."""
    return mongo_client[settings.DB_NAME_COOKIE_MANAGEMENT]


@pytest.fixture(scope="session")
async def concur_logs_db(mongo_client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Fixture for the concur logs database."""
    return mongo_client[settings.DB_NAME_CONCUR_LOGS]


# Override dependencies for testing
def override_get_current_user():
    # Return a dummy user for authenticated endpoints
    return {"_id": "60d0fe4f3460595e63456789", "email": "testuser@example.com", "user_roles": ["system_admin"], "df_id": "test_df_id"}


# Override the application's dependencies
fastapi_app.dependency_overrides[get_current_user] = override_get_current_user

# Mock database dependencies to return our test databases
fastapi_app.dependency_overrides[get_concur_master_db] = lambda: concur_master_db
fastapi_app.dependency_overrides[get_concur_logs_db] = lambda: concur_logs_db


# Mock PostgreSQL pool for now, as we don't have a specific test setup for it yet
@pytest.fixture(scope="session")
async def postgres_pool_mock():
    """Mock for PostgreSQL pool."""

    class MockPool:
        async def acquire(self):
            return self

        async def release(self, conn):
            pass

        async def fetchrow(self, query, *args):
            return None  # Or a dummy row

        async def fetch(self, query, *args):
            return []

        async def execute(self, query, *args):
            return "MOCK_COMMAND_OK"

        async def close(self):
            pass

    return MockPool()


fastapi_app.dependency_overrides[get_postgres_pool] = lambda: postgres_pool_mock
