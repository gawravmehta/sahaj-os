from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal

from app.api.v1.deps import get_translation_service, get_current_user
from app.services.translation_service import TranslationService

router = APIRouter()


@router.post(
    "/create-translations",
    summary="List all Purpose Templates",
)
async def create_translations(
    english_text: str = Query(..., description="The English text to be translated."),
    model: Literal["google/gemini-2.0-flash-001"] = Query(
        "google/gemini-2.0-flash-001",
        description="The AI model to use for translation.",
    ),
    current_user: dict = Depends(get_current_user),
    service: TranslationService = Depends(get_translation_service),
):
    try:

        translations = await service.translate_all_languages(current_user, english_text, batch_size=22, model=model)
        if not translations:
            raise HTTPException(status_code=500, detail="Translation service returned no translations.")

        return service.return_transaltion_response(english_text, translations)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
