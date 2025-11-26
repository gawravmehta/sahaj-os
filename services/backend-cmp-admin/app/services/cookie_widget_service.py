from datetime import timedelta
from typing import Any, Dict
from app.cmp_widget.generator import WidgetBuilder
from app.services.cookie_service import CookieManagementService
from app.schemas.assets_schema import MetaCookies
from app.services.data_fiduciary_service import DataFiduciaryService
from app.core.config import settings
import re
import uuid
import mimetypes
import os
import asyncio
from app.core.logger import get_logger
from app.utils.business_logger import log_business_event

logger = get_logger("api.widget_service")


class WidgetService:
    """
    Handles the business logic for managing widget builds.
    """

    def __init__(
        self,
        cookie_service: CookieManagementService,
        df_service: DataFiduciaryService,
    ):
        self.cookie_service = cookie_service
        self.df_service = df_service

    def _normalize_expiry(self, lifespan: Any) -> Dict[str, Any]:
        if isinstance(lifespan, dict):
            value = lifespan.get("value", 1)
            unit = lifespan.get("unit", "day")

        elif isinstance(lifespan, str):
            lifespan_lower = lifespan.strip().lower()
            if lifespan_lower == "session":
                return {"value": 0, "unit": "day"}
            match = re.search(r"(\d+)\s*([a-zA-Z]+)", lifespan_lower)
            if match:
                value, unit = int(match.group(1)), match.group(2)
            else:
                value, unit = 1, "day"

        elif isinstance(lifespan, (int, float)):
            value, unit = lifespan, "day"
        else:
            value, unit = 1, "day"

        unit = unit.lower().rstrip("s")
        return {"value": value, "unit": unit}

    async def prepare_widget_config(self, user: Dict[str, Any], asset_id: str, s3_service) -> Dict[str, Any]:
        logger.info(
            f"Preparing widget configuration for asset_id={asset_id}",
            extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id},
        )

        cookies_result = await self.cookie_service._get_all_published_cookies_for_website(asset_id, user["df_id"])

        if not cookies_result.get("cookies") or cookies_result.get("total_items", 0) == 0:
            logger.warning(
                f"No published cookies found for asset_id={asset_id}, df_id={user['df_id']}",
                extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id},
            )
            await log_business_event(
                event_type="WIDGET_BUILD_FAILED_NO_COOKIES",
                user_email=user.get("email", "system"),
                context={"asset_id": asset_id, "df_id": user.get("df_id")},
                message="No published cookies found for website, widget build aborted.",
                business_logs_collection="widget_events",
                log_level="WARN",
            )
            return {"status": "error", "message": "No published cookies found for this website."}

        logger.info(
            f"Fetching DF info for df_id={user['df_id']}", extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id}
        )
        df_info = await self.df_service.get_details(df_id=user["df_id"])
        df_info = df_info["org_info"]

        cookies_data: Dict[str, list] = {}
        for cookie in cookies_result.get("cookies", []):
            category = cookie.get("category", "other").lower()
            expiry = self._normalize_expiry(cookie.get("lifespan", {"value": 1, "unit": "year"}))
            cookies_data.setdefault(category, []).append(
                {
                    "name": cookie.get("cookie_name"),
                    "description": cookie.get("translations", {}),
                    "domain": cookie.get("hostname", ""),
                    "expiry": expiry,
                }
            )

        config = {
            "COOKIES_DATA": cookies_data,
            "WIDGET_NAME": asset_id,
            "INPUT_JSON_FILE": "app/cmp_widget/static_cookie_translation.json",
            "DF_NAME": df_info.get("name", "Default Firm Name"),
            "PRIVACY_URL": df_info.get("privacy_policy_url", ""),
            "COOKIE_URL": df_info.get("cookie_policy_url", ""),
            "LOGO_URL": df_info.get("df_logo_url"),
            "SRC_TEMPLATE_PATH": "app/cmp_widget/src/template.html",
            "COOKIE_CONSENT_URL": settings.COOKIE_CONSENT_URL,
        }

        logger.info(
            f"Building and uploading widget for {asset_id}", extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id}
        )
        build_result = await self.build_production_widget(config, s3_service)

        if build_result.get("status") == "success" and build_result.get("url"):
            meta_cookies_update = MetaCookies(script_url=build_result["url"])
            await self.cookie_service.asset_service.update_asset_cookie_fields(asset_id=asset_id, user=user, meta_cookies=meta_cookies_update)
            logger.info(
                f"Widget build and upload successful for asset_id={asset_id}",
                extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id, "widget_url": build_result.get("url")},
            )
            await log_business_event(
                event_type="WIDGET_BUILD_SUCCESS",
                user_email=user.get("email", "system"),
                context={"asset_id": asset_id, "df_id": user.get("df_id"), "widget_url": build_result.get("url")},
                message="Cookie widget built and uploaded successfully.",
                business_logs_collection="widget_events",
                log_level="INFO",
            )
            return build_result.get("url")

        logger.error(
            f"Widget build or upload failed for asset_id={asset_id}",
            extra={"user_id": user.get("id"), "df_id": user.get("df_id"), "asset_id": asset_id, "build_result": build_result},
        )
        await log_business_event(
            event_type="WIDGET_BUILD_FAILED_GENERIC",
            user_email=user.get("email", "system"),
            context={"asset_id": asset_id, "df_id": user.get("df_id"), "build_result_message": build_result.get("message")},
            message="Cookie widget build or upload failed.",
            business_logs_collection="widget_events",
            log_level="ERROR",
            error_details=str(build_result),
        )
        return build_result

    async def build_production_widget(self, config: Dict[str, Any], s3_service) -> Dict[str, Any]:
        widget_name = config.get("WIDGET_NAME", "unknown_widget")
        logger.info(f"Initializing WidgetBuilder for {widget_name}", extra={"widget_name": widget_name})
        builder = WidgetBuilder(config)
        try:
            loop = asyncio.get_running_loop()
            logger.info("Starting build process...", extra={"widget_name": widget_name})
            await loop.run_in_executor(None, builder.build)
            logger.info("Build process completed.", extra={"widget_name": widget_name})

            local_path = f"app/cmp_widget/dist/{widget_name}-cmp-widget.iife.js"
            if not os.path.exists(local_path):
                logger.error(f"Built file not found at {local_path}", extra={"widget_name": widget_name, "local_path": local_path})
                raise FileNotFoundError(f"Built file not found at {local_path}")
            logger.info(f"Built file found at {local_path}", extra={"widget_name": widget_name, "local_path": local_path})

            filename = f"{widget_name}_.js"
            content_type = mimetypes.guess_type(local_path)[0] or "text/js"
            logger.info(
                f"Uploading to S3 bucket {settings.COOKIE_CONSENT_BUCKET} as {filename} (content_type={content_type})",
                extra={"widget_name": widget_name, "bucket": settings.COOKIE_CONSENT_BUCKET, "filename": filename, "content_type": content_type},
            )

            s3_service.fput_object(
                bucket_name=settings.COOKIE_CONSENT_BUCKET,
                object_name=filename,
                file_path=local_path,
                content_type=content_type,
            )

            file_url = f"https://{settings.S3_URL}/{settings.COOKIE_CONSENT_BUCKET}/{filename}"

            logger.info(f"Widget uploaded and accessible at {file_url}", extra={"widget_name": widget_name, "file_url": file_url})

            return {
                "status": "success",
                "message": f"Widget '{widget_name}' built and uploaded successfully.",
                "url": file_url,
            }

        except Exception as e:
            logger.error(f"Error during widget build/upload for {widget_name}: {e}", exc_info=True, extra={"widget_name": widget_name})
            return {"status": "error", "message": str(e), "url": None}
