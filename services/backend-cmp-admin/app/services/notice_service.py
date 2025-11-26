import json
from typing import Dict, Any, List


class NoticeService:
    def __init__(self, supported_languages_map, static_json_file, categories_translation_file):
        self.supported_languages_map = supported_languages_map
        self.static_json_file = static_json_file
        self.categories_translation_file = categories_translation_file

    async def build_notice_data(self, deeply_enriched_data: List[Dict[str, Any]], translated_audio: List[Dict[str, Any]] = None):
        """
        Builds a consolidated dictionary of notice data keyed by language code,
        using a single deeply enriched data structure.
        """
        with open(self.static_json_file, "r", encoding="utf-8") as f:
            static_data = json.load(f)
        static_data_dict = {item["language"]: item for item in static_data}

        with open(self.categories_translation_file, "r", encoding="utf-8") as f:
            categories_translation_list = json.load(f)

        categories_translation = {item["eng"]: item for item in categories_translation_list}

        consolidated_data = {}

        audio_map = {}
        if translated_audio:

            for audio in translated_audio:

                if hasattr(audio, "audio_language"):
                    lang = audio.audio_language
                    url = audio.audio_url
                else:
                    lang = audio.get("audio_language")
                    url = audio.get("audio_url")

                if lang and url:
                    audio_map[lang] = url

        for lang_code, lang_data in static_data_dict.items():
            lang_name = self.supported_languages_map.get(lang_code, lang_code)
            combined_data = lang_data.copy()
            combined_data["language"] = lang_name

            if lang_name in audio_map:
                combined_data["audio_file_url"] = audio_map[lang_name]
            elif lang_code in audio_map:
                combined_data["audio_file_url"] = audio_map[lang_code]

            combined_data["data_elements"] = []

            for de_entry in deeply_enriched_data:
                de_obj = de_entry["de_obj"]

                de_translated = de_obj.get("translations", {}).get(lang_code, de_obj.get("de_name", "N/A"))

                purposes_for_de = []
                for purpose_obj in de_entry["purposes"]:

                    purpose_translated = purpose_obj.get("translations", {}).get(lang_code, purpose_obj.get("purpose_title", "N/A"))

                    original_category = purpose_obj.get("purpose_category", "")
                    category_translated = categories_translation.get(original_category, {}).get(lang_code, original_category)

                    service_message = ""
                    legal_message = ""
                    for de_in_purpose in purpose_obj.get("data_elements", []):
                        if de_in_purpose.get("de_id") == de_obj["_id"]:
                            service_message = de_in_purpose.get("service_message", "")
                            legal_message = de_in_purpose.get("legal_message", "")
                            break

                    consent_obj = {
                        "purpose_id": purpose_obj["_id"],
                        "description": purpose_translated,
                        "consent_expiry_period": purpose_obj["consent_time_period"],
                        "data_processor_details": purpose_obj.get("data_processor_details", []),
                        "purpose_category": category_translated,
                        "service_message": service_message,
                        "legal_message": legal_message,
                    }

                    purposes_for_de.append(consent_obj)

                combined_data["data_elements"].append(
                    {
                        "de_id": de_obj["_id"],
                        "title": de_translated,
                        "data_retention_period": de_obj["de_retention_period"],
                        "consents": purposes_for_de,
                    }
                )

            consolidated_data[lang_code] = combined_data

        return consolidated_data

    def render_html(self, consolidated_data: Dict[str, Any], df_name: str, notice_type: str = "single"):

        if notice_type == "single":
            html_template_file = "app/constants/html_simple.html"
        elif notice_type == "multiple":
            html_template_file = "app/constants/html_complex.html"
        elif notice_type == "boxed":
            html_template_file = "app/constants/html_boxed.html"
        else:
            html_template_file = "app/constants/html_layered.html"

        with open(html_template_file, "r", encoding="utf-8") as f:
            html_template = f.read()
        json_string = json.dumps(consolidated_data, indent=4, ensure_ascii=False)
        final_html = html_template.replace("// {{ NOTICE_DATA }}", json_string)
        final_html = final_html.replace("{{ df_name }}", df_name)
        return final_html
