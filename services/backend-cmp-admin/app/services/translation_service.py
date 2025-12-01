import json
from typing import Dict, Optional, List
from itertools import islice
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
import httpx
from app.core.logger import get_logger

logger = get_logger("api.translation_service")


supported_languages_map: Dict[str, str] = {
    "asm": "Assamese",
    "mni": "Manipuri",
    "nep": "Nepali",
    "san": "Sanskrit",
    "urd": "Urdu",
    "hin": "Hindi",
    "mai": "Maithili",
    "tam": "Tamil",
    "mal": "Malayalam",
    "ben": "Bengali",
    "kok": "Konkani",
    "guj": "Gujarati",
    "kan": "Kannada",
    "snd": "Sindhi",
    "ori": "Odia",
    "sat": "Santali",
    "pan": "Punjabi",
    "mar": "Marathi",
    "tel": "Telugu",
    "kas": "Kashmiri",
    "brx": "Bodo",
    "doi": "Dogri",
    "eng": "English",
}


class TranslationService:
    def __init__(
        self,
        df_register_collection: Optional[AsyncIOMotorCollection] = None,
    ):
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.df_register_collection = df_register_collection

    async def _get_api_key(self, df_id: str) -> str:
        df_doc = await self.df_register_collection.find_one({"df_id": df_id})
        if not df_doc:
            logger.error(f"Data fiduciary not found for df_id: {df_id}", extra={"df_id": df_id})
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        openrouter_key = df_doc.get("ai", {}).get("openrouter_api_key")

        if not openrouter_key:
            logger.error(f"OpenRouter API key not configured for DF: {df_id}", extra={"df_id": df_id})
            raise HTTPException(status_code=400, detail="OpenRouter API key not configured for this DF")
        return openrouter_key

    def _chunks(self, data: List[str], size: int):
        """Yield successive chunks of size n from list."""
        it = iter(data)
        for first in it:
            yield [first] + list(islice(it, size - 1))

    async def translate_batch(self, model: str, df_id: str, text: str, lang_codes: List[str]) -> Optional[Dict[str, str]]:
        """Translate English text into a given batch of languages."""
        languages_list = [f"{code} ({supported_languages_map[code]})" for code in lang_codes]
        languages_str = ", ".join(languages_list)
        logger.info(f"Starting translation for batch: {languages_str}", extra={"df_id": df_id, "languages": lang_codes})

        system_msg = f"""
        You are a highly accurate translation assistant.
        Translate the given English text into the following languages: {languages_str}.
        Return the response strictly in valid JSON format where:
        - Keys are the language codes exactly as provided.
        - Values are the translated texts.
        - Do not add any commentary or explanation.
        """

        user_msg = f"Text to translate: {text}"

        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            openrouter_key = await self._get_api_key(df_id)
            if not openrouter_key:
                logger.error(f"OpenRouter API key not available for DF: {df_id}", extra={"df_id": df_id})
                return None

            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )

            resp.raise_for_status()
            data = resp.json()
            raw_response = data["choices"][0]["message"]["content"].strip()

            try:
                translations = json.loads(raw_response)
                if not isinstance(translations, dict):
                    logger.warning(
                        f"Translation response is not a valid dict for batch: {languages_str}",
                        extra={"df_id": df_id, "languages": lang_codes, "raw_response": raw_response},
                    )
                    return None
                logger.info(f"Successfully translated batch: {languages_str}", extra={"df_id": df_id, "languages": lang_codes})
                return translations
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON for batch: {languages_str}. Error: {e}",
                    exc_info=True,
                    extra={"df_id": df_id, "languages": lang_codes, "raw_response": raw_response},
                )
                return None

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error during translation for batch {languages_str}: {e.response.text}",
                exc_info=True,
                extra={"df_id": df_id, "languages": lang_codes, "status_code": e.response.status_code, "response_body": e.response.text},
            )

        except Exception as e:
            logger.error(
                f"Unexpected error for batch {languages_str}: {e}",
                exc_info=True,
                extra={"df_id": df_id, "languages": lang_codes, "text": text},
            )
        return None

    async def translate_all_languages(
        self,
        current_user: dict,
        text: str,
        batch_size: int = 5,
        model: Optional[str] = "google/gemini-2.0-flash-001",
    ) -> Dict[str, str]:
        df_id = current_user.get("df_id")
        logger.info(f"Starting translation for all languages for DF: {df_id}", extra={"df_id": df_id, "text_length": len(text)})
        translations = {}
        language_codes = [code for code in supported_languages_map.keys() if code != "eng"]
        batches = list(self._chunks(language_codes, batch_size))

        for i, batch in enumerate(batches, start=1):
            logger.info(
                f"Processing batch {i}/{len(batches)} for DF: {df_id}",
                extra={"df_id": df_id, "batch_number": i, "total_batches": len(batches), "batch_languages": batch},
            )
            batch_result = await self.translate_batch(model, df_id, text, batch)

            if batch_result:
                translations.update(batch_result)
                logger.info(f"Batch {i} completed successfully for DF: {df_id}", extra={"df_id": df_id, "batch_number": i})
            else:
                logger.warning(
                    f"Skipping batch {i} due to errors for DF: {df_id}", extra={"df_id": df_id, "batch_number": i, "batch_languages": batch}
                )

        logger.info(f"Finished translation for all languages for DF: {df_id}", extra={"df_id": df_id, "total_translations": len(translations)})
        return translations
