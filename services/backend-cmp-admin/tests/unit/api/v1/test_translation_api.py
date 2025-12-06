from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.deps import get_current_user, get_translation_service
from app.main import app
from app.services.translation_service import TranslationService

client = TestClient(app)
BASE_URL = "/api/v1/translation"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    """Returns a mock user dictionary for authentication dependency."""
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_translation_service():
    """Returns a MagicMock for the TranslationService."""
    service = MagicMock(spec=TranslationService)
    service.translate_all_languages = AsyncMock()
    service.return_transaltion_response = MagicMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_translation_service):
    """Overrides FastAPI dependencies for testing."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_translation_service] = lambda: mock_translation_service
    yield
    # Clear overrides after each test
    app.dependency_overrides = {}


# ---------------- TEST CREATE TRANSLATIONS ---------------- #


@pytest.mark.parametrize(
    "english_text, model, translate_side_effect, translate_return_value, return_translation_response_value, expected_status, expected_response_json",
    [
        # Test case 1: Successful translation
        (
            "Hello",
            "google/gemini-2.0-flash-001",
            None,
            {"es": "Hola", "fr": "Bonjour"},
            {"english_text": "Hello", "translations": {"es": "Hola", "fr": "Bonjour"}},
            200,
            {"english_text": "Hello", "translations": {"es": "Hola", "fr": "Bonjour"}},
        ),
        # Test case 2: HTTPException raised by translate_all_languages
        (
            "Error text",
            "google/gemini-2.0-flash-001",
            HTTPException(status_code=400, detail="Translation service error"),
            None,
            None,
            400,
            {"detail": "Translation service error"},
        ),
        # Test case 3: Generic Exception raised by translate_all_languages
        (
            "Another error",
            "google/gemini-2.0-flash-001",
            Exception("Unexpected internal server error"),
            None,
            None,
            500,
            {"detail": "Unexpected internal server error"},
        ),
        # Test case 4: translate_all_languages returns no translations (empty dict)
        (
            "Empty translations",
            "google/gemini-2.0-flash-001",
            None,
            {},
            None,  # return_transaltion_response is not called
            500,
            {"detail": "Translation service returned no translations."},
        ),
        # Test case 5: translate_all_languages returns None (should be handled as no translations)
        (
            "None translations",
            "google/gemini-2.0-flash-001",
            None,
            None,
            None,  # return_transaltion_response is not called
            500,
            {"detail": "Translation service returned no translations."},
        ),
    ],
)
async def test_create_translations(
    mock_user,
    mock_translation_service,
    english_text,
    model,
    translate_side_effect,
    translate_return_value,
    return_translation_response_value,
    expected_status,
    expected_response_json,
):
    """Tests the /create-translations endpoint for various scenarios."""
    mock_translation_service.translate_all_languages.side_effect = translate_side_effect
    mock_translation_service.translate_all_languages.return_value = translate_return_value
    mock_translation_service.return_transaltion_response.return_value = return_translation_response_value

    url = f"{BASE_URL}/create-translations"
    res = client.post(url, params={"english_text": english_text, "model": model})

    assert res.status_code == expected_status
    assert res.json() == expected_response_json

    # Assert that translate_all_languages was called correctly
    mock_translation_service.translate_all_languages.assert_called_once_with(mock_user, english_text, batch_size=22, model=model)

    # Assert return_transaltion_response was called only on successful translation
    if expected_status == 200:
        mock_translation_service.return_transaltion_response.assert_called_once_with(english_text, translate_return_value)
    else:
        mock_translation_service.return_transaltion_response.assert_not_called()


def test_create_translations_missing_english_text():
    """Tests /create-translations with missing 'english_text' query parameter."""
    url = f"{BASE_URL}/create-translations"
    res = client.post(url, params={"model": "google/gemini-2.0-flash-001"})
    assert res.status_code == 422
    assert "Field required" in res.json()["detail"][0]["msg"]


def test_create_translations_invalid_model():
    """Tests /create-translations with an invalid 'model' query parameter."""
    url = f"{BASE_URL}/create-translations"
    res = client.post(url, params={"english_text": "Test text", "model": "invalid-model"})
    assert res.status_code == 422
    assert "Input should be 'google/gemini-2.0-flash-001'" in res.json()["detail"][0]["msg"]
