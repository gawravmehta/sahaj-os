# import pytest
# import uuid
# from fastapi.testclient import TestClient
# from motor.motor_asyncio import AsyncIOMotorClient

# from app.main import app
# from app.db.dependencies import (
#     get_concur_master_db,
#     get_concur_logs_db,
# )
# from app.api.v1.deps import get_current_user
# from app.core.config import settings


# # -------------------------------------------------------------
# #  USER OVERRIDE (FOR TESTING AUTHENTICATED ENDPOINTS)
# # -------------------------------------------------------------


# @pytest.fixture
# def test_user():
#     return {
#         "_id": "60d0fe4f3460595e63456789",
#         "email": "testuser@example.com",
#         "user_roles": ["system_admin"],
#         "df_id": "test_df_id",
#     }


# @pytest.fixture
# def override_user(test_user):
#     def _override():
#         return test_user

#     return _override


# # -------------------------------------------------------------
# #  UNIQUE MONGO DB FOR EACH TEST RUN
# # -------------------------------------------------------------


# @pytest.fixture(scope="session")
# async def mongo_client():
#     """Connect using your real Mongo URI."""
#     client = AsyncIOMotorClient(settings.MONGO_MASTER_URI)
#     yield client
#     client.close()


# @pytest.fixture(scope="session")
# async def concur_master_db(mongo_client):
#     """
#     Create a unique isolated DB for this test session.
#     Example: concur_master_test_ab12c98c3
#     """
#     db_name = f"test_master_{uuid.uuid4().hex[:8]}"
#     db = mongo_client[db_name]

#     yield db

#     # Drop after tests
#     # await mongo_client.drop_database(db_name)


# @pytest.fixture(scope="session")
# async def concur_logs_db(mongo_client):
#     """Same isolation for logs DB."""
#     db_name = f"test_logs_{uuid.uuid4().hex[:8]}"
#     db = mongo_client[db_name]

#     yield db

#     await mongo_client.drop_database(db_name)


# # -------------------------------------------------------------
# #  MAIN TEST CLIENT (NO POSTGRES, ONLY MONGO OVERRIDES)
# # -------------------------------------------------------------


# @pytest.fixture
# def client(
#     override_user,
#     concur_master_db,
#     concur_logs_db,
# ):
#     """
#     Injects isolated test DBs + test user into FastAPI.
#     """

#     app.dependency_overrides[get_current_user] = override_user
#     app.dependency_overrides[get_concur_master_db] = lambda: concur_master_db
#     app.dependency_overrides[get_concur_logs_db] = lambda: concur_logs_db

#     with TestClient(app) as c:
#         yield c

#     app.dependency_overrides = {}
