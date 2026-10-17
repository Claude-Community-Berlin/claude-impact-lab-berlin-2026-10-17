"""OWNER: Dev A (feat/parent-ai). The 👍 / 👎 buttons under an answer."""

from fastapi import APIRouter

from app.errors import NotImplementedYet
from app.schemas import ErrorResponse, FeedbackRequest, Ok

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=Ok, responses={404: {"model": ErrorResponse}})
async def feedback(req: FeedbackRequest) -> Ok:
    """Store whether an answer was helpful.

    TODO (Dev A): call logs.add_feedback(req.query_id, req.helpful); it returns False when the
    query id is unknown -> raise NotFound("Unknown answer.").
    """
    raise NotImplementedYet("dev-a")
