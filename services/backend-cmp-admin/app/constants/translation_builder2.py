import json
from enum import Enum
from typing import Dict, Any, List


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

    def _get_cookies_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Gets dynamic cookie data, simulating a database fetch."""
        return {
            "essential": [
                {
                    "name": "session_id",
                    "description": {
                        "eng": "Tracks user session",
                        "hin": "उपयोगकर्ता सत्र को ट्रैक करता है",
                    },
                    "domain": "proteantech.in",
                    "expiry": {"value": 1, "unit": "year"},
                },
                {
                    "name": "df_session",
                    "description": {
                        "eng": "Anonymously tracks your session for security.",
                        "hin": "सुरक्षा के लिए आपके सत्र को गुमनाम रूप से ट्रैक करता है।",
                    },
                    "domain": "proteantech.in",
                    "expiry": {"value": 1, "unit": "day"},
                },
            ],
            "analytics": [
                {
                    "name": "_ga",
                    "description": {"eng": "Google Analytics ID", "hin": "गूगल एनालिटिक्स आईडी"},
                    "domain": "google.com",
                    "expiry": {"value": 2, "unit": "year"},
                }
            ],
        }

    def _format_expiry(self, value: int, unit: str, lang: str) -> str:
        """Formats a cookie expiry into a human-readable string using loaded data."""
        units_data = self.data["expiryUnits"]
        translated_unit = units_data.get(unit, {}).get(lang, units_data.get(unit, {}).get("eng"))
        if not translated_unit:
            return ""
        return f"{value} {translated_unit}{'s' if value > 1 and lang == 'eng' else ''}"

    def build_banner(self, language: str, df_name: str, privacy_url: str, cookie_url: str) -> Dict[str, Any]:
        """Builds the complete cookie banner dictionary for a given language."""
        texts = self.data["texts"]
        categories_data = self.data["categories"]
        cookies_data = self._get_cookies_data()

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

    def build_all_languages(self, df_name: str, privacy_url: str, cookie_url: str) -> Dict[str, Any]:
        """Generates the cookie banner JSON for multiple languages."""
        languages = self.data.get("languages", [])
        if not languages:
            raise ValueError("No languages found in the JSON data.")
        return {lang: self.build_banner(lang, df_name, privacy_url, cookie_url) for lang in languages}


def generate_js_translations_file(df_name: str, privacy_url: str, cookie_url: str, input_file: str, output_file: str):
    """
    Generates a JavaScript file with an exported translations object.
    """
    try:
        banner_builder = CookieBanner(file_path=input_file)
        all_translations = banner_builder.build_all_languages(
            df_name=df_name,
            privacy_url=privacy_url,
            cookie_url=cookie_url,
        )

        js_content = f"export const translations = {json.dumps(all_translations, indent=2, ensure_ascii=False)};\n"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(js_content)

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    generate_js_translations_file(
        df_name="Protean",
        privacy_url="https://proteantech.in/privacy-policy",
        cookie_url="https://proteantech.in/cookie-policy",
        input_file="static_cookie_translation.json",
        output_file="translations.js",
    )
