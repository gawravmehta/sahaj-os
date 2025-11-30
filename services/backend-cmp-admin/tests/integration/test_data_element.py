import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from unittest.mock import patch
from fastapi import HTTPException
from bson import ObjectId


# Helper function to create a valid DataElementCreate payload
def de_create_body(
    name="Test DE",
    description="Desc",
    original_name="Orig Name",
    data_type="string",
    sensitivity="low",
    is_core_identifier=False,
    retention_period=30,
):
    return {
        "de_name": name,
        "de_description": description,
        "de_original_name": original_name,
        "de_data_type": data_type,
        "de_sensitivity": sensitivity,
        "is_core_identifier": is_core_identifier,
        "de_retention_period": retention_period,
        "translations": {"eng": "English translation"},
    }


def dummy_object_id():
    return str(ObjectId())


# -------------------------
# CREATE TEST
# -------------------------
@pytest.mark.asyncio
async def test_create_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    data_element_data = de_create_body()
    response = await client.post("/api/v1/data-elements/create-data-element", json=data_element_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["de_name"] == data_element_data["de_name"]
    assert "de_id" in response_data
    assert response_data["de_status"] == "draft"

    # verify DB
    de_id = response_data["de_id"]
    get_response = await client.get(f"/api/v1/data-elements/get-data-element/{de_id}")
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_create_data_element_invalid_data(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    invalid_data = de_create_body()
    invalid_data.pop("de_name")
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422

    invalid_data = de_create_body()
    invalid_data["de_sensitivity"] = "super_high"
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422

    invalid_data = de_create_body()
    invalid_data["de_retention_period"] = 0
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_data_element_duplicate_name(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    payload = de_create_body(name="Duplicate DE")
    res1 = await client.post("/api/v1/data-elements/create-data-element", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/data-elements/create-data-element", json=payload)
    assert res2.status_code == 409


# -------------------------
# GET TESTS
# -------------------------
@pytest.mark.asyncio
async def test_get_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent = dummy_object_id()
    res = await client.get(f"/api/v1/data-elements/get-data-element/{non_existent}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Data Element not found"


@pytest.mark.asyncio
async def test_get_all_data_elements_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE One"))
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE Two"))

    res = await client.get("/api/v1/data-elements/get-all-data-element")
    assert res.status_code == 200
    data = res.json()
    assert "data_elements" in data
    assert data["total_items"] >= 2


@pytest.mark.asyncio
async def test_get_all_data_elements_with_filter(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Core DE", is_core_identifier=True))
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Non Core", is_core_identifier=False))

    res = await client.get("/api/v1/data-elements/get-all-data-element", params={"is_core_identifier": True})
    assert res.status_code == 200
    data = res.json()
    assert all(de["is_core_identifier"] is True for de in data["data_elements"])


@pytest.mark.asyncio
async def test_get_all_data_elements_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService

    with patch.object(DataElementService, "get_all_data_element", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        res = await client.get("/api/v1/data-elements/get-all-data-element")
        assert res.status_code == 400
        assert res.json()["detail"] == "A simulated HTTP error"


# -------------------------
# UPDATE TESTS
# -------------------------
@pytest.mark.asyncio
async def test_update_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE Update"))
    de_id = res.json()["de_id"]

    update_data = {"de_description": "Updated", "de_retention_period": 60}

    res2 = await client.patch(f"/api/v1/data-elements/update-data-element/{de_id}", json=update_data)
    assert res2.status_code == 200
    updated = res2.json()
    assert updated["de_description"] == "Updated"
    assert updated["de_retention_period"] == 60


@pytest.mark.asyncio
async def test_update_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()

    res = await client.patch(f"/api/v1/data-elements/update-data-element/{fake_id}", json={"de_description": "Something"})

    assert res.status_code == 404
    assert res.json()["detail"] == "Data Element not found."


@pytest.mark.asyncio
async def test_update_data_element_no_changes(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="No Change"))
    de_id = res.json()["de_id"]

    with patch("app.services.data_element_service.DataElementService.update_data_element", return_value=None):
        res2 = await client.patch(f"/api/v1/data-elements/update-data-element/{de_id}", json={"de_description": "Mock"})
        assert res2.status_code == 404
        assert res2.json()["detail"] == "Data Element Template not found or no changes made"


# -------------------------
# PUBLISH TEST
# -------------------------
@pytest.mark.asyncio
async def test_publish_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Publish Me"))
    de_id = res.json()["de_id"]

    res2 = await client.patch(f"/api/v1/data-elements/publish-data-element/{de_id}")
    assert res2.status_code == 200
    assert res2.json()["de_status"] == "published"


@pytest.mark.asyncio
async def test_publish_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    res = await client.patch(f"/api/v1/data-elements/publish-data-element/{fake_id}")
    assert res.status_code == 404


# -------------------------
# DELETE TESTS
# -------------------------
@pytest.mark.asyncio
async def test_delete_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body())
    de_id = res.json()["de_id"]

    res2 = await client.delete(f"/api/v1/data-elements/delete-data-element/{de_id}")
    assert res2.status_code == 200

    # verify deletion
    res3 = await client.get(f"/api/v1/data-elements/get-data-element/{de_id}")
    assert res3.status_code == 404


@pytest.mark.asyncio
async def test_delete_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    res = await client.delete(f"/api/v1/data-elements/delete-data-element/{fake_id}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Data Element not found or already deleted."


# ================================================================
#  🔥 CONSOLIDATED INTERNAL SERVER ERROR TESTS
# ================================================================

ENDPOINTS = [
    ("POST", "/api/v1/data-elements/create-data-element", "app.services.data_element_service.DataElementService.create_data_element", True),
    ("PATCH", "/api/v1/data-elements/update-data-element/{id}", "app.services.data_element_service.DataElementService.update_data_element", True),
    ("PATCH", "/api/v1/data-elements/publish-data-element/{id}", "app.services.data_element_service.DataElementService.publish_data_element", False),
    ("GET", "/api/v1/data-elements/get-data-element/{id}", "app.services.data_element_service.DataElementService.get_data_element", False),
    ("GET", "/api/v1/data-elements/get-all-data-element", "app.services.data_element_service.DataElementService.get_all_data_element", False),
    ("DELETE", "/api/v1/data-elements/delete-data-element/{id}", "app.services.data_element_service.DataElementService.delete_data_element", False),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url, service_method, needs_payload", ENDPOINTS)
async def test_internal_server_errors(client: AsyncClient, test_db: AsyncIOMotorDatabase, method, url, service_method, needs_payload):

    # Create a real DE when required
    if "{id}" in url:
        c = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Temp Internal Error"))
        de_id = c.json()["de_id"]
        url = url.replace("{id}", de_id)

    if needs_payload:
        if url.endswith("create-data-element"):
            payload = de_create_body()
        else:
            payload = {"de_description": "Updated"}
    else:
        payload = None

    with patch(service_method, side_effect=Exception("Simulated Internal Error")):
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=payload)
        elif method == "PATCH":
            response = await client.patch(url, json=payload)
        elif method == "DELETE":
            response = await client.delete(url)

    assert response.status_code == 500
    assert response.json()["detail"] == "Simulated Internal Error"


# -------------------------
# TEMPLATE LIST TESTS
# -------------------------
@pytest.mark.asyncio
async def test_list_data_element_templates_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService

    with patch.object(
        DataElementService, "get_all_data_element_templates", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")
    ):
        res = await client.get("/api/v1/data-elements/templates")
        assert res.status_code == 400
        assert res.json()["detail"] == "A simulated HTTP error"


@pytest.mark.asyncio
async def test_list_data_element_templates_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService

    with patch.object(DataElementService, "get_all_data_element_templates", side_effect=Exception("Simulated internal error")):
        res = await client.get("/api/v1/data-elements/templates")
        assert res.status_code == 500
        assert res.json()["detail"] == "Simulated internal error"


# -------------------------
# COPY TESTS
# -------------------------


# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", return_value=None)
# async def test_copy_data_element_success(mock_log, client: AsyncClient, test_db: AsyncIOMotorDatabase):
#     # First create a data element
#     create_res = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Original DE"))
#     assert create_res.status_code == 201
#     original_id = create_res.json()["de_id"]

#     # Copy it
#     copy_res = await client.post(f"/api/v1/data-elements/copy-data-element?de_id={original_id}")

#     assert copy_res.status_code == 201
#     copied = copy_res.json()


#     assert copied["de_id"] != original_id
#     assert copied["de_name"] == "Original DE"
@pytest.mark.asyncio
async def test_copy_data_element_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService

    de_id = dummy_object_id()
    with patch.object(DataElementService, "copy_data_element", side_effect=Exception("Simulated internal error")):
        res = await client.post(f"/api/v1/data-elements/copy-data-element?de_id={de_id}")
        assert res.status_code == 500
        assert res.json()["detail"] == "Simulated internal error"


@pytest.mark.asyncio
async def test_copy_data_element_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService

    de_id = dummy_object_id()
    with patch.object(DataElementService, "copy_data_element", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        res = await client.post(f"/api/v1/data-elements/copy-data-element?de_id={de_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "A simulated HTTP error"
