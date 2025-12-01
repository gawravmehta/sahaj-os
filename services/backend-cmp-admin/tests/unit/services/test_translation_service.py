import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.translation_service import TranslationService, supported_languages_map


@pytest.fixture
def mock_df_collection():
    return AsyncMock()


@pytest.fixture
def translation_service(mock_df_collection):
    return TranslationService(df_register_collection=mock_df_collection)


@pytest.fixture
def current_user():
    return {"df_id": "df123"}


@pytest.mark.asyncio
async def test_get_api_key_success(translation_service, mock_df_collection):
    mock_df_collection.find_one.return_value = {"ai": {"openrouter_api_key": "KEY123"}}

    key = await translation_service._get_api_key("df123")
    assert key == "KEY123"


@pytest.mark.asyncio
async def test_get_api_key_df_not_found(translation_service, mock_df_collection):
    mock_df_collection.find_one.return_value = None

    with pytest.raises(HTTPException) as exc:
        await translation_service._get_api_key("df123")

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_api_key_missing_api_key(translation_service, mock_df_collection):
    mock_df_collection.find_one.return_value = {"ai": {}}

    with pytest.raises(HTTPException) as exc:
        await translation_service._get_api_key("df123")

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_translate_all_languages_success(translation_service, mock_df_collection, current_user, monkeypatch):

    mock_df_collection.find_one.return_value = {"ai": {"openrouter_api_key": "KEY123"}}

    async def fake_translate_batch(model, df_id, text, batch):
        return {code: f"{code}_translated" for code in batch}

    monkeypatch.setattr(translation_service, "translate_batch", fake_translate_batch)

    result = await translation_service.translate_all_languages(current_user=current_user, text="Hello", batch_size=6)

    expected_langs = [code for code in supported_languages_map if code != "eng"]

    assert set(result.keys()) == set(expected_langs)
    assert result["hin"] == "hin_translated"


@pytest.mark.asyncio
async def test_translate_all_languages_partial_failure(translation_service, mock_df_collection, current_user, monkeypatch):
    mock_df_collection.find_one.return_value = {"ai": {"openrouter_api_key": "KEY123"}}

    async def fake_translate_batch(model, df_id, text, batch):
        if batch[0] == "asm":
            return {code: f"{code}_ok" for code in batch}
        return None

    monkeypatch.setattr(translation_service, "translate_batch", fake_translate_batch)

    result = await translation_service.translate_all_languages(current_user=current_user, text="Hello", batch_size=5)

    assert "asm" in result
    assert all(code.endswith("_ok") for code in result.values())
    assert len(result) < (len(supported_languages_map) - 1)
