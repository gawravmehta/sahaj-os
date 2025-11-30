import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from unittest.mock import patch
from app.schemas.data_element_schema import LanguageCodes
from fastapi import HTTPException, status
from bson import ObjectId

# Helper function to create a valid DataElementCreate payload
def de_create_body(name="Test DE", description="Desc", original_name="Orig Name", data_type="string", sensitivity="low", is_core_identifier=False, retention_period=30):
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

# Helper function to create a dummy ObjectId string
def dummy_object_id():
    return str(ObjectId())

@pytest.mark.asyncio
async def test_create_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    data_element_data = de_create_body()
    response = await client.post("/api/v1/data-elements/create-data-element", json=data_element_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["de_name"] == data_element_data["de_name"]
    assert "de_id" in response_data
    assert response_data["de_status"] == "draft"

    de_id = response_data["de_id"]
    get_response = await client.get(f"/api/v1/data-elements/get-data-element/{de_id}")
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    assert get_response_data["de_name"] == data_element_data["de_name"]
    assert get_response_data["de_description"] == data_element_data["de_description"]


@pytest.mark.asyncio
async def test_create_data_element_invalid_data(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Missing required field (de_name)
    invalid_data = de_create_body()
    invalid_data.pop("de_name")
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422

    # Invalid enum value for de_sensitivity
    invalid_data = de_create_body()
    invalid_data["de_sensitivity"] = "super_high"
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422

    # Invalid value for de_retention_period (non-positive)
    invalid_data = de_create_body()
    invalid_data["de_retention_period"] = 0
    response = await client.post("/api/v1/data-elements/create-data-element", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_data_element_duplicate_name(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    data_element_data = de_create_body(name="Duplicate DE")
    response1 = await client.post("/api/v1/data-elements/create-data-element", json=data_element_data)
    assert response1.status_code == 201

    response2 = await client.post("/api/v1/data-elements/create-data-element", json=data_element_data)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_get_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent_id = dummy_object_id()
    response = await client.get(f"/api/v1/data-elements/get-data-element/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Data Element not found"


@pytest.mark.asyncio
async def test_get_all_data_elements_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE One"))
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE Two"))

    response = await client.get("/api/v1/data-elements/get-all-data-element")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["total_items"] >= 2 # Could be more if other tests created items
    assert "data_elements" in response_data
    assert any(de["de_name"] == "DE One" for de in response_data["data_elements"])
    assert any(de["de_name"] == "DE Two" for de in response_data["data_elements"])


@pytest.mark.asyncio
async def test_get_all_data_elements_with_filter(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Core DE", is_core_identifier=True))
    await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="Non-Core DE", is_core_identifier=False))

    response = await client.get("/api/v1/data-elements/get-all-data-element", params={"is_core_identifier": True})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["total_items"] >= 1
    assert all(de["is_core_identifier"] is True for de in response_data["data_elements"])
    assert any(de["de_name"] == "Core DE" for de in response_data["data_elements"])
    assert not any(de["de_name"] == "Non-Core DE" for de in response_data["data_elements"])


@pytest.mark.asyncio
async def test_update_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    create_response = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE to Update"))
    assert create_response.status_code == 201
    de_id = create_response.json()["de_id"]

    update_data = {"de_description": "Updated description", "de_retention_period": 60}
    update_response = await client.patch(f"/api/v1/data-elements/update-data-element/{de_id}", json=update_data)
    assert update_response.status_code == 200
    updated_de = update_response.json()
    assert updated_de["de_id"] == de_id
    assert updated_de["de_description"] == update_data["de_description"]
    assert updated_de["de_retention_period"] == update_data["de_retention_period"]
    assert updated_de["de_name"] == "DE to Update" # Ensure other fields are unchanged


@pytest.mark.asyncio
async def test_update_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent_id = dummy_object_id()
    update_data = {"de_name": "Non Existent Update"}
    response = await client.patch(f"/api/v1/data-elements/update-data-element/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Data Element not found."


@pytest.mark.asyncio
async def test_update_data_element_no_changes(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    create_response = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="No Change DE"))
    assert create_response.status_code == 201
    de_id = create_response.json()["de_id"]

    with patch("app.services.data_element_service.DataElementService.update_data_element", return_value=None):
        update_data = {"de_description": "This update will be mocked to do nothing."}
        update_response = await client.patch(f"/api/v1/data-elements/update-data-element/{de_id}", json=update_data)
        assert update_response.status_code == 404
        assert update_response.json()["detail"] == "Data Element Template not found or no changes made"


@pytest.mark.asyncio
async def test_publish_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    create_response = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE to Publish"))
    assert create_response.status_code == 201
    de_id = create_response.json()["de_id"]

    publish_response = await client.patch(f"/api/v1/data-elements/publish-data-element/{de_id}")
    assert publish_response.status_code == 200
    published_de = publish_response.json()
    assert published_de["de_id"] == de_id
    assert published_de["de_status"] == "published"


@pytest.mark.asyncio
async def test_publish_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent_id = dummy_object_id()
    response = await client.patch(f"/api/v1/data-elements/publish-data-element/{non_existent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_data_element_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    create_response = await client.post("/api/v1/data-elements/create-data-element", json=de_create_body(name="DE to Delete"))
    assert create_response.status_code == 201
    de_id = create_response.json()["de_id"]

    delete_response = await client.delete(f"/api/v1/data-elements/delete-data-element/{de_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["de_id"] == de_id

    get_response = await client.get(f"/api/v1/data-elements/get-data-element/{de_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_data_element_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent_id = dummy_object_id()
    response = await client.delete(f"/api/v1/data-elements/delete-data-element/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Data Element not found or already deleted."


@pytest.mark.parametrize(
    "service_method_to_patch, http_method, endpoint_url, request_data",
    [
        (
            "app.services.data_element_service.DataElementService.create_data_element",
            "POST",
            "/api/v1/data-elements/create-data-element",
            de_create_body(name="Error Create DE"),
        ),
        (
            "app.services.data_element_service.DataElementService.update_data_element",
            "PATCH",
            "/api/v1/data-elements/update-data-element/placeholder_id",
            {"de_description": "New description"},
        ),
        (
            "app.services.data_element_service.DataElementService.publish_data_element",
            "PATCH",
            "/api/v1/data-elements/publish-data-element/placeholder_id",
            None,
        ),
        (
            "app.services.data_element_service.DataElementService.get_all_data_element",
            "GET",
            "/api/v1/data-elements/get-all-data-element",
            None,
        ),
        (
            "app.services.data_element_service.DataElementService.get_data_element",
            "GET",
            "/api/v1/data-elements/get-data-element/placeholder_id",
            None,
        ),
        (
            "app.services.data_element_service.DataElementService.delete_data_element",
            "DELETE",
            "/api/v1/data-elements/delete-data-element/placeholder_id",
            None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_data_element_endpoints_internal_server_error(
    client: AsyncClient,
    test_db: AsyncIOMotorDatabase,
    service_method_to_patch,
    http_method,
    endpoint_url,
    request_data,
):
    de_id = dummy_object_id() # Default dummy ID

    # Create a real data element for endpoints that need a valid ID
    if "placeholder_id" in endpoint_url and http_method in ["PATCH", "GET", "DELETE"]:
        create_response = await client.post(
            "/api/v1/data-elements/create-data-element",
            json=de_create_body(name="Error Test DE"),
        )
        assert create_response.status_code == 201
        de_id = create_response.json()["de_id"]

    endpoint_url = endpoint_url.replace("placeholder_id", de_id)

    with patch(service_method_to_patch, side_effect=Exception("A simulated internal error occurred")):
        if http_method == "GET":
            response = await client.get(endpoint_url)
        elif http_method == "POST":
            response = await client.post(endpoint_url, json=request_data)
        elif http_method == "PATCH":
            response = await client.patch(endpoint_url, json=request_data)
        elif http_method == "DELETE":
            response = await client.delete(endpoint_url)

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_list_data_element_templates_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService
    with patch.object(DataElementService, "get_all_data_element_templates", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        response = await client.get("/api/v1/data-elements/templates")
        assert response.status_code == 400
        assert response.json()["detail"] == "A simulated HTTP error"


@pytest.mark.asyncio
async def test_list_data_element_templates_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService
    with patch.object(DataElementService, "get_all_data_element_templates", side_effect=Exception("Simulated internal error")):
        response = await client.get("/api/v1/data-elements/templates")
        assert response.status_code == 500
        assert response.json()["detail"] == "Simulated internal error"


@pytest.mark.asyncio
async def test_copy_data_element_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService
    de_id = dummy_object_id() # Needs a de_id in the URL
    with patch.object(DataElementService, "copy_data_element", side_effect=Exception("Simulated internal error")):
        response = await client.post(f"/api/v1/data-elements/copy-data-element?de_id={de_id}")
        assert response.status_code == 500
        assert response.json()["detail"] == "Simulated internal error"


@pytest.mark.asyncio
async def test_copy_data_element_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService
    de_id = dummy_object_id() # Needs a de_id in the URL
    with patch.object(DataElementService, "copy_data_element", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        response = await client.post(f"/api/v1/data-elements/copy-data-element?de_id={de_id}")
        assert response.status_code == 400
        assert response.json()["detail"] == "A simulated HTTP error"


@pytest.mark.asyncio
async def test_get_all_data_element_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.data_element_service import DataElementService
    with patch.object(DataElementService, "get_all_data_element", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        response = await client.get("/api/v1/data-elements/get-all-data-element")
        assert response.status_code == 400
        assert response.json()["detail"] == "A simulated HTTP error"
