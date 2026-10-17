from fastapi import APIRouter

from app.config import get_settings
from app.schemas import LANGUAGES, Health, Language, LanguagesResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=Health)
async def health() -> Health:
    return Health(mock_ai=get_settings().mock_ai)


@router.get("/languages", response_model=LanguagesResponse)
async def languages() -> LanguagesResponse:
    return LanguagesResponse(languages=[
        Language(code=code, label=v["label"], rtl=v["rtl"]) for code, v in LANGUAGES.items()
    ])
