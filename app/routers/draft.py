"""OWNER: Dev A (feat/parent-ai).

TODO (Dev A): DraftRequest now has optional child_name / parent_name. Pass them to Claude in
the user message (inside <parent_text>-style tags) so the German message names the child and
is signed with the parent's name. Update prompts/draft_message.md to match.
"""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import LANGUAGES, DraftAI, DraftRequest, DraftResponse, ErrorResponse
from app.services import claude, mock

router = APIRouter(tags=["draft"])


@router.post("/draft-message", response_model=DraftResponse, responses={502: {"model": ErrorResponse}})
async def draft_message(req: DraftRequest) -> DraftResponse:
    """Turn what the parent wants to say into a polite German message + back-translation."""
    if get_settings().mock_ai:
        result = mock.draft(req.text)
    else:
        language = LANGUAGES[req.lang]["name"]
        messages = [{
            "role": "user",
            "content": (
                f"Parent's language: {language}\n\n"
                f"<parent_text>\n{req.text}\n</parent_text>"
            ),
        }]
        result = await claude.generate("draft_message", messages, DraftAI)
    return DraftResponse(**result.model_dump(), lang=req.lang)
