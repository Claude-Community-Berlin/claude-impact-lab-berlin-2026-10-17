"""OWNER: Dev C (feat/staff-docs-insights). The "Eltern-Übersicht" screen.

Plain SQL over query_log (see app/db.py). No Claude call: group questions by exact text.
  families             = COUNT(DISTINCT family_id) (ignore NULL)
  questions_this_week  = rows in the last 7 days
  languages            = distinct families per lang, biggest first
  top_questions        = most repeated question texts, top 5
  unanswered           = question texts with answered_from_documents = 0, top 5
"""

from fastapi import APIRouter, Depends

from app.auth import require_staff
from app.errors import NotImplementedYet
from app.schemas import ErrorResponse, InsightsResponse

router = APIRouter(
    prefix="/staff", tags=["staff: insights"],
    dependencies=[Depends(require_staff)],
    responses={401: {"model": ErrorResponse}},
)


@router.get("/insights", response_model=InsightsResponse)
async def insights() -> InsightsResponse:
    raise NotImplementedYet("dev-c")
