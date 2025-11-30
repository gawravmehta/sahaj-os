# tests/integration/test_assets.py
import pytest
from fastapi.testclient import TestClient

BASE = "/api/v1/assets"


# ------------------------------- CREATE ASSET ----------------------------------

def test_create_asset_success(client: TestClient):
    body = {
        "asset_name": "TestAsset",
        "category": "Website",
        "usage_url": "https://example.com"
    }

    res = client.post(f"{BASE}/create-asset", json=body)

    assert res.status_code == 201
    data = res.json()

    assert data["asset_id"]                      # should exist
    assert data["asset_name"] == "TestAsset"
    assert data["usage_url"] == "https://example.com"


def test_create_asset_duplicate(client: TestClient):
    body = {
        "asset_name": "DuplicateAsset",
        "category": "Website",
        "usage_url": "https://example.com"
    }

    # first insert
    res1 = client.post(f"{BASE}/create-asset", json=body)
    assert res1.status_code == 201

    # duplicate insert
    res2 = client.post(f"{BASE}/create-asset", json=body)
    assert res2.status_code == 409


def test_create_asset_validation_error(client: TestClient):
    invalid_body = {"wrong": "field"}

    res = client.post(f"{BASE}/create-asset", json=invalid_body)

    assert res.status_code == 422
