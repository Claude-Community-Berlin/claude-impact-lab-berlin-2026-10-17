"""OWNER: Dev A (feat/parent-ai).

Used by the onboarding screen: the parent types a Kita code, the UI shows
"Kita Sonnenblume, Berlin" (or the "Kita code not found" state on 404).
"""

from fastapi import APIRouter

from app.errors import NotImplementedYet
from app.schemas import ErrorResponse, KitaInfo

router = APIRouter(tags=["kitas"])


@router.get("/kitas/{code}", response_model=KitaInfo, responses={404: {"model": ErrorResponse}})
async def get_kita(code: str) -> KitaInfo:
    """Look up a Kita by code (case-insensitive). Only one Kita exists: settings.kita_code.

    TODO (Dev A): return KitaInfo from settings (kita_code / kita_name / kita_city);
    raise NotFound("Kita code not found.") for any other code.
    """
    raise NotImplementedYet("dev-a")
