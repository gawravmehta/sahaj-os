import json
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List
import re
import os
import subprocess
from dotenv import load_dotenv


class CookieCategory(str, Enum):
    ESSENTIAL = "essential"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERFORMANCE = "performance"
    SECURITY = "security"


class CookieBanner:
    """
    A class to handle the loading, processing, and building of
    multi-language cookie banner data.
    """

    def __init__(self, file_path: str):
        """Initializes the class by loading the static data."""
        self.data = self._load_data(file_path)

    def _load_data(self, file_path: str) -> Dict[str, Any]:
        """Loads all configuration data from a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Error: The '{file_path}' file was not found. Please create it.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(
                f"❌ Error: The '{file_path}' file is not a valid JSON. Please check its syntax.",
                doc=None,
                pos=0,
            )

    def _get_dev_cookies_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Gets dynamic cookie data based on environment, preferring the static
        'dev_cookies' key if in dev mode, otherwise falling back to the
        default hardcoded production data for demonstration.
        """

        dev_data = self.data.get("dev_cookies")
        if dev_data:
            return dev_data

    def _format_expiry(self, value: int, unit: str, lang: str) -> str:
        """
        Formats a cookie expiry into a human-readable string using loaded data.
        If value is 0 and unit is 'day', display it as 'session'.
        """
        units_data = self.data.get("expiryUnits", {})

        if value == 0 and unit.lower() == "day":
            translated_unit = units_data.get("session", {}).get(lang, units_data.get("session", {}).get("eng", "Session"))
            return translated_unit

        unit_lower = unit.lower().rstrip("s")

        translated_unit = units_data.get(unit_lower, {}).get(lang, units_data.get(unit_lower, {}).get("eng"))
        if not translated_unit:
            return ""

        if lang == "eng" and value != 1:
            translated_unit += "s"

        return f"{value} {translated_unit}"

    def build_banner(
        self, language: str, df_name: str, privacy_url: str, cookie_url: str, cookies_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Builds the complete cookie banner dictionary for a given language."""
        texts = self.data["texts"]
        categories_data = self.data["categories"]
        try:
            banner = {
                "description": texts["description"].get(language, texts["description"]["eng"]).format(df_name=df_name),
                "links": [
                    {
                        "text": link["text"].get(language, link["text"]["eng"]),
                        "url": link["url"].format(privacy_url=privacy_url, cookie_url=cookie_url),
                    }
                    for link in texts["links"]
                ],
                "bannerButtons": {k: v.get(language, v["eng"]) for k, v in texts["bannerButtons"].items()},
                "modalTitle": texts["modalTitle"].get(language, texts["modalTitle"]["eng"]),
                "modalSectionTitle": texts["modalSectionTitle"].get(language, texts["modalSectionTitle"]["eng"]),
                "modalButtons": {k: v.get(language, v["eng"]) for k, v in texts["modalButtons"].items()},
                "poweredBy": texts["poweredBy"].get(language, texts["poweredBy"]["eng"]),
                "categories": {},
            }
        except KeyError as e:
            raise KeyError(
                f"❌ Error: A key was not found in the JSON data for language '{language}': {e}. Please ensure all languages are translated."
            )

        for category, cookies in cookies_data.items():
            translated_cookies = []
            for cookie in cookies:
                cookie_description = cookie["description"].get(language, cookie["description"]["eng"])
                translated_cookie = {
                    "name": cookie["name"],
                    "description": cookie_description,
                    "domain": cookie["domain"],
                    "expiry": self._format_expiry(cookie["expiry"]["value"], cookie["expiry"]["unit"], language),
                }
                if "provider" in cookie:
                    translated_cookie["provider"] = cookie["provider"]

                translated_cookies.append(translated_cookie)

            category_info = categories_data.get(category, {})
            category_name = category_info.get("name", {}).get(language, category_info.get("name", {}).get("eng", ""))
            category_desc = category_info.get("description", {}).get(language, category_info.get("description", {}).get("eng", ""))

            banner["categories"][category] = {
                "name": category_name,
                "description": category_desc,
                "cookies": translated_cookies,
            }
        return banner

    def build_all_languages(self, df_name: str, privacy_url: str, cookie_url: str, cookies_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generates the cookie banner JSON for multiple languages."""
        languages = self.data.get("languages", [])
        if not languages:
            raise ValueError("No languages found in the JSON data.")

        return {lang: self.build_banner(lang, df_name, privacy_url, cookie_url, cookies_data) for lang in languages}


class WidgetBuilder:
    """
    Handles all steps of the widget build process: path management,
    dynamic file generation, and running the Vite build subprocess.
    """

    def __init__(self, config: Dict[str, Any], is_dev: bool = False):
        self.widget_name = config["WIDGET_NAME"]
        self.df_name = config["DF_NAME"]
        self.privacy_url = config["PRIVACY_URL"]
        self.cookie_url = config["COOKIE_URL"]
        self.src_template_path = config["SRC_TEMPLATE_PATH"]
        self.logo_url = config["LOGO_URL"]
        self.consent_api_base_url = config["COOKIE_CONSENT_URL"]
        self.is_dev = is_dev

        self.banner_builder = CookieBanner(file_path=config["INPUT_JSON_FILE"])
        if self.is_dev:
            self.cookies_data = self.banner_builder._get_dev_cookies_data()
        else:
            self.cookies_data = config["COOKIES_DATA"]
            self.banner_builder.cookies_data = self.cookies_data

    @property
    def build_dir(self):
        folder_name = f"{self.widget_name}-dev" if self.is_dev else self.widget_name
        if self.is_dev:
            return os.path.join("src/builds", folder_name)
        else:
            return os.path.join("app/cmp_widget/src/builds", folder_name)

    @property
    def entry_file(self):
        return os.path.join(self.build_dir, "cmp-entry.js")

    @property
    def translations_file(self):
        return os.path.join(self.build_dir, "translations.js")

    @property
    def template_file(self):
        return os.path.join(self.build_dir, "template.html")

    @property
    def output_file_name(self):
        return f"{self.widget_name}-cmp-widget.iife.js"

    @property
    def dist_file_path(self):
        if self.is_dev:
            return os.path.join("dev-dist", self.output_file_name)
        else:
            return os.path.join("app/cmp_widget/dist", self.output_file_name)

    def _generate_js_translations_file(self):
        all_translations = self.banner_builder.build_all_languages(
            df_name=self.df_name,
            privacy_url=self.privacy_url,
            cookie_url=self.cookie_url,
            cookies_data=self.cookies_data,
        )
        js_content = f"export const translations = {json.dumps(all_translations, indent=2, ensure_ascii=False)};\n"
        with open(self.translations_file, "w", encoding="utf-8") as f:
            f.write(js_content)

    def _insert_categories_into_html(self):
        with open(self.src_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        category_list_pattern = re.compile(r'(<div class="category-list">.*?<\/div>)', re.DOTALL)
        match = category_list_pattern.search(template_content)
        if not match:
            raise ValueError("❌ Could not find '<div class=\"category-list\">' block in template.")

        generated_categories = ""
        first_category = True
        for category in self.cookies_data.keys():
            class_attr = f' class="category-item{" active" if first_category else ""}"'
            generated_categories += f' \t\t\t\t\t<div{class_attr} data-category="{category}"></div>\n'
            first_category = False

        new_category_list_content = f'<div class="category-list">\n{generated_categories} \t\t\t\t</div>'
        updated_html = category_list_pattern.sub(new_category_list_content, template_content)

        with open(self.template_file, "w", encoding="utf-8") as f:
            f.write(updated_html)

    def _generate_js_entry_file(self):
        js_content = f"""
// **GENERATED FILE: Do not edit manually**

// 1. DYNAMIC ASSETS (From the current build folder)
import {{ translations }} from "./translations.js"; 
import template from "./template.html?raw";

// 2. STATIC ASSETS (From the main src/ folder)
import styles from "../../styles.css?raw";

// 3. CORE WIDGET LOGIC
import {{ initWidget }} from "../../cmp.js"; 

// 4. DYNAMIC WEBSITE ID
const websiteId = "{self.widget_name}";
const consentApiBaseUrl = "{self.consent_api_base_url}";

// Execute the widget initialization with all loaded assets
initWidget({{ translations, template, styles, websiteId, consentApiBaseUrl }});
"""
        with open(self.entry_file, "w", encoding="utf-8") as f:
            f.write(js_content)

    def _mock_upload_dist_file(self):
        """Mocks the process of uploading the final built file to a CDN or server."""

        if not os.path.exists(self.dist_file_path):
            print(f"Warning: Final build file not found at '{self.dist_file_path}'. Skipping upload.")
            return

        file_size = os.path.getsize(self.dist_file_path)
        mock_upload_url = f"https://cdn.example.com/widgets/{self.widget_name}/{self.output_file_name}"

        print(f"Uploading '{self.output_file_name}' (Size: {file_size/1024:.2f} KB)...")
        print(f"Successfully uploaded to: {mock_upload_url}")

    def _clean_build_directory(self):
        """Removes the dynamically created build folder from src/builds."""
        print("\n--- Starting Cleanup ---")
        if not os.path.exists(self.build_dir):
            print(f"Warning: Build directory '{self.build_dir}' not found. Nothing to clean.")
            return

        try:
            import shutil

            shutil.rmtree(self.build_dir)
            print(f"Cleaned up build directory: {self.build_dir}")
        except Exception as e:
            print(f"Error during cleanup of '{self.build_dir}': {e}")

    def _insert_logo_url(self):
        """Replaces the LOGO_SRC placeholder in the generated HTML template."""

        try:
            with open(self.template_file, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Error: Cannot find generated template file at '{self.template_file}'")

        updated_html = template_content.replace("{{LOGO_URL}}", self.logo_url)
        print(updated_html)

        with open(self.template_file, "w", encoding="utf-8") as f:
            f.write(updated_html)

        print(f"Logo URL inserted into '{self.template_file}'!")

    def build(self):
        """Orchestrates the full production build, deployment, and cleanup process."""
        if self.is_dev:
            return self.dev_start()

        print(f"\n--- Starting Production Build for Widget: {self.widget_name} ---")
        os.makedirs(self.build_dir, exist_ok=True)
        print(f"Created build directory: {self.build_dir}")

        try:
            self._generate_js_translations_file()
            self._insert_categories_into_html()
            self._insert_logo_url()
            self._generate_js_entry_file()

            print("\n--- Executing Vite Build ---")
            env = os.environ.copy()
            base_dir = Path("app/cmp_widget")
            entry_file_path = Path(self.entry_file)

            relative_entry_file_posix = entry_file_path.relative_to(base_dir).as_posix()

            env["BUILD_ENTRY"] = relative_entry_file_posix
            env["BUILD_FILE_NAME"] = self.output_file_name.split(".")[0]

            subprocess.run(["npm", "install"], check=True, env=env, shell=True, cwd=base_dir)
            subprocess.run(["npm", "run", "build"], check=True, env=env, shell=True, cwd=base_dir)

            self._mock_upload_dist_file()
            self._clean_build_directory()
            print(f"\nSUCCESS! Widget '{self.widget_name}' built, deployed, and cleaned up.")
        except Exception as e:
            print(f"\nError during build for {self.widget_name}: {e}")
            self._clean_build_directory()
            raise

    def dev_start(self):
        """Starts development server for widget."""
        print(f"\n--- Starting Dev Server for Widget: {self.widget_name}-dev ---")
        os.makedirs(self.build_dir, exist_ok=True)
        print(f"Created build directory: {self.build_dir}")

        try:
            self._generate_js_translations_file()
            self._insert_categories_into_html()
            self._generate_js_entry_file()
            self._insert_logo_url()

            print("\n--- Running Vite Dev Server ---")
            env = os.environ.copy()
            env["BUILD_ENTRY"] = self.entry_file

            subprocess.run(["npm", "install"], check=True, env=env, shell=True)
            subprocess.run(["npm", "run", "dev"], check=True, env=env, shell=True)
        except Exception as e:
            print(f"\nError during dev for {self.widget_name}: {e}")
            raise


def get_config_from_env() -> Dict[str, str]:
    """Loads environment variables and sets defaults."""

    load_dotenv()
    cookies_data = {
        "essential": [
            {
                "name": "abhsishek123",
                "description": {"eng": "Tracks user session", "hin": "उपयोगकर्ता सत्र को ट्रैक करता है"},
                "domain": "proteantech.in",
                "expiry": {"value": 1, "unit": "year"},
            }
        ],
        "analytics": [
            {
                "name": "_ga12312",
                "description": {"eng": "Google Analytics ID", "hin": "गूगल एनालिटिक्स आईडी"},
                "domain": "google.com",
                "expiry": {"value": 2, "unit": "year"},
            }
        ],
        "marketing": [
            {
                "name": "_fbpppppp",
                "description": {"eng": "Facebook Pixel ID", "hin": "फेसबुक पिक्सेल आईडी"},
                "domain": "facebook.com",
                "expiry": {"value": 3, "unit": "month"},
            }
        ],
        "performance": [
            {
                "name": "main12321",
                "description": {"eng": "Facebook Pixel ID", "hin": "फेसबुक पिक्सेल आईडी"},
                "domain": "facebook.com",
                "expiry": {"value": 3, "unit": "month"},
            }
        ],
    }
    return {
        "COOKIES_DATA": cookies_data,
        "WIDGET_NAME": os.getenv("WIDGET_NAME", "default_widget"),
        "INPUT_JSON_FILE": os.getenv("INPUT_JSON_FILE", "static_cookie_translation.json"),
        "DF_NAME": os.getenv("DF_NAME", "Default Firm Name"),
        "PRIVACY_URL": os.getenv("PRIVACY_URL", "https://default.com/privacy"),
        "COOKIE_URL": os.getenv("COOKIE_URL", "https://default.com/cookie"),
        "SRC_TEMPLATE_PATH": os.getenv("SRC_TEMPLATE_PATH", "src/template.html"),
        "LOGO_URL": os.getenv("LOGO_URL"),
    }


if __name__ == "__main__":
    import sys

    config = get_config_from_env()

    is_dev_mode = "--dev" in sys.argv or "-d" in sys.argv

    builder = WidgetBuilder(config, is_dev=is_dev_mode)

    if is_dev_mode:
        builder.dev_start()
    else:
        builder.build()
