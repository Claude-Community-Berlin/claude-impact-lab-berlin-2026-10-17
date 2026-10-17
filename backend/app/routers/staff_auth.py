"""Demo login. The Kita code is the password; the response is a fixed bearer token."""

from fastapi import APIRouter

from app.config import get_settings
from app.errors import Unauthorized
from app.schemas import ErrorResponse, LoginRequest, LoginResponse

router = APIRouter(prefix="/staff", tags=["staff"])


@router.post("/login", response_model=LoginResponse, responses={401: {"model": ErrorResponse}})
async def login(req: LoginRequest) -> LoginResponse:
    settings = get_settings()
    if req.code.strip().upper() != settings.kita_code.upper():
        raise Unauthorized("Kita code not found.")
    return LoginResponse(token=settings.staff_token)
