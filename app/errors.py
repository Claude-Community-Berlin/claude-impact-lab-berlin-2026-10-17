import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = logging.getLogger("kita")

FRIENDLY = "Something went wrong, please try again in a moment."


class AIError(Exception):
    """Raised by the Claude service. `code` is ai_unavailable or ai_bad_output."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class ApiError(Exception):
    """An error with a fixed HTTP status and a message that is safe to show to users."""

    status = 500
    code = "internal_error"

    def __init__(self, message: str = FRIENDLY):
        super().__init__(message)
        self.message = message


class NotFound(ApiError):
    status = 404
    code = "not_found"


class Unauthorized(ApiError):
    status = 401
    code = "unauthorized"


class InvalidRequest(ApiError):
    status = 422
    code = "invalid_request"


class NotImplementedYet(ApiError):
    """Raised by endpoint stubs. Delete the raise when you implement the endpoint."""

    status = 501
    code = "not_implemented"

    def __init__(self, owner: str = ""):
        super().__init__(f"Not built yet{f' (owner: {owner})' if owner else ''}.")


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def on_validation(_: Request, exc: RequestValidationError):
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        msg = f"Invalid value for '{field}'." if field else "Invalid request."
        return _error(422, "invalid_request", msg)

    @app.exception_handler(ApiError)
    async def on_api_error(_: Request, exc: ApiError):
        return _error(exc.status, exc.code, exc.message)

    @app.exception_handler(AIError)
    async def on_ai_error(_: Request, exc: AIError):
        log.warning("AI error %s: %s", exc.code, exc.detail)
        return _error(502, exc.code, FRIENDLY)

    @app.exception_handler(Exception)
    async def on_unexpected(_: Request, exc: Exception):
        log.exception("Unexpected error")
        return _error(500, "internal_error", FRIENDLY)
