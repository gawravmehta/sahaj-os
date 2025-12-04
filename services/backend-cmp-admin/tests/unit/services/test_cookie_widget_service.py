import os
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.services.cookie_widget_service import WidgetService

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_cookie_service():
    """Mock CookieManagementService"""
    service = MagicMock()
    service._get_all_published_cookies_for_website = AsyncMock()
    service.asset_service = MagicMock()
    service.asset_service.update_asset_cookie_fields = AsyncMock()
    return service


@pytest.fixture
def mock_df_service():
    """Mock DataFiduciaryService"""
    service = MagicMock()
    service.get_details = AsyncMock()
    return service


@pytest.fixture
def mock_s3_service():
    """Mock S3 service"""
    service = MagicMock()
    service.fput_object = MagicMock()
    return service


@pytest.fixture
def widget_service(mock_cookie_service, mock_df_service):
    """Create WidgetService instance with mocked dependencies"""
    return WidgetService(cookie_service=mock_cookie_service, df_service=mock_df_service)


@pytest.fixture
def mock_user():
    """Mock user object"""
    return {"_id": "u1", "id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def sample_cookies():
    """Sample published cookies for testing"""
    return [
        {
            "cookie_name": "_ga",
            "category": "analytics",
            "hostname": ".example.com",
            "lifespan": {"value": 2, "unit": "year"},
            "translations": {"eng": "Google Analytics cookie"},
        },
        {
            "cookie_name": "session_id",
            "category": "essential",
            "hostname": "example.com",
            "lifespan": "session",
            "translations": {"eng": "Session identifier"},
        },
        {
            "cookie_name": "_fbp",
            "category": "marketing",
            "hostname": ".example.com",
            "lifespan": "90 days",
            "translations": {"eng": "Facebook Pixel"},
        },
    ]


@pytest.fixture
def sample_df_info():
    """Sample data fiduciary information"""
    return {
        "df": {
            "org_info": {
                "name": "Test Organization",
                "privacy_policy_url": "https://example.com/privacy",
                "cookie_policy_url": "https://example.com/cookies",
                "df_logo_url": "https://example.com/logo.png",
            }
        }
    }


# ---------------- TEST _normalize_expiry ---------------- #


@pytest.mark.parametrize(
    "lifespan_input, expected_output",
    [
        # Dict input
        ({"value": 30, "unit": "days"}, {"value": 30, "unit": "day"}),
        ({"value": 1, "unit": "year"}, {"value": 1, "unit": "year"}),
        ({"value": 2, "unit": "months"}, {"value": 2, "unit": "month"}),
        # String input - session
        ("session", {"value": 0, "unit": "day"}),
        ("Session", {"value": 0, "unit": "day"}),
        # String input - with numbers
        ("90 days", {"value": 90, "unit": "day"}),
        ("1 year", {"value": 1, "unit": "year"}),
        ("2years", {"value": 2, "unit": "year"}),
        ("30days", {"value": 30, "unit": "day"}),
        # String input - no match (fallback)
        ("invalid", {"value": 1, "unit": "day"}),
        # Numeric input
        (30, {"value": 30, "unit": "day"}),
        (1.5, {"value": 1.5, "unit": "day"}),
        # Other types (fallback)
        (None, {"value": 1, "unit": "day"}),
        ([], {"value": 1, "unit": "day"}),
    ],
)
def test_normalize_expiry(widget_service, lifespan_input, expected_output):
    """Test expiry normalization with various input formats"""
    result = widget_service._normalize_expiry(lifespan_input)
    assert result == expected_output


def test_normalize_expiry_removes_plural(widget_service):
    """Test that normalize_expiry removes plural 's' from units"""
    result = widget_service._normalize_expiry({"value": 10, "unit": "days"})
    assert result["unit"] == "day"

    result = widget_service._normalize_expiry("5 years")
    assert result["unit"] == "year"


# ---------------- TEST prepare_widget_config ---------------- #


@pytest.mark.asyncio
async def test_prepare_widget_config_success(
    widget_service,
    mock_cookie_service,
    mock_df_service,
    mock_s3_service,
    mock_user,
    sample_cookies,
    sample_df_info,
):
    """Test successful widget configuration preparation"""
    # Mock cookie service response
    mock_cookie_service._get_all_published_cookies_for_website.return_value = {
        "cookies": sample_cookies,
        "total_items": 3,
    }

    # Mock DF service response
    mock_df_service.get_details.return_value = sample_df_info

    # Mock build_production_widget
    with patch.object(widget_service, "build_production_widget", new_callable=AsyncMock) as mock_build:
        mock_build.return_value = {
            "status": "success",
            "url": "https://s3.example.com/bucket/asset123_.js",
            "message": "Widget built successfully",
        }

        result = await widget_service.prepare_widget_config(user=mock_user, asset_id="asset123", s3_service=mock_s3_service)

        # Verify result
        assert result == "https://s3.example.com/bucket/asset123_.js"

        # Verify cookie service was called
        mock_cookie_service._get_all_published_cookies_for_website.assert_called_once_with("asset123", "df123")

        # Verify DF service was called
        mock_df_service.get_details.assert_called_once_with(df_id="df123", user=mock_user)

        # Verify build was called with correct config
        assert mock_build.called
        config = mock_build.call_args[0][0]
        assert config["WIDGET_NAME"] == "asset123"
        assert config["DF_NAME"] == "Test Organization"
        assert "analytics" in config["COOKIES_DATA"]
        assert "essential" in config["COOKIES_DATA"]
        assert "marketing" in config["COOKIES_DATA"]

        # Verify asset was updated
        mock_cookie_service.asset_service.update_asset_cookie_fields.assert_called_once()


@pytest.mark.asyncio
async def test_prepare_widget_config_no_cookies(widget_service, mock_cookie_service, mock_user):
    """Test widget config preparation when no cookies are found"""
    # Mock empty cookies response
    mock_cookie_service._get_all_published_cookies_for_website.return_value = {
        "cookies": [],
        "total_items": 0,
    }

    result = await widget_service.prepare_widget_config(user=mock_user, asset_id="asset123", s3_service=None)

    assert result["status"] == "error"
    assert "No published cookies found" in result["message"]


@pytest.mark.asyncio
async def test_prepare_widget_config_build_failure(
    widget_service,
    mock_cookie_service,
    mock_df_service,
    mock_s3_service,
    mock_user,
    sample_cookies,
    sample_df_info,
):
    """Test widget config preparation when build fails"""
    # Mock services
    mock_cookie_service._get_all_published_cookies_for_website.return_value = {
        "cookies": sample_cookies,
        "total_items": 3,
    }
    mock_df_service.get_details.return_value = sample_df_info

    # Mock build failure
    with patch.object(widget_service, "build_production_widget", new_callable=AsyncMock) as mock_build:
        mock_build.return_value = {
            "status": "error",
            "message": "Build failed",
            "url": None,
        }

        result = await widget_service.prepare_widget_config(user=mock_user, asset_id="asset123", s3_service=mock_s3_service)

        assert result["status"] == "error"
        assert result["message"] == "Build failed"

        # Verify asset was NOT updated
        mock_cookie_service.asset_service.update_asset_cookie_fields.assert_not_called()


@pytest.mark.asyncio
async def test_prepare_widget_config_cookies_data_structure(
    widget_service,
    mock_cookie_service,
    mock_df_service,
    mock_s3_service,
    mock_user,
    sample_cookies,
    sample_df_info,
):
    """Test that cookies data is structured correctly by category"""
    mock_cookie_service._get_all_published_cookies_for_website.return_value = {
        "cookies": sample_cookies,
        "total_items": 3,
    }
    mock_df_service.get_details.return_value = sample_df_info

    with patch.object(widget_service, "build_production_widget", new_callable=AsyncMock) as mock_build:
        mock_build.return_value = {
            "status": "success",
            "url": "https://example.com/widget.js",
        }

        await widget_service.prepare_widget_config(user=mock_user, asset_id="asset123", s3_service=mock_s3_service)

        config = mock_build.call_args[0][0]
        cookies_data = config["COOKIES_DATA"]

        # Check structure
        assert "analytics" in cookies_data
        assert "essential" in cookies_data
        assert "marketing" in cookies_data

        # Check analytics cookie
        assert len(cookies_data["analytics"]) == 1
        assert cookies_data["analytics"][0]["name"] == "_ga"
        assert cookies_data["analytics"][0]["expiry"]["value"] == 2
        assert cookies_data["analytics"][0]["expiry"]["unit"] == "year"

        # Check essential cookie
        assert len(cookies_data["essential"]) == 1
        assert cookies_data["essential"][0]["name"] == "session_id"
        assert cookies_data["essential"][0]["expiry"]["value"] == 0
        assert cookies_data["essential"][0]["expiry"]["unit"] == "day"

        # Check marketing cookie
        assert len(cookies_data["marketing"]) == 1
        assert cookies_data["marketing"][0]["name"] == "_fbp"
        assert cookies_data["marketing"][0]["expiry"]["value"] == 90
        assert cookies_data["marketing"][0]["expiry"]["unit"] == "day"


# ---------------- TEST build_production_widget ---------------- #


@pytest.mark.asyncio
async def test_build_production_widget_success(widget_service, mock_s3_service, tmp_path):
    """Test successful widget build and upload"""
    config = {
        "WIDGET_NAME": "test_widget",
        "COOKIES_DATA": {"essential": []},
        "DF_NAME": "Test Org",
        "PRIVACY_URL": "https://example.com/privacy",
        "COOKIE_URL": "https://example.com/cookies",
        "LOGO_URL": "https://example.com/logo.png",
        "INPUT_JSON_FILE": "app/cmp_widget/static_cookie_translation.json",
        "SRC_TEMPLATE_PATH": "app/cmp_widget/src/template.html",
        "COOKIE_CONSENT_URL": "https://consent.example.com",
    }

    # Create a fake built file
    dist_dir = tmp_path / "app" / "cmp_widget" / "dist"
    dist_dir.mkdir(parents=True)
    fake_file = dist_dir / "test_widget-cmp-widget.iife.js"
    fake_file.write_text("// widget code")

    with patch("app.cmp_widget.generator.WidgetBuilder") as mock_builder_class:
        mock_builder = MagicMock()
        mock_builder_class.return_value = mock_builder

        with patch("os.path.exists", return_value=True):
            with patch("app.services.cookie_widget_service.settings") as mock_settings:
                mock_settings.COOKIE_CONSENT_BUCKET = "consent-bucket"
                mock_settings.S3_URL = "s3.example.com"

                result = await widget_service.build_production_widget(config=config, s3_service=mock_s3_service)

        assert result["status"] == "success"
        assert "test_widget" in result["message"]
        assert "test_widget_.js" in result["url"]
        assert "s3.example.com/consent-bucket/test_widget_.js" in result["url"]

        # Verify builder was called
        mock_builder.build.assert_called_once()

        # Verify S3 upload was called
        mock_s3_service.fput_object.assert_called_once()


@pytest.mark.asyncio
async def test_build_production_widget_file_not_found(widget_service, mock_s3_service):
    """Test widget build when output file is not found"""
    config = {
        "WIDGET_NAME": "test_widget",
        "COOKIES_DATA": {"essential": []},
        "DF_NAME": "Test Org",
        "PRIVACY_URL": "https://example.com/privacy",
        "COOKIE_URL": "https://example.com/cookies",
        "LOGO_URL": "https://example.com/logo.png",
        "INPUT_JSON_FILE": "app/cmp_widget/static_cookie_translation.json",
        "SRC_TEMPLATE_PATH": "app/cmp_widget/src/template.html",
        "COOKIE_CONSENT_URL": "https://consent.example.com",
    }

    with patch("app.cmp_widget.generator.WidgetBuilder") as mock_builder_class:
        mock_builder = MagicMock()
        mock_builder_class.return_value = mock_builder

        with patch("os.path.exists", return_value=False):
            result = await widget_service.build_production_widget(config=config, s3_service=mock_s3_service)

    assert result["status"] == "error"
    assert "not found" in result["message"].lower()
    assert result["url"] is None

    # Verify S3 upload was NOT called
    mock_s3_service.fput_object.assert_not_called()


@pytest.mark.asyncio
async def test_build_production_widget_build_exception(widget_service, mock_s3_service):
    """Test widget build when builder raises exception"""
    config = {
        "WIDGET_NAME": "test_widget",
        "COOKIES_DATA": {"essential": []},
        "DF_NAME": "Test Org",
        "PRIVACY_URL": "https://example.com/privacy",
        "COOKIE_URL": "https://example.com/cookies",
        "LOGO_URL": "https://example.com/logo.png",
        "INPUT_JSON_FILE": "app/cmp_widget/static_cookie_translation.json",
        "SRC_TEMPLATE_PATH": "app/cmp_widget/src/template.html",
        "COOKIE_CONSENT_URL": "https://consent.example.com",
    }

    with patch("app.cmp_widget.generator.WidgetBuilder") as mock_builder_class:
        mock_builder = MagicMock()
        mock_builder.build.side_effect = Exception("Build process failed")
        mock_builder_class.return_value = mock_builder

        result = await widget_service.build_production_widget(config=config, s3_service=mock_s3_service)

    assert result["status"] == "error"
    assert "Build process failed" in result["message"]
    assert result["url"] is None


@pytest.mark.asyncio
async def test_build_production_widget_s3_exception(widget_service, mock_s3_service):
    """Test widget build when S3 upload fails"""
    config = {
        "WIDGET_NAME": "test_widget",
        "COOKIES_DATA": {"essential": []},
        "DF_NAME": "Test Org",
        "PRIVACY_URL": "https://example.com/privacy",
        "COOKIE_URL": "https://example.com/cookies",
        "LOGO_URL": "https://example.com/logo.png",
        "INPUT_JSON_FILE": "app/cmp_widget/static_cookie_translation.json",
        "SRC_TEMPLATE_PATH": "app/cmp_widget/src/template.html",
        "COOKIE_CONSENT_URL": "https://consent.example.com",
    }

    # Mock S3 service to raise exception
    mock_s3_service.fput_object.side_effect = Exception("S3 upload failed")

    with patch("app.cmp_widget.generator.WidgetBuilder") as mock_builder_class:
        mock_builder = MagicMock()
        mock_builder_class.return_value = mock_builder

        with patch("os.path.exists", return_value=True):
            with patch("app.services.cookie_widget_service.settings") as mock_settings:
                mock_settings.COOKIE_CONSENT_BUCKET = "consent-bucket"
                mock_settings.S3_URL = "s3.example.com"

                result = await widget_service.build_production_widget(config=config, s3_service=mock_s3_service)

    assert result["status"] == "error"
    assert "S3 upload failed" in result["message"]
    assert result["url"] is None
