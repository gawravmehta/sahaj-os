import os
import json
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

import httpx


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from motor.motor_asyncio import AsyncIOMotorCollection


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cookie_scanner")


@dataclass
class NormalizedCookie:
    name: str
    value: str
    domain: str
    path: str = "/"
    secure: bool = False
    httpOnly: bool = False
    sameSite: str = "None"
    expires: Optional[float] = None
    source: str = "network"


@dataclass
class ClassifiedCookie(NormalizedCookie):
    category: str = "Unknown"
    purpose: str = ""


class CookieScanError(Exception):
    pass


class CookieScanService:
    def __init__(self, df_register_collection: AsyncIOMotorCollection, model: Optional[str] = "google/gemini-2.0-flash-001"):
        self.df_register_collection = df_register_collection
        self.ai_model_name = model
        self.openrouter_base_url = "https://openrouter.ai/api/v1"

    async def _get_api_key(self, df_id: str) -> str:
        if self.df_register_collection is None:
            raise CookieScanError("df_register_collection not provided")
        df_doc = await self.df_register_collection.find_one({"df_id": df_id})
        if not df_doc:
            raise CookieScanError("Data fiduciary not found")

        openrouter_key = df_doc.get("ai", {}).get("openrouter_api_key")
        if not openrouter_key:
            raise CookieScanError("OpenRouter API key not configured for this DF")
        return openrouter_key

    def _get_selenium_driver(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        if os.getenv("HEADLESS", "1") != "0":
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        try:
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Page.enable", {})
            return driver
        except Exception as e:
            logger.exception("Failed to initialize Selenium WebDriver")
            raise CookieScanError(f"WebDriver initialization failed: {e}")

    def _find_and_accept_cookies(self, driver: webdriver.Chrome) -> bool:
        selectors: List[Tuple[str, str]] = [
            ("ID", "onetrust-accept-btn-handler"),
            ("CSS_SELECTOR", "button[aria-label*='cookie'] i"),
            ("CSS_SELECTOR", "button[class*='cookie']"),
            ("CSS_SELECTOR", "button[class*='consent']"),
            ("CSS_SELECTOR", "a[class*='cookie']"),
            ("CSS_SELECTOR", "a[class*='consent']"),
            ("CSS_SELECTOR", "div[class*='cookie'] button"),
            ("XPATH", "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]"),
            ("XPATH", "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]"),
            ("XPATH", "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]"),
            ("XPATH", "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]"),
        ]

        for by, selector in selectors:
            try:
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((getattr(By, by), selector)))
                driver.execute_script("arguments[0].click();", element)
                logger.info(f"Accepted cookies using {by}: {selector}")
                time.sleep(2)
                return True
            except Exception:
                continue

        logger.info("No cookie consent banner found")
        return False

    def _collect_cookies_once(self, driver: webdriver.Chrome) -> Dict[str, NormalizedCookie]:
        all_norm: Dict[str, NormalizedCookie] = {}

        try:
            resp = driver.execute_cdp_cmd("Network.getAllCookies", {})
            for c in resp.get("cookies", []):
                key = f"{c['name']}||{c.get('domain','')}||{c.get('path','/')}"
                all_norm[key] = NormalizedCookie(
                    name=c["name"],
                    value=c.get("value", ""),
                    domain=c.get("domain", driver.execute_script("return location.hostname")),
                    path=c.get("path", "/"),
                    secure=c.get("secure", False),
                    httpOnly=c.get("httpOnly", False),
                    sameSite=c.get("sameSite", "None") or "None",
                    expires=c.get("expires", None),
                    source="network",
                )
        except Exception:
            logger.debug("Network.getAllCookies failed", exc_info=True)

        try:
            js_cookie_str = driver.execute_script("return document.cookie")
            if js_cookie_str:
                host = driver.execute_script("return location.hostname")
                for kv in js_cookie_str.split("; "):
                    if "=" in kv:
                        name, value = kv.split("=", 1)
                        key = f"{name}||{host}||/"
                        if key not in all_norm:
                            all_norm[key] = NormalizedCookie(
                                name=name,
                                value=value,
                                domain=host,
                                path="/",
                                secure=False,
                                httpOnly=False,
                                sameSite="None",
                                expires=None,
                                source="javascript",
                            )
        except Exception:
            logger.debug("Reading document.cookie failed", exc_info=True)

        return all_norm

    def _scroll_page(self, driver: webdriver.Chrome):
        scroll_script = "window.scrollBy(0, window.innerHeight);" "return document.body.scrollHeight - window.scrollY - window.innerHeight;"
        remaining = driver.execute_script(scroll_script)
        loops = 0
        while remaining and remaining > 0 and loops < 30:
            time.sleep(1)
            remaining = driver.execute_script(scroll_script)
            loops += 1

    def capture_normalized_cookies(self, url: str, duration_sec: int = 60) -> List[NormalizedCookie]:
        driver = self._get_selenium_driver()
        try:
            logger.info(f"Opening {url}")
            driver.get(url)
            WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")

            self._find_and_accept_cookies(driver)

            self._scroll_page(driver)

            start = time.time()
            collected: Dict[str, NormalizedCookie] = {}
            while time.time() - start < duration_sec:
                collected.update(self._collect_cookies_once(driver))
                time.sleep(2)

            collected.update(self._collect_cookies_once(driver))

            cookies_list = [asdict(c) for c in collected.values()]
            logger.info(f"Captured {len(cookies_list)} cookies")
            return [NormalizedCookie(**c) for c in cookies_list]
        except Exception as e:
            raise CookieScanError(f"Capture failed: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    async def _ai_classify_batch(self, df_id: str, cookies: List[NormalizedCookie]) -> List[ClassifiedCookie]:
        openrouter_key = await self._get_api_key(df_id)
        if not openrouter_key:
            logger.warning("No OpenRouter API key found. Applying heuristic fallback.")
            return self._heuristic_classify(cookies)

        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
        }

        cookies_payload = [
            {
                "name": c.name,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "httpOnly": c.httpOnly,
                "sameSite": c.sameSite,
            }
            for c in cookies
        ]

        system_msg = (
            "You are a privacy compliance assistant.\n"
            "Return ONLY a JSON array, nothing else.\n"
            "For each input cookie, output an object with keys: name, domain, category, purpose.\n"
            "category must be one of: Essential, Functional, Analytics, Marketing, Performance, Security, Unknown.\n"
            "purpose is a short one-line human explanation."
        )
        user_msg = "Classify these cookies by name/domain. If unsure, use Unknown.\n\n" + json.dumps(cookies_payload, ensure_ascii=False)

        body = {
            "model": self.ai_model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "response_format": {"type": "json_object"},
        }

        retries = 3
        wait = 2
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    logger.debug(f"Attempt {attempt+1}/{retries} to classify batch of {len(cookies)} cookies.")
                    resp = await client.post(
                        f"{self.openrouter_base_url}/chat/completions",
                        headers=headers,
                        json=body,
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]

                    parsed_response = json.loads(content)
                    if isinstance(parsed_response, dict) and "results" in parsed_response:
                        items = parsed_response["results"]
                    elif isinstance(parsed_response, list):
                        items = parsed_response
                    else:
                        items = parsed_response.get("cookies", []) if isinstance(parsed_response, dict) else []

                    by_key: Dict[Tuple[str, str], Dict[str, str]] = {}
                    for it in items:
                        nm = (it.get("name") or "").strip()
                        dm = (it.get("domain") or "").strip()
                        if not nm:
                            continue
                        by_key[(nm.lower(), dm.lower())] = {
                            "category": (it.get("category") or "Unknown").strip(),
                            "purpose": (it.get("purpose") or "").strip(),
                        }

                    out: List[ClassifiedCookie] = []
                    for c in cookies:
                        key_exact = (c.name.lower(), c.domain.lower())
                        fallback_key = (c.name.lower(), "")
                        meta = by_key.get(key_exact) or by_key.get(fallback_key) or {"category": "Unknown", "purpose": ""}
                        out.append(ClassifiedCookie(**asdict(c), **meta))

                    logger.info(f"Successfully classified {len(out)} cookies in batch.")
                    return out

            except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, KeyError) as e:

                error_type = type(e).__name__
                logger.warning(f"AI classify attempt {attempt+1}/{retries} failed with a {error_type} error: {e}")
                time.sleep(wait)
                wait *= 2

        logger.error("AI classification failed after all retries; applying heuristic fallback for this batch.")
        return self._heuristic_classify(cookies)

    def _heuristic_classify(self, cookies: List[NormalizedCookie]) -> List[ClassifiedCookie]:
        analytics_keys = ("ga", "_ga", "gid", "_gid", "_gat", "_gcl", "_hj", "_fbp", "_clck", "amplitude", "mixpanel")
        marketing_keys = ("_fbp", "_fbc", "fr", "mkt", "ads", "_uetsid", "_uetvid", "_tt_", "_scid")
        perf_keys = ("ak_bmsc", "bm_sv", "_cfuvid", "cf_bm")
        essential_keys = ("session", "sid", "csrftoken", "_csrf", "auth", "cookieconsent", "OptanonConsent", "OptanonAlertBoxClosed")

        out: List[ClassifiedCookie] = []
        for c in cookies:
            name_lower = c.name.lower()
            cat = "Unknown"
            if any(k in name_lower for k in essential_keys):
                cat = "Essential"
            elif any(k in name_lower for k in analytics_keys):
                cat = "Analytics"
            elif any(k in name_lower for k in marketing_keys):
                cat = "Marketing"
            elif any(k in name_lower for k in perf_keys):
                cat = "Performance"
            purpose = {
                "Essential": "Required for core site functionality and security.",
                "Analytics": "Collects usage statistics and insights.",
                "Marketing": "Used for advertising and cross-site tracking.",
                "Performance": "Improves site speed and reliability.",
            }.get(cat, "")
            out.append(ClassifiedCookie(**asdict(c), category=cat, purpose=purpose))
        return out

    async def classify_cookies(self, df_id: str, cookies: List[NormalizedCookie], batch_size: int = 20) -> List[ClassifiedCookie]:
        classified: List[ClassifiedCookie] = []
        for i in range(0, len(cookies), batch_size):
            batch = cookies[i : i + batch_size]
            classified.extend(await self._ai_classify_batch(df_id, batch))
        return classified

    async def scan(self, df_id: str, url: str, capture_seconds: int = 20, classify: bool = True) -> Dict[str, Any]:
        """
        Scan website cookies and classify them if enabled.
        """
        cookies = self.capture_normalized_cookies(url, duration_sec=capture_seconds)

        if classify:
            classified = await self.classify_cookies(df_id, cookies)
            cookies_out = [asdict(c) for c in classified]
        else:
            cookies_out = [asdict(c) for c in cookies]

        result = {
            "site": url,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "total_cookies": len(cookies_out),
            "cookies": cookies_out,
        }
        return result

    def save_json(self, result: Dict[str, Any], output_dir: str = "captured_cookies") -> str:
        os.makedirs(output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"cookies_{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
        logger.info(f"Saved to {path}")
        return path
