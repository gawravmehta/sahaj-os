# tests/conftest.py
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import unittest.mock

from app.main import app
from app.api.v1.deps import get_current_user, get_asset_service
from app.db.dependencies import get_db_client
from app.crud.assets_crud import AssetCrud
from app.services.assets_service import AssetService
from app.utils.business_logger import log_business_event, opensearch_client
from app.core.config import settings


TEST_DB_NAME = "sahaj_tests"


# ------------ Event Loop for async DB ops ------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ------------ Async DB client fixture ------------
@pytest_asyncio.fixture(scope="session")
async def test_db_client():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    yield client
    await client.drop_database(TEST_DB_NAME)
    client.close()


# ------------ SYNC fixture for dependency overrides (IMPORTANT) ------------
@pytest.fixture(autouse=True)
def override_dependencies(test_db_client, event_loop):

    # Attach Mongo client to app
    app.state.motor_client = test_db_client

    # Swap DB name
    original_db = settings.DB_NAME_CONCUR_MASTER
    settings.DB_NAME_CONCUR_MASTER = TEST_DB_NAME

    # override DB client
    app.dependency_overrides[get_db_client] = lambda: test_db_client

    # fake user
    def fake_user():
        return {"_id": "u1", "df_id": "df123", "email": "test@example.com"}

    app.dependency_overrides[get_current_user] = fake_user

    # mock opensearch + log function
    app.dependency_overrides[log_business_event] = unittest.mock.AsyncMock()
    mock_os = unittest.mock.Mock()
    mock_os.index.return_value = {"_id": "mock_id"}
    app.dependency_overrides[opensearch_client] = mock_os

    # real service
    async def real_asset_service():
        db = test_db_client[TEST_DB_NAME]
        crud = AssetCrud(db["asset_master"])
        return AssetService(crud, "app-logs-business")

    app.dependency_overrides[get_asset_service] = real_asset_service

    # clean DB (sync wrapper)
    event_loop.run_until_complete(test_db_client.drop_database(TEST_DB_NAME))

    yield

    # reset after test
    app.dependency_overrides = {}
    settings.DB_NAME_CONCUR_MASTER = original_db


# ------------ SAFE TestClient fixture (sync) ------------
@pytest.fixture
def client():
    return TestClient(app)
