from typing import Any, Dict, Optional
import re
from datetime import datetime, UTC, timedelta

from fastapi import HTTPException, status

from app.schemas.cookie_schema import CookieInDB
from app.schemas.assets_schema import MetaCookies
from app.utils.business_logger import log_business_event
from app.crud.cookie_crud import CookieCrud
from app.core.logger import app_logger
from app.services.assets_service import AssetService
from app.services.cookie_scan_service import CookieScanError, CookieScanService


class CookieManagementService:
    def __init__(
        self,
        crud: CookieCrud,
        asset_service: AssetService,
        cookie_scan_service: CookieScanService,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.asset_service = asset_service
        self.cookie_scan_service = cookie_scan_service
        self.business_logs_collection = business_logs_collection

    def _calculate_expiry(self, lifespan_str: Optional[str]) -> Optional[datetime]:
        """
        Helper function to calculate the expiry date based on a lifespan string.
        Returns a datetime object or None if 'session' or invalid.
        """
        if not lifespan_str or lifespan_str.lower() == "session":
            return None

        match = re.match(r"(\d+)\s*(hour|day|week|month|year)s?", lifespan_str, re.IGNORECASE)
        if not match:
            app_logger.warning(f"Invalid lifespan string format: {lifespan_str}")
            return None

        value = int(match.group(1))
        unit = match.group(2).lower()
        now = datetime.now(UTC)

        if unit == "hour":
            return now + timedelta(hours=value)
        elif unit == "day":
            return now + timedelta(days=value)
        elif unit == "week":
            return now + timedelta(weeks=value)
        elif unit == "month":
            return now + timedelta(days=value * 30)
        elif unit == "year":
            return now + timedelta(days=value * 365)

        return None

    def _convert_epoch_to_datetime(self, epoch_value: Optional[float]) -> Optional[datetime]:
        """
        Convert epoch timestamp to a datetime object (UTC).
        Returns None if epoch_value is invalid or missing.
        """
        try:
            if epoch_value is None:
                return None
            return datetime.fromtimestamp(float(epoch_value), tz=UTC)
        except Exception as e:
            app_logger.error(f"Error converting epoch {epoch_value} to datetime: {e}")
            return None

    def _calculate_lifespan(self, max_age: Optional[int], expires: Optional[float]) -> str:
        """
        Calculates cookie lifespan in human-readable format.
        Priority:
        1. Use maxAge if available.
        2. Otherwise, use expires - current_time.
        3. Default to 'session' if nothing found.
        """

        if max_age is not None:
            seconds = int(max_age)
            return self._format_duration(seconds)

        if expires is not None:
            try:
                expiry_datetime = datetime.fromtimestamp(float(expires), tz=UTC)
                now = datetime.now(UTC)
                diff = (expiry_datetime - now).total_seconds()
                if diff > 0:
                    return self._format_duration(diff)
            except Exception:
                pass

        return "session"

    def _format_duration(self, seconds: float) -> str:
        """
        Converts seconds into a human-readable lifespan.
        Examples:
            3600 -> "1 hour"
            86400 -> "1 day"
            90000 -> "1 day 1 hour"
        """
        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0 and days == 0:

            parts.append(f"{minutes} min{'s' if minutes > 1 else ''}")

        return " ".join(parts) if parts else "less than a minute"

    async def _get_all_published_cookies_for_website(
        self,
        asset_id: str,
        df_id: str,
    ) -> Dict[str, Any]:
        """
        Internal function to retrieve all published cookies for a given website (no pagination, no logs).
        """
        cookies = await self.crud._get_published_cookies_for_website(asset_id, df_id)
        return {
            "total_items": cookies.get("total", 0),
            "cookies": cookies.get("data", []),
        }

    async def scan_website_cookies(self, user: Dict[str, Any], asset_id: str, classify: bool = False) -> Dict[str, Any]:
        """
        Scans and classifies cookies for a given asset.
        """
        df_id = user["df_id"]
        app_logger.info(f"Initiating cookie scan for asset_id: {asset_id}, df_id: {df_id}")

        asset = await self.asset_service.get_asset(asset_id=asset_id, user=user, for_system=True)
        if not asset:
            app_logger.warning(f"Asset not found for asset_id: {asset_id}")
            raise HTTPException(status_code=404, detail="Asset not found")

        usage_url = asset.get("usage_url")
        if not usage_url:
            app_logger.error(f"Asset {asset_id} does not have a usage_url for scanning.")
            raise HTTPException(status_code=400, detail="Asset does not have a usage_url")

        app_logger.info(f"Starting cookie scan for URL: {usage_url}")
        meta_cookies_processing = MetaCookies(scan_status="running")
        await self.asset_service.update_asset_cookie_fields(asset_id=asset_id, user=user, meta_cookies=meta_cookies_processing)

        try:
            scan_results = await self.cookie_scan_service.scan(df_id=df_id, url=usage_url, classify=classify)
            cookies = scan_results.get("cookies", [])
            website_id = asset_id
            created_cookies = []
            skipped_cookies = []
            app_logger.info(f"Cookie scan completed for {usage_url}. Found {len(cookies)} cookies.")

            for cookie in cookies:
                try:
                    is_duplicate = await self.crud.is_duplicate(
                        {
                            "cookie_name": cookie.get("name"),
                            "hostname": cookie.get("domain"),
                            "path": cookie.get("path", "/"),
                        },
                        website_id,
                    )
                    if is_duplicate:
                        skipped_cookies.append(cookie["name"])
                        app_logger.debug(f"Skipping duplicate cookie: {cookie.get('name')} for website {website_id}")
                        continue

                    cookie_model = CookieInDB(
                        cookie_name=cookie.get("name"),
                        description=cookie.get("purpose", ""),
                        hostname=cookie.get("domain"),
                        category=cookie.get("category", "Unknown").lower(),
                        lifespan=self._calculate_lifespan(cookie.get("maxAge"), cookie.get("expires")),
                        path=cookie.get("path", "/"),
                        http_only=cookie.get("httpOnly", False),
                        secure=cookie.get("secure", False),
                        same_site=cookie.get("sameSite"),
                        is_third_party=cookie.get("isThirdParty", False),
                        cookie_status="draft",
                        source="scan",
                        expiry=self._convert_epoch_to_datetime(cookie.get("expires")),
                        website_id=website_id,
                        df_id=df_id,
                        created_by=user["_id"],
                        created_at=datetime.now(UTC),
                        updated_by=None,
                        updated_at=None,
                    )

                    created_cookie = await self.crud.create_cookie(cookie_model.model_dump())
                    created_cookies.append(created_cookie)
                    app_logger.debug(f"Created new cookie: {cookie.get('name')} for website {website_id}")

                except Exception as e:
                    app_logger.error(f"Error creating cookie {cookie.get('name')}: {str(e)}", exc_info=True)

            meta_cookies = MetaCookies(
                scan_frequency="weekly",
                next_scan_date=datetime.now(UTC) + timedelta(weeks=1),
                scan_status="completed",
                cookies_count=len(created_cookies),
            )
            await self.asset_service.update_asset_cookie_fields(asset_id=asset_id, user=user, meta_cookies=meta_cookies)
            app_logger.info(f"Cookie scan process finished for asset_id: {asset_id}. {len(created_cookies)} created, {len(skipped_cookies)} skipped.")

            await log_business_event(
                event_type="SCAN_WEBSITE_COOKIES_COMPLETED",
                user_email=user.get("email"),
                context={
                    "asset_id": asset_id,
                    "website_url": usage_url,
                    "df_id": df_id,
                    "cookies_created_count": len(created_cookies),
                    "cookies_skipped_count": len(skipped_cookies),
                },
                message=f"Website '{usage_url}' scanned successfully. {len(created_cookies)} new cookies created, {len(skipped_cookies)} skipped.",
                business_logs_collection=self.business_logs_collection,
            )
            return created_cookies

        except CookieScanError as e:
            app_logger.error(f"Cookie scanning failed for asset_id {asset_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Cookie scanning failed: {str(e)}")
        except Exception as e:
            app_logger.error(f"Unexpected error during cookie scan for asset_id {asset_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def get_all_websites_with_cookies(self, user: Dict[str, Any], current_page: int = 1, data_per_page: int = 20) -> Dict[str, Any]:
        data = await self.asset_service.get_all_assets(user=user, current_page=current_page, data_per_page=data_per_page, category="Website")

        await log_business_event(
            event_type="LIST_WEBSITES_WITH_COOKIES",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": user.get("df_id"),
                "total_websites": data.get("total_items"),
            },
            message=f"User listed websites with associated cookies. Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )
        return data

    async def create_cookie(self, website_id: str, current_user: dict, cookie_data: Dict[str, Any]) -> CookieInDB:
        """
        Business logic to create a new manual cookie entry, including a duplicate check.
        """
        app_logger.info(f"Attempting to create cookie for website_id: {website_id}, by user: {current_user['_id']}")

        is_duplicate = await self.crud.is_duplicate(cookie_data, website_id)
        if is_duplicate:
            app_logger.warning(
                f"Cookie creation failed due to duplicate: name='{cookie_data.get('cookie_name')}', "
                f"hostname='{cookie_data.get('hostname')}', path='{cookie_data.get('path')}' for website {website_id}"
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A cookie with the same name, hostname, and path already exists.")

        now = datetime.now(UTC)

        cookie_data.update(
            {
                "website_id": website_id,
                "df_id": current_user["df_id"],
                "created_by": current_user["_id"],
                "created_at": now,
                "updated_by": None,
                "updated_at": None,
            }
        )

        if cookie_data.get("lifespan"):
            cookie_data["expiry"] = self._calculate_expiry(cookie_data["lifespan"])

        cookie_model = CookieInDB(**cookie_data)
        created_cookie = await self.crud.create_cookie(cookie_model.model_dump())

        if created_cookie:
            app_logger.info(
                f"Cookie '{cookie_data.get('cookie_name')}' created successfully with ID: {created_cookie['_id']} "
                f"for website '{website_id}' by user '{current_user['_id']}'"
            )
            await log_business_event(
                event_type="CREATE_COOKIE",
                user_email=current_user.get("email"),
                context={
                    "cookie_id": str(created_cookie["_id"]),
                    "cookie_name": cookie_data.get("cookie_name"),
                    "hostname": cookie_data.get("hostname"),
                    "path": cookie_data.get("path"),
                    "website_id": website_id,
                    "df_id": current_user.get("df_id"),
                },
                message=f"Cookie '{cookie_data.get('cookie_name')}' created successfully for website '{website_id}'.",
                business_logs_collection=self.business_logs_collection,
            )
            return created_cookie
        else:
            app_logger.error(f"Failed to create cookie for website_id: {website_id}. No document returned from CRUD operation.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create cookie.")

    async def get_all_cookies_for_website(
        self,
        website_id: str,
        current_user: Dict[str, Any],
        current_page: int = 1,
        data_per_page: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieves all cookies for a given website asynchronously.
        """
        offset = (current_page - 1) * data_per_page
        df_id = current_user["df_id"]
        cookies = await self.crud.get_cookies_for_website(website_id, df_id, offset=offset, limit=data_per_page)
        total_items = cookies.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page
        await log_business_event(
            event_type="LIST_COOKIES",
            user_email=current_user.get("email"),
            context={
                "website_id": website_id,
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": current_user.get("df_id"),
            },
            message=f"User listed cookies for website '{website_id}'. Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "cookies": cookies.get("data", []),
        }

    async def get_cookie(self, cookie_id: str, current_user: Dict[str, Any]) -> CookieInDB:
        """Retrieves a single cookie by its ID, with validation."""
        df_id = current_user["df_id"]
        app_logger.info(f"Fetching cookie with ID: {cookie_id} for df_id: {df_id}")
        cookie_doc = await self.crud.get_cookie_master(cookie_id, df_id)
        await log_business_event(
            event_type="GET_COOKIE",
            user_email=current_user.get("email"),
            context={
                "cookie_id": cookie_id,
                "df_id": df_id,
            },
            message=f"User fetched cookie with ID '{cookie_id}'.",
            business_logs_collection=self.business_logs_collection,
        )
        if not cookie_doc:
            app_logger.warning(f"Cookie with ID: {cookie_id} not found for df_id: {df_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cookie not found.")
        app_logger.info(f"Successfully fetched cookie with ID: {cookie_id}")
        return cookie_doc

    async def update_cookie(self, cookie_id: str, user: Dict[str, Any], update_data: Dict[str, Any]) -> CookieInDB:
        """
        Business logic for updating a cookie asynchronously.
        """
        df_id = user["df_id"]
        app_logger.info(f"Attempting to update cookie with ID: {cookie_id} for df_id: {df_id}")
        existing_cookie = await self.crud.get_cookie_master(cookie_id, df_id)
        if not existing_cookie:
            app_logger.warning(f"Cookie with ID: {cookie_id} not found for df_id: {df_id}")
            raise HTTPException(status_code=404, detail="Asset not found.")

        if existing_cookie["cookie_status"] != "draft":
            app_logger.warning(
                f"Attempted to update cookie {cookie_id} which is not in 'draft' status. Current status: {existing_cookie['cookie_status']}"
            )
            raise HTTPException(
                status_code=400,
                detail="Only Cookies in draft status can be updated.",
            )
        if any(field in update_data for field in ["cookie_name", "hostname", "path"]):
            is_duplicate = await self.crud.is_duplicate(
                update_data,
                website_id=existing_cookie["website_id"],
            )
            if is_duplicate:
                app_logger.warning(
                    f"Cookie update failed due to duplicate: name='{update_data.get('cookie_name', existing_cookie.get('cookie_name'))}', "
                    f"hostname='{update_data.get('hostname', existing_cookie.get('hostname'))}', "
                    f"path='{update_data.get('path', existing_cookie.get('path'))}' for website {existing_cookie['website_id']}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A cookie with the same name, hostname, and path already exists.",
                )
        update_data["updated_at"] = datetime.now(UTC)
        update_data["updated_by"] = user["_id"]
        updated = await self.crud.update_cookie_master(cookie_id, df_id, update_data)
        if updated:
            app_logger.info(f"Cookie {cookie_id} updated successfully by user {user['_id']}. Fields changed: {', '.join(update_data.keys())}")
        else:
            app_logger.error(f"Failed to update cookie {cookie_id} for df_id {df_id}. No document returned from CRUD operation.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update cookie.")

        await log_business_event(
            event_type="UPDATE_COOKIE",
            user_email=user.get("email"),
            context={
                "cookie_id": cookie_id,
                "cookie_name": existing_cookie.get("cookie_name"),
                "website_id": existing_cookie.get("website_id"),
                "df_id": df_id,
                "updated_fields": list(update_data.keys()),
            },
            message=f"Cookie '{existing_cookie.get('cookie_name')}' for website '{existing_cookie.get('website_id')}' updated successfully. Fields changed: {', '.join(update_data.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )
        return updated

    async def delete_cookie(self, cookie_id: str, user: Dict[str, Any]):
        """
        Business logic for deleting a cookie asynchronously.
        """
        df_id = user["df_id"]
        app_logger.info(f"Attempting to delete (archive) cookie with ID: {cookie_id} for df_id: {df_id}")
        existing_cookie = await self.crud.get_cookie_master(cookie_id, df_id)

        if not existing_cookie:
            app_logger.warning(f"Cookie with ID: {cookie_id} not found for df_id: {df_id}. Cannot delete.")
            return None

        if existing_cookie.get("cookie_status") == "archived":
            app_logger.info(f"Cookie with ID: {cookie_id} is already archived. No action taken.")
            return None

        update_cookie = await self.crud.update_cookie_master(
            cookie_id,
            df_id,
            {
                "cookie_status": "archived",
                "updated_at": datetime.now(UTC),
                "updated_by": df_id,
            },
        )
        if update_cookie:
            app_logger.info(f"Cookie '{existing_cookie.get('cookie_name')}' (ID: {cookie_id}) successfully archived by user {user['_id']}.")
        else:
            app_logger.error(f"Failed to archive cookie {cookie_id} for df_id {df_id}. No document returned from CRUD operation.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete cookie (archive).")

        await log_business_event(
            event_type="DELETE_COOKIE",
            user_email=user.get("email"),
            context={
                "cookie_id": cookie_id,
                "cookie_name": existing_cookie.get("cookie_name"),
                "website_id": existing_cookie.get("website_id"),
                "df_id": df_id,
            },
            message=f"Cookie '{existing_cookie.get('cookie_name')}' for website '{existing_cookie.get('website_id')}' soft-deleted (archived) successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return update_cookie

    async def publish_cookie(self, cookie_id: str, user: Dict[str, Any]):
        df_id = user["df_id"]
        app_logger.info(f"Attempting to publish cookie with ID: {cookie_id} for df_id: {df_id}")
        cookie = await self.crud.get_cookie_master(cookie_id, df_id)
        if not cookie:
            app_logger.warning(f"Cookie with ID: {cookie_id} not found for df_id: {df_id}. Cannot publish.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cookie not found or does not belong to the current domain.",
            )
        if cookie["cookie_status"] == "published":
            app_logger.info(f"Cookie with ID: {cookie_id} is already published. No action taken.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cookie is already published.",
            )
        elif cookie["cookie_status"] == "archived":
            app_logger.warning(f"Attempted to publish archived cookie {cookie_id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish an archived Cookie.",
            )
        translations = cookie.get("translations", {})
        if not translations or not isinstance(translations, dict) or not any(v for v in translations.values()):
            app_logger.warning(f"Cookie {cookie_id} has missing or empty translations. Cannot publish.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translations are required and cannot be empty before publishing.",
            )
        update_data = {
            "cookie_status": "published",
            "updated_by": user["_id"],
            "updated_at": datetime.now(UTC),
        }
        updated_cookie = await self.crud.update_cookie_master(cookie_id, df_id, update_data)
        if updated_cookie:
            app_logger.info(f"Cookie '{cookie.get('cookie_name')}' (ID: {cookie_id}) successfully published by user {user['_id']}.")
        else:
            app_logger.error(f"Failed to publish cookie {cookie_id} for df_id {df_id}. No document returned from CRUD operation.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to publish cookie.")

        await log_business_event(
            event_type="PUBLISH_COOKIE",
            user_email=user.get("email"),
            context={
                "cookie_id": cookie_id,
                "cookie_name": cookie.get("cookie_name"),
                "website_id": cookie.get("website_id"),
                "df_id": df_id,
                "user_id": user["_id"],
            },
            message=f"Cookie '{cookie.get('cookie_name')}' for website '{cookie.get('website_id')}' published successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return updated_cookie
