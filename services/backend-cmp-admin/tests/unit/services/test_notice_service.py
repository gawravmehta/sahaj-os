import json
import pytest
from unittest.mock import patch, mock_open
from app.services.notice_service import NoticeService


@pytest.fixture
def service():
    return NoticeService(
        supported_languages_map={"en": "English", "hi": "Hindi"},
        static_json_file="static.json",
        categories_translation_file="categories.json",
    )


@pytest.fixture
def mock_static_json():
    return [
        {"language": "en", "title": "Notice EN"},
        {"language": "hi", "title": "Notice HI"},
    ]


@pytest.fixture
def mock_categories_json():
    return [
        {"eng": "finance", "en": "Finance", "hi": "वित्त"},
        {"eng": "health", "en": "Health", "hi": "स्वास्थ्य"},
    ]


@pytest.fixture
def deeply_enriched_data():
    return [
        {
            "de_obj": {
                "_id": "de1",
                "de_name": "Email",
                "de_retention_period": "1 year",
                "translations": {"hi": "ईमेल"},
            },
            "purposes": [
                {
                    "_id": "p1",
                    "purpose_title": "Marketing",
                    "purpose_category": "finance",
                    "consent_time_period": "6 months",
                    "translations": {"hi": "मार्केटिंग"},
                    "data_processor_details": [{"id": "dpr1"}],
                    "data_elements": [
                        {
                            "de_id": "de1",
                            "service_message": "Service email",
                            "legal_message": "Legal email",
                        }
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def translated_audio():
    return [
        {"audio_language": "English", "audio_url": "http://audio-en.com"},
        {"audio_language": "hi", "audio_url": "http://audio-hi.com"},
    ]


# -------------------------------------------------------------------
# TEST: build_notice_data
# -------------------------------------------------------------------

@patch("builtins.open")
@pytest.mark.asyncio
async def test_build_notice_data_success(
    mock_open_func,
    service,
    mock_static_json,
    mock_categories_json,
    deeply_enriched_data,
    translated_audio,
):
    # Mock file reads
    mock_open_func.side_effect = [
        mock_open(read_data=json.dumps(mock_static_json)).return_value,
        mock_open(read_data=json.dumps(mock_categories_json)).return_value,
    ]

    result = await service.build_notice_data(deeply_enriched_data, translated_audio)

    assert "en" in result
    assert "hi" in result

    en_data = result["en"]
    hi_data = result["hi"]

    # audio
    assert en_data["audio_file_url"] == "http://audio-en.com"
    assert hi_data["audio_file_url"] == "http://audio-hi.com"

    # DE data merged
    assert en_data["data_elements"][0]["de_id"] == "de1"
    assert hi_data["data_elements"][0]["title"] == "ईमेल"  # translated

    # category translation
    assert en_data["data_elements"][0]["consents"][0]["purpose_category"] == "Finance"
    assert hi_data["data_elements"][0]["consents"][0]["purpose_category"] == "वित्त"


# -------------------------------------------------------------------
# TEST: render_html
# -------------------------------------------------------------------

@patch("builtins.open", new_callable=mock_open, read_data="<html>// {{ NOTICE_DATA }} {{ df_name }}</html>")
def test_render_html_single(mock_file, service):
    consolidated = {"en": {"title": "Test"}}
    output = service.render_html(consolidated, "Test DF", "single")

    assert "Test DF" in output
    assert json.dumps(consolidated, indent=4, ensure_ascii=False) in output


@patch("builtins.open", new_callable=mock_open, read_data="<html>// {{ NOTICE_DATA }} {{ df_name }}</html>")
def test_render_html_multiple(mock_file, service):
    output = service.render_html({"en": {}}, "DF", "multiple")
    assert "DF" in output
