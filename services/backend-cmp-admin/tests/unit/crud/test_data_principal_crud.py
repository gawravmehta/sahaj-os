import pytest
from unittest.mock import AsyncMock, MagicMock
import asyncpg
from typing import List, Dict, Any
from app.crud.data_principal_crud import DataPrincipalCRUD
from datetime import datetime, timezone
import uuid


# ------------------ MOCK ASYNCPG POOL AND CONNECTION FIXTURES ------------------


@pytest.fixture
def mock_conn():
    """Mocked asyncpg connection."""
    conn = MagicMock(spec=asyncpg.Connection)
    conn.execute = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetchval = AsyncMock(return_value=0)
    conn.fetch = AsyncMock(return_value=[])
    return conn


@pytest.fixture
def mock_pool(mock_conn): # Removed 'async' here
    """Mocked asyncpg pool."""
    pool = MagicMock(spec=asyncpg.Pool)
    # Mock acquire context manager
    mock_ctx_mgr = AsyncMock()
    mock_ctx_mgr.__aenter__.return_value = mock_conn
    pool.acquire.return_value = mock_ctx_mgr
    return pool


@pytest.fixture
def crud(mock_pool):
    return DataPrincipalCRUD(mock_pool)


@pytest.fixture
def dummy_dp_data():
    return {
        "dp_id": str(uuid.uuid4()),
        "dp_system_id": "system_id_123",
        "dp_identifiers": ["identifier_A", "identifier_B"],
        "dp_email": ["email1@example.com"],
        "dp_mobile": ["+1234567890"],
        "dp_other_identifier": ["other_id_X"],
        "dp_preferred_lang": "en",
        "dp_country": "USA",
        "dp_state": "CA",
        "dp_active_devices": ["device_1"],
        "dp_tags": ["tag1", "tag2"],
        "is_active": True,
        "is_legacy": False,
        "added_by": "admin",
        "added_with": "API",
        "created_at_df": datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "last_activity": datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
        "dp_e": ["hashed_email1"],
        "dp_m": ["hashed_mobile1"],
        "is_deleted": False,
        "consent_count": 1,
        "consent_status": "active",
        "inserted_at": datetime(2023, 1, 1, 9, 0, 0, tzinfo=timezone.utc),
        "legacy_notification_ids": ["legacy1"],
        "consent_artifacts": ["artifact1"],
        "dpar_req": ["dpar1"],
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_ensure_table(crud, mock_conn):
    table_name = "test_data_principals"
    await crud.ensure_table(table_name)
    mock_conn.execute.assert_called_once()
    assert f"CREATE TABLE IF NOT EXISTS {table_name}" in mock_conn.execute.call_args[0][0]


@pytest.mark.asyncio
async def test_get_by_system_id(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    system_id = dummy_dp_data["dp_system_id"]
    mock_conn.fetchrow.return_value = {
        "dp_email": dummy_dp_data["dp_email"],
        "dp_mobile": dummy_dp_data["dp_mobile"],
        "is_deleted": dummy_dp_data["is_deleted"],
    }

    result = await crud.get_by_system_id(table_name, system_id)

    mock_conn.fetchrow.assert_called_once()
    assert system_id in mock_conn.fetchrow.call_args[0]
    assert result["dp_email"] == dummy_dp_data["dp_email"]


@pytest.mark.asyncio
async def test_get_by_dp_id(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    dp_id = dummy_dp_data["dp_id"]
    mock_conn.fetchrow.return_value = dummy_dp_data.copy() # Return full data

    result = await crud.get_by_dp_id(table_name, dp_id)

    mock_conn.fetchrow.assert_called_once()
    assert dp_id in mock_conn.fetchrow.call_args[0]
    assert result["dp_id"] == dummy_dp_data["dp_id"]


@pytest.mark.asyncio
async def test_insert_or_update_deleted(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    system_id = dummy_dp_data["dp_system_id"]
    emails = dummy_dp_data["dp_email"]
    mobiles = dummy_dp_data["dp_mobile"]

    await crud.insert_or_update_deleted(table_name, system_id, emails, mobiles)

    mock_conn.execute.assert_called_once()
    assert system_id in mock_conn.execute.call_args[0]
    assert emails in mock_conn.execute.call_args[0]
    assert mobiles in mock_conn.execute.call_args[0]


@pytest.mark.asyncio
async def test_insert(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"

    await crud.insert(table_name, dummy_dp_data)

    mock_conn.execute.assert_called_once()
    # Verify that data elements are passed correctly
    assert dummy_dp_data["dp_id"] in mock_conn.execute.call_args[0]
    assert dummy_dp_data["dp_system_id"] in mock_conn.execute.call_args[0]


@pytest.mark.asyncio
async def test_exists_not_deleted(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    principal_id = dummy_dp_data["dp_id"]
    mock_conn.fetchval.return_value = 1 # Simulate existence

    result = await crud.exists_not_deleted(table_name, principal_id)

    mock_conn.fetchval.assert_called_once()
    assert "SELECT COUNT" in mock_conn.fetchval.call_args[0][0] # Use 'in' for partial string match
    assert mock_conn.fetchval.call_args[0][1] == principal_id # Check positional args
    assert result == 1


@pytest.mark.asyncio
async def test_get_consent_status(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    principal_id = dummy_dp_data["dp_id"]
    mock_conn.fetchval.return_value = dummy_dp_data["consent_status"]

    result = await crud.get_consent_status(table_name, principal_id)

    mock_conn.fetchval.assert_called_once()
    assert "SELECT consent_status" in mock_conn.fetchval.call_args[0][0] # Use 'in' for partial string match
    assert mock_conn.fetchval.call_args[0][1] == principal_id # Check positional args
    assert result == dummy_dp_data["consent_status"]


@pytest.mark.asyncio
async def test_soft_delete(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    principal_id = dummy_dp_data["dp_id"]

    await crud.soft_delete(table_name, principal_id)

    mock_conn.execute.assert_called_once()
    assert "UPDATE" in mock_conn.execute.call_args[0][0]
    assert principal_id in mock_conn.execute.call_args[0]


@pytest.mark.asyncio
async def test_count(crud, mock_conn):
    table_name = "test_data_principals"
    where_clause = "dp_country = $1"
    values = ["USA"]
    mock_conn.fetchval.return_value = 10

    result = await crud.count(table_name, where_clause, values)

    mock_conn.fetchval.assert_called_once()
    assert "SELECT COUNT" in mock_conn.fetchval.call_args[0][0] # Use 'in' for partial string match
    assert mock_conn.fetchval.call_args[0][1:] == tuple(values) # Check positional args
    assert result == 10


@pytest.mark.asyncio
async def test_fetch_all(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    where_clause = "dp_country = $1"
    values = ["USA"]
    limit = 10
    offset = 0
    mock_conn.fetch.return_value = [dummy_dp_data.copy()]

    result = await crud.fetch_all(table_name, where_clause, values, limit, offset)

    mock_conn.fetch.assert_called_once()
    # Check query string and parameters
    assert where_clause in mock_conn.fetch.call_args[0][0]
    assert f"LIMIT ${len(values)+1} OFFSET ${len(values)+2}" in mock_conn.fetch.call_args[0][0]
    assert mock_conn.fetch.call_args[0][1:] == (*values, limit, offset)
    assert len(result) == 1
    assert result[0] == dummy_dp_data


@pytest.mark.asyncio
async def test_fetch_options(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    mock_conn.fetchrow.return_value = {
        "dp_country": ["USA", "IND"],
        "dp_preferred_lang": ["en", "fr"],
        "is_legacy": [True, False],
        "dp_tags": ["tag1", "tag2"],
        "consent_status": ["active", "revoked"],
        "added_with": ["API", "Manual"],
    }

    result = await crud.fetch_options(table_name)

    mock_conn.fetchrow.assert_called_once()
    assert "array_agg(DISTINCT dp_country)" in mock_conn.fetchrow.call_args[0][0]
    assert result["dp_country"] == ["USA", "IND"]


@pytest.mark.asyncio
async def test_get_emails_mobiles_and_other_identifiers(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    principal_id = dummy_dp_data["dp_id"]
    mock_conn.fetchrow.return_value = {
        "dp_email": dummy_dp_data["dp_email"],
        "dp_mobile": dummy_dp_data["dp_mobile"],
        "dp_other_identifier": dummy_dp_data["dp_other_identifier"],
    }

    result = await crud.get_emails_mobiles_and_other_identifiers(table_name, principal_id)

    mock_conn.fetchrow.assert_called_once()
    assert "SELECT dp_email, dp_mobile, dp_other_identifier" in mock_conn.fetchrow.call_args[0][0] # Use 'in' for partial string match
    assert mock_conn.fetchrow.call_args[0][1] == principal_id # Check positional args
    assert result["dp_email"] == dummy_dp_data["dp_email"]


@pytest.mark.asyncio
async def test_update_principal(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    principal_id = dummy_dp_data["dp_id"]
    set_clauses = "dp_country = $1, dp_state = $2"
    values = ["CAN", "ON", principal_id] # principal_id is the last value for $len(values)

    await crud.update_principal(table_name, principal_id, set_clauses, values)

    mock_conn.execute.assert_called_once()
    assert set_clauses in mock_conn.execute.call_args[0][0]
    assert tuple(values) == mock_conn.execute.call_args[0][1:] # Compare tuple with tuple


@pytest.mark.asyncio
async def test_fetch_all_tags(crud, mock_conn, dummy_dp_data):
    table_name = "test_data_principals"
    mock_conn.fetch.return_value = [{"tag": "tag1"}, {"tag": "tag2"}]

    result = await crud.fetch_all_tags(table_name)

    mock_conn.fetch.assert_called_once()
    assert "unnest(dp_tags) AS tag" in mock_conn.fetch.call_args[0][0]
    assert result == ["tag1", "tag2"]
