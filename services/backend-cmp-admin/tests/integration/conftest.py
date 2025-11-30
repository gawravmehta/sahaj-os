import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.db.dependencies import get_concur_master_db
from app.api.v1.deps import get_current_user

MONGO_TEST_URI = "mongodb://localhost:27017"
TEST_DB_NAME = "test_db"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    motor_client = AsyncIOMotorClient(MONGO_TEST_URI)
    db = motor_client[TEST_DB_NAME]

    for coll_name in await db.list_collection_names():
        await db[coll_name].drop()

    async def override_get_db():
        yield db

    async def override_get_current_user():
        return {
            "_id": "615f8d9b8d9b8d9b8d9b8d9b",
            "email": "test@example.com",
            "df_id": "615f8d9b8d9b8d9b8d9b8d9b",
        }

    app.dependency_overrides[get_concur_master_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield db

    # Teardown
    await motor_client.drop_database(TEST_DB_NAME)
    motor_client.close()

    app.dependency_overrides.pop(get_concur_master_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
