"""OWNER: Dev C (feat/staff-docs-insights). The Kita's knowledge base: the .md files that
/ask answers from.

Rules for the implementation:
  - name is a path relative to settings.data_dir, must end in .md, may contain one level of
    folder (letters/x.md). Resolve the path and check it stays inside data_dir (no ../ tricks).
  - PUT creates the file if it does not exist ("Dokument hinzufügen").
  - After every write call prompts.invalidate() so /ask uses the new text immediately.
"""

from fastapi import APIRouter, Depends

from app.auth import require_staff
from app.errors import NotImplementedYet
from app.schemas import DocumentContent, DocumentInfo, DocumentWrite, ErrorResponse

router = APIRouter(
    prefix="/staff", tags=["staff: documents"],
    dependencies=[Depends(require_staff)],
    responses={401: {"model": ErrorResponse}},
)


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents() -> list[DocumentInfo]:
    raise NotImplementedYet("dev-c")


@router.get("/documents/{name:path}", response_model=DocumentContent,
            responses={404: {"model": ErrorResponse}})
async def get_document(name: str) -> DocumentContent:
    raise NotImplementedYet("dev-c")


@router.put("/documents/{name:path}", response_model=DocumentContent,
            responses={422: {"model": ErrorResponse}})
async def put_document(name: str, body: DocumentWrite) -> DocumentContent:
    raise NotImplementedYet("dev-c")
