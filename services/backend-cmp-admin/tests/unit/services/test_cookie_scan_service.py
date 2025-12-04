import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from app.services.cookie_scan_service import (
    CookieScanService,
    NormalizedCookie,
    ClassifiedCookie,
    CookieScanError,
)
import httpx
from datetime import datetime, timezone


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_df_register_collection():
    """Mock MongoDB collection for DF register"""
    collection = AsyncMock()
    return collection


@pytest.fixture
def cookie_scan_service(mock_df_register_collection):
    """Create CookieScanService instance with mocked collection"""
    return CookieScanService(df_register_collection=mock_df_register_collection, model="google/gemini-2.0-flash-001")


@pytest.fixture
def sample_normalized_cookies():
    """Sample normalized cookies for testing"""
    return [
        NormalizedCookie(
            name="_ga",
            value="GA1.2.123456789.1234567890",
            domain=".example.com",
            path="/",
            secure=False,
            httpOnly=False,
            sameSite="None",
            expires=1234567890.0,
            source="network",
        ),
        NormalizedCookie(
            name="session_id",
            value="abc123xyz",
            domain="example.com",
            path="/",
            secure=True,
            httpOnly=True,
            sameSite="Lax",
            expires=None,
            source="javascript",
        ),
        NormalizedCookie(
            name="_fbp",
            value="fb.1.1234567890.123456789",
            domain=".example.com",
            path="/",
            secure=False,
            httpOnly=False,
            sameSite="None",
            expires=1234567890.0,
            source="network",
        ),
    ]


# ---------------- TEST _get_api_key ---------------- #


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "df_doc, expected_exception, expected_message",
    [
        # Success case
        (
            {"df_id": "df123", "ai": {"openrouter_api_key": "sk-test-key-123"}},
            None,
            None,
        ),
        # DF not found
        (None, CookieScanError, "Data fiduciary not found"),
        # API key not configured
        (
            {"df_id": "df123", "ai": {}},
            CookieScanError,
            "OpenRouter API key not configured for this DF",
        ),
        # API key is None
        (
            {"df_id": "df123", "ai": {"openrouter_api_key": None}},
            CookieScanError,
            "OpenRouter API key not configured for this DF",
        ),
    ],
)
async def test_get_api_key(cookie_scan_service, mock_df_register_collection, df_doc, expected_exception, expected_message):
    """Test API key retrieval with various scenarios"""
    mock_df_register_collection.find_one.return_value = df_doc

    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            await cookie_scan_service._get_api_key("df123")
        assert expected_message in str(exc_info.value)
    else:
        api_key = await cookie_scan_service._get_api_key("df123")
        assert api_key == "sk-test-key-123"
        mock_df_register_collection.find_one.assert_called_once_with({"df_id": "df123"})


@pytest.mark.asyncio
async def test_get_api_key_no_collection():
    """Test _get_api_key raises error when collection is None"""
    service = CookieScanService(df_register_collection=None)

    with pytest.raises(CookieScanError) as exc_info:
        await service._get_api_key("df123")
    assert "df_register_collection not provided" in str(exc_info.value)


# ---------------- TEST capture_normalized_cookies ---------------- #


@pytest.mark.parametrize(
    "selenium_side_effect, expected_exception",
    [
        (None, None),  # Success case
        (Exception("WebDriver initialization failed"), CookieScanError),  # WebDriver error
    ],
)
def test_capture_normalized_cookies(cookie_scan_service, selenium_side_effect, expected_exception):
    """Test cookie capture with Selenium"""
    with patch.object(cookie_scan_service, "_get_selenium_driver") as mock_driver_factory:
        if selenium_side_effect:
            mock_driver_factory.side_effect = selenium_side_effect

            with pytest.raises(expected_exception):
                cookie_scan_service.capture_normalized_cookies("https://example.com", duration_sec=1)
        else:
            # Mock driver
            mock_driver = MagicMock()
            mock_driver_factory.return_value = mock_driver

            # Mock driver methods
            mock_driver.execute_script.return_value = "complete"
            mock_driver.execute_cdp_cmd.return_value = {
                "cookies": [
                    {
                        "name": "test_cookie",
                        "value": "test_value",
                        "domain": ".example.com",
                        "path": "/",
                        "secure": False,
                        "httpOnly": False,
                        "sameSite": "None",
                        "expires": 1234567890.0,
                    }
                ]
            }

            with patch("time.sleep"):  # Skip actual sleeps
                with patch("time.time", side_effect=[0, 0.5, 1.5]):  # Simulate time passing
                    cookies = cookie_scan_service.capture_normalized_cookies("https://example.com", duration_sec=1)

            assert len(cookies) > 0
            assert all(isinstance(c, NormalizedCookie) for c in cookies)
            mock_driver.quit.assert_called_once()


# ---------------- TEST _heuristic_classify ---------------- #


@pytest.mark.parametrize(
    "cookie_name, expected_category",
    [
        ("_ga", "Analytics"),
        ("session_id", "Essential"),
        ("_fbp", "Marketing"),
        ("ak_bmsc", "Performance"),
        ("random_cookie", "Unknown"),
        ("OptanonConsent", "Essential"),
        ("_gid", "Analytics"),
        ("_uetsid", "Marketing"),
    ],
)
def test_heuristic_classify(cookie_scan_service, cookie_name, expected_category):
    """Test heuristic classification based on cookie names"""
    cookie = NormalizedCookie(
        name=cookie_name, value="test", domain="example.com", path="/", secure=False, httpOnly=False, sameSite="None", expires=None, source="network"
    )

    classified = cookie_scan_service._heuristic_classify([cookie])

    assert len(classified) == 1
    assert isinstance(classified[0], ClassifiedCookie)
    assert classified[0].category == expected_category
    assert classified[0].name == cookie_name


def test_heuristic_classify_multiple_cookies(cookie_scan_service, sample_normalized_cookies):
    """Test heuristic classification with multiple cookies"""
    classified = cookie_scan_service._heuristic_classify(sample_normalized_cookies)

    assert len(classified) == 3
    assert all(isinstance(c, ClassifiedCookie) for c in classified)

    # Check specific classifications
    categories = {c.name: c.category for c in classified}
    assert categories["_ga"] == "Analytics"
    assert categories["session_id"] == "Essential"
    assert categories["_fbp"] == "Marketing"


# ---------------- TEST _ai_classify_batch ---------------- #


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_key, ai_response, expected_fallback",
    [
        # Success case with AI classification
        (
            "sk-test-key",
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"results": [{"name": "_ga", "domain": ".example.com", "category": "Analytics", "purpose": "Google Analytics tracking"}]}'
                        }
                    }
                ]
            },
            False,
        ),
        # No API key - should use heuristic fallback
        (None, None, True),
        # AI request fails - should use heuristic fallback
        ("sk-test-key", None, True),
    ],
)
async def test_ai_classify_batch(
    cookie_scan_service,
    mock_df_register_collection,
    sample_normalized_cookies,
    api_key,
    ai_response,
    expected_fallback,
):
    """Test AI-powered cookie classification with various scenarios"""
    # Mock API key retrieval
    if api_key:
        mock_df_register_collection.find_one.return_value = {"df_id": "df123", "ai": {"openrouter_api_key": api_key}}
    else:
        mock_df_register_collection.find_one.return_value = {"df_id": "df123", "ai": {}}

    if expected_fallback:
        # Should fall back to heuristic
        classified = await cookie_scan_service._ai_classify_batch("df123", sample_normalized_cookies[:1])
        assert len(classified) > 0
        assert all(isinstance(c, ClassifiedCookie) for c in classified)
    else:
        # Mock httpx client for AI request
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.json.return_value = ai_response
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response

            classified = await cookie_scan_service._ai_classify_batch("df123", sample_normalized_cookies[:1])

            assert len(classified) > 0
            assert all(isinstance(c, ClassifiedCookie) for c in classified)
            assert classified[0].category == "Analytics"
            assert "Google Analytics" in classified[0].purpose


@pytest.mark.asyncio
async def test_ai_classify_batch_with_retries(cookie_scan_service, mock_df_register_collection, sample_normalized_cookies):
    """Test AI classification with retry logic on failure"""
    # Mock API key
    mock_df_register_collection.find_one.return_value = {"df_id": "df123", "ai": {"openrouter_api_key": "sk-test-key"}}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # First two calls fail, third succeeds
        mock_response_fail = AsyncMock()
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError("500 Server Error", request=Mock(), response=Mock())

        mock_response_success = AsyncMock()
        mock_response_success.json.return_value = {
            "choices": [
                {"message": {"content": '{"results": [{"name": "_ga", "domain": ".example.com", "category": "Analytics", "purpose": "Tracking"}]}'}}
            ]
        }
        mock_response_success.raise_for_status = MagicMock()

        mock_client.post.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]

        with patch("time.sleep"):  # Skip sleep delays
            classified = await cookie_scan_service._ai_classify_batch("df123", sample_normalized_cookies[:1])

        assert len(classified) > 0
        assert mock_client.post.call_count == 3


# ---------------- TEST classify_cookies ---------------- #


@pytest.mark.asyncio
async def test_classify_cookies_batching(cookie_scan_service, mock_df_register_collection):
    """Test cookie classification with batching logic"""
    # Create 25 cookies to test batching (default batch_size=20)
    cookies = [
        NormalizedCookie(
            name=f"cookie_{i}",
            value=f"value_{i}",
            domain="example.com",
            path="/",
            secure=False,
            httpOnly=False,
            sameSite="None",
            expires=None,
            source="network",
        )
        for i in range(25)
    ]

    # Mock to use heuristic (no API key)
    mock_df_register_collection.find_one.return_value = {"df_id": "df123", "ai": {}}

    classified = await cookie_scan_service.classify_cookies("df123", cookies, batch_size=10)

    assert len(classified) == 25
    assert all(isinstance(c, ClassifiedCookie) for c in classified)


# ---------------- TEST scan ---------------- #


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "classify_enabled, expected_has_category",
    [
        (True, True),  # With classification
        (False, False),  # Without classification
    ],
)
async def test_scan(
    cookie_scan_service,
    mock_df_register_collection,
    classify_enabled,
    expected_has_category,
):
    """Test main scan method with and without classification"""
    # Mock capture method
    with patch.object(cookie_scan_service, "capture_normalized_cookies") as mock_capture:
        mock_capture.return_value = [
            NormalizedCookie(
                name="_ga",
                value="test",
                domain="example.com",
                path="/",
                secure=False,
                httpOnly=False,
                sameSite="None",
                expires=None,
                source="network",
            )
        ]

        # Mock API key for classification
        if classify_enabled:
            mock_df_register_collection.find_one.return_value = {"df_id": "df123", "ai": {}}  # Will use heuristic fallback

        result = await cookie_scan_service.scan(df_id="df123", url="https://example.com", capture_seconds=20, classify=classify_enabled)

        assert result["site"] == "https://example.com"
        assert result["total_cookies"] == 1
        assert "captured_at" in result
        assert len(result["cookies"]) == 1

        if expected_has_category:
            assert "category" in result["cookies"][0]
        else:
            # Without classification, should just have NormalizedCookie fields
            assert result["cookies"][0]["name"] == "_ga"

        mock_capture.assert_called_once_with("https://example.com", duration_sec=20)


@pytest.mark.asyncio
async def test_scan_capture_failure(cookie_scan_service):
    """Test scan method when cookie capture fails"""
    with patch.object(cookie_scan_service, "capture_normalized_cookies") as mock_capture:
        mock_capture.side_effect = CookieScanError("Selenium failed")

        with pytest.raises(CookieScanError) as exc_info:
            await cookie_scan_service.scan(df_id="df123", url="https://example.com", capture_seconds=20, classify=False)

        assert "Selenium failed" in str(exc_info.value)


# ---------------- TEST save_json ---------------- #


def test_save_json(cookie_scan_service, tmp_path):
    """Test saving scan results to JSON file"""
    result = {
        "site": "https://example.com",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "total_cookies": 1,
        "cookies": [{"name": "test", "value": "123"}],
    }

    output_dir = str(tmp_path / "captured_cookies")
    saved_path = cookie_scan_service.save_json(result, output_dir=output_dir)

    assert saved_path.endswith(".json")
    assert "cookies_" in saved_path

    # Verify file exists and contains correct data
    import json

    with open(saved_path, "r") as f:
        loaded = json.load(f)

    assert loaded["site"] == "https://example.com"
    assert loaded["total_cookies"] == 1
