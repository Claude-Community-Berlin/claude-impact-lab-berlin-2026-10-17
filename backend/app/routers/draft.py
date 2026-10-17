"""OWNER: Dev A (feat/parent-ai)."""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import LANGUAGES, DraftAI, DraftRequest, DraftResponse, ErrorResponse
from app.services import claude, mock

router = APIRouter(tags=["draft"])


def _tag(name: str, value: str | None) -> str:
    """Optional values go in their own tag; an empty tag tells Claude the value is missing."""
    return f"<{name}>{(value or '').strip()}</{name}>"


@router.post("/draft-message", response_model=DraftResponse, responses={502: {"model": ErrorResponse}})
async def draft_message(req: DraftRequest) -> DraftResponse:
    """Turn what the parent wants to say into a polite German message + back-translation."""
    if get_settings().mock_ai:
        result = mock.draft(req.text, req.child_name, req.parent_name)
    else:
        language = LANGUAGES[req.lang]["name"]
        messages = [{
            "role": "user",
            "content": (
                f"Parent's language: {language}\n\n"
                f"{_tag('child_name', req.child_name)}\n"
                f"{_tag('parent_name', req.parent_name)}\n\n"
                f"<parent_text>\n{req.text}\n</parent_text>"
            ),
        }]
        result = await claude.generate("draft_message", messages, DraftAI)
    return DraftResponse(**result.model_dump(), lang=req.lang)
