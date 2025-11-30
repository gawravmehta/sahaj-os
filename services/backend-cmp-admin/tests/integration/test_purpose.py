import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from unittest.mock import patch, ANY
from fastapi import HTTPException
from bson import ObjectId


def purpose_create_body(
    title="Test Purpose",
    description="Description",
    priority="low",
    review_frequency="quarterly",
    consent_time_period=30,
    reconsent=False,
    translations={"eng": "English translation"},
    data_elements=[],
):
    return {
        "purpose_title": title,
        "purpose_description": description,
        "purpose_priority": priority,
        "review_frequency": review_frequency,
        "consent_time_period": consent_time_period,
        "reconsent": reconsent,
        "data_elements": data_elements,
        "translations": translations,
    }


def dummy_object_id():
    return str(ObjectId())


@pytest.mark.asyncio
async def test_create_purpose_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    purpose_data = purpose_create_body(title="New Purpose Integration")
    response = await client.post("/api/v1/purposes/create-purpose", json=purpose_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["purpose_title"] == purpose_data["purpose_title"]
    assert "purpose_id" in response_data
    assert response_data["purpose_status"] == "draft"

    purpose_id = response_data["purpose_id"]
    get_response = await client.get(f"/api/v1/purposes/get-purpose/{purpose_id}")
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_create_purpose_invalid_data(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    invalid_data = purpose_create_body()
    invalid_data.pop("purpose_title")
    response = await client.post("/api/v1/purposes/create-purpose", json=invalid_data)
    assert response.status_code == 422

    invalid_data = purpose_create_body()
    invalid_data["purpose_priority"] = "super_high"
    response = await client.post("/api/v1/purposes/create-purpose", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_purpose_duplicate_name(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    payload = purpose_create_body(title="Duplicate Purpose")
    res1 = await client.post("/api/v1/purposes/create-purpose", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/purposes/create-purpose", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Purpose title already exists."


@pytest.mark.asyncio
async def test_get_purpose_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    non_existent = dummy_object_id()
    res = await client.get(f"/api/v1/purposes/get-purpose/{non_existent}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Purpose Template not found"


@pytest.mark.asyncio
async def test_get_all_purposes_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Purpose One"))
    await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Purpose Two"))

    res = await client.get("/api/v1/purposes/get-all-purposes")
    assert res.status_code == 200
    data = res.json()
    assert "purposes" in data
    assert data["total_items"] >= 2


@pytest.mark.asyncio
async def test_update_purpose_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Purpose Update"))
    purpose_id = res.json()["purpose_id"]

    update_data = {"purpose_description": "Updated Desc", "consent_time_period": 60}

    res2 = await client.put(f"/api/v1/purposes/update-purpose/{purpose_id}", json=update_data)
    assert res2.status_code == 200
    updated = res2.json()
    assert updated["purpose_description"] == "Updated Desc"
    assert updated["consent_time_period"] == 60


@pytest.mark.asyncio
async def test_update_purpose_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    res = await client.put(f"/api/v1/purposes/update-purpose/{fake_id}", json={"purpose_description": "Something"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Purpose not found."


@pytest.mark.asyncio
async def test_update_purpose_not_draft(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Published Purpose"))
    purpose_id = res.json()["purpose_id"]

    await client.patch(f"/api/v1/purposes/publish-purpose/{purpose_id}")

    update_data = {"purpose_description": "Should not update"}
    res2 = await client.put(f"/api/v1/purposes/update-purpose/{purpose_id}", json=update_data)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Only Purpose in draft status can be updated."


@pytest.mark.asyncio
async def test_publish_purpose_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Publish Me"))
    purpose_id = res.json()["purpose_id"]

    res2 = await client.patch(f"/api/v1/purposes/publish-purpose/{purpose_id}")
    assert res2.status_code == 200
    assert res2.json()["purpose_status"] == "published"


@pytest.mark.asyncio
async def test_publish_purpose_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    res = await client.patch(f"/api/v1/purposes/publish-purpose/{fake_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_publish_purpose_missing_translations(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="No Translations", translations={}))
    purpose_id = res.json()["purpose_id"]

    res2 = await client.patch(f"/api/v1/purposes/publish-purpose/{purpose_id}")
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Translations are required and cannot be empty before publishing."


@pytest.mark.asyncio
async def test_delete_purpose_success(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Delete Me"))
    purpose_id = res.json()["purpose_id"]

    res2 = await client.delete(f"/api/v1/purposes/delete-purpose/{purpose_id}")
    assert res2.status_code == 204

    res3 = await client.get(f"/api/v1/purposes/get-purpose/{purpose_id}")
    assert res3.status_code == 404


@pytest.mark.asyncio
async def test_delete_purpose_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    res = await client.delete(f"/api/v1/purposes/delete-purpose/{fake_id}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Purpose Template not found"


@pytest.mark.asyncio
@patch("app.services.purpose_service.log_business_event", return_value=None)
@patch("app.crud.purpose_crud.PurposeCRUD.get_all_purpose_templates")
@patch("app.services.data_element_service.DataElementService.copy_data_element_by_title")
async def test_copy_purpose_success(
    mock_copy_de_by_title,
    mock_get_templates,
    mock_log,
    client: AsyncClient,
    test_db: AsyncIOMotorDatabase,
):
    template_id = dummy_object_id()

    mock_get_templates.return_value = {
        "data": [
            {
                "_id": template_id,
                "translations": {"en": "External Template Purpose Title"},
                "industry": "Finance",
                "sub_category": "Loans",
                "data_elements": ["DE_Template_1", "DE_Template_2"],
            }
        ],
        "total": 1,
    }

    mock_copy_de_by_title.side_effect = [
        {"_id": dummy_object_id(), "de_name": "Copied DE1"},
        {"_id": dummy_object_id(), "de_name": "Copied DE2"},
    ]

    data_elements_to_copy = ["DE_Template_1", "DE_Template_2"]
    copy_response = await client.post(f"/api/v1/purposes/copy-purpose?purpose_id={template_id}", json=data_elements_to_copy)

    assert copy_response.status_code == 201
    copied_purpose = copy_response.json()

    assert copied_purpose["purpose_title"] == "External Template Purpose Title"
    assert "purpose_id" in copied_purpose
    assert copied_purpose["purpose_id"] != template_id
    assert copied_purpose["purpose_status"] == "draft"
    assert len(copied_purpose["data_elements"]) == 2
    mock_copy_de_by_title.assert_any_call("DE_Template_1", ANY)
    mock_copy_de_by_title.assert_any_call("DE_Template_2", ANY)
    assert mock_copy_de_by_title.call_count == len(data_elements_to_copy)
    mock_log.assert_called_once()


@pytest.mark.asyncio
@patch("app.crud.purpose_crud.PurposeCRUD.get_all_purpose_templates")
async def test_copy_purpose_template_not_found(mock_get_templates, client: AsyncClient, test_db: AsyncIOMotorDatabase):
    fake_id = dummy_object_id()
    mock_get_templates.return_value = {"data": [], "total": 0}
    res = await client.post(f"/api/v1/purposes/copy-purpose?purpose_id={fake_id}", json=[])
    assert res.status_code == 404
    assert res.json()["detail"] == f"Purpose template with ID '{fake_id}' not found."


@pytest.mark.asyncio
@patch("app.crud.purpose_crud.PurposeCRUD.get_all_purpose_templates")
async def test_copy_purpose_duplicate_name(mock_get_templates, client: AsyncClient, test_db: AsyncIOMotorDatabase):
    template_id = dummy_object_id()

    existing_purpose_title = "Existing Purpose for Copy Test"
    await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title=existing_purpose_title))

    mock_get_templates.return_value = {
        "data": [{"_id": template_id, "translations": {"en": existing_purpose_title}}],
        "total": 1,
    }
    res = await client.post(f"/api/v1/purposes/copy-purpose?purpose_id={template_id}", json=[])
    assert res.status_code == 400
    assert res.json()["detail"] == f"Purpose title '{existing_purpose_title}' already exists."


@pytest.mark.asyncio
async def test_copy_purpose_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.purpose_service import PurposeService

    purpose_id = dummy_object_id()
    with patch.object(PurposeService, "copy_purpose", side_effect=Exception("Simulated internal error")):
        res = await client.post(f"/api/v1/purposes/copy-purpose?purpose_id={purpose_id}", json=[])
        assert res.status_code == 500
        assert res.json()["detail"] == "Simulated internal error"


@pytest.mark.asyncio
async def test_copy_purpose_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    from app.services.purpose_service import PurposeService

    purpose_id = dummy_object_id()
    with patch.object(PurposeService, "copy_purpose", side_effect=HTTPException(status_code=400, detail="A simulated HTTP error")):
        res = await client.post(f"/api/v1/purposes/copy-purpose?purpose_id={purpose_id}", json=[])
        assert res.status_code == 400
        assert res.json()["detail"] == "A simulated HTTP error"


ENDPOINTS = [
    (
        "POST",
        "/api/v1/purposes/create-purpose",
        "app.services.purpose_service.PurposeService.create_purpose",
        True,
    ),
    ("PUT", "/api/v1/purposes/update-purpose/{id}", "app.services.purpose_service.PurposeService.update_purpose_data", True),
    ("PATCH", "/api/v1/purposes/publish-purpose/{id}", "app.services.purpose_service.PurposeService.publish_purpose", False),
    ("GET", "/api/v1/purposes/get-purpose/{id}", "app.services.purpose_service.PurposeService.get_purpose", False),
    ("GET", "/api/v1/purposes/get-all-purposes", "app.services.purpose_service.PurposeService.get_all_purpose", False),
    ("DELETE", "/api/v1/purposes/delete-purpose/{id}", "app.services.purpose_service.PurposeService.delete_purpose", False),
    (
        "GET",
        "/api/v1/purposes/templates",
        "app.services.purpose_service.PurposeService.get_all_purpose_templates",
        False,
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url, service_method, needs_payload", ENDPOINTS)
async def test_internal_server_errors(client: AsyncClient, test_db: AsyncIOMotorDatabase, method, url, service_method, needs_payload):

    if "{id}" in url:
        c = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="Temp Internal Error"))
        purpose_id = c.json()["purpose_id"]
        url = url.replace("{id}", purpose_id)

    payload = None
    if needs_payload:
        if "create-purpose" in url:
            payload = purpose_create_body()
        elif "update-purpose" in url:
            payload = {"purpose_description": "Updated"}

    with patch(service_method, side_effect=Exception("Simulated Internal Error")):
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=payload)
        elif method == "PUT":
            response = await client.put(url, json=payload)
        elif method == "PATCH":
            response = await client.patch(url, json=payload)
        elif method == "DELETE":
            response = await client.delete(url)

    assert response.status_code == 500
    assert response.json()["detail"] == "Simulated Internal Error"


@pytest.mark.asyncio
async def test_update_purpose_no_changes(client: AsyncClient, test_db: AsyncIOMotorDatabase):

    res = await client.post("/api/v1/purposes/create-purpose", json=purpose_create_body(title="NoChangeTest"))
    purpose_id = res.json()["purpose_id"]

    with patch("app.services.purpose_service.PurposeService.update_purpose_data", return_value=None):
        resp = await client.put(f"/api/v1/purposes/update-purpose/{purpose_id}", json={"purpose_description": "New Desc"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Purpose not found or no changes made"


@pytest.mark.asyncio
async def test_get_all_purposes_empty(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    resp = await client.get("/api/v1/purposes/get-all-purposes")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No Purpose Templates found"


@pytest.mark.asyncio
async def test_template_list_internal_error(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    with patch("app.services.purpose_service.PurposeService.get_all_purpose_templates", side_effect=Exception("Template error")):
        resp = await client.get("/api/v1/purposes/templates")
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Template error"


@pytest.mark.asyncio
async def test_list_templates_http_exception_is_propagated(client, test_db):
    with patch(
        "app.services.purpose_service.PurposeService.get_all_purpose_templates", side_effect=HTTPException(status_code=401, detail="Not allowed")
    ):
        response = await client.get("/api/v1/purposes/templates")

        # Because except HTTPException: raise  is executed
        assert response.status_code == 401
        assert response.json()["detail"] == "Not allowed"
