from collections.abc import Sequence

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.backend.log import get_logger

logger = get_logger(__name__)


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    detail: str | Sequence[object]
    if isinstance(exc, RequestValidationError):
        status_code = 422
        error_type = "Validation Error"
        detail = exc.errors()
        logger.warning(f"[API] Validation error: {exc}")
    else:
        status_code = 500
        error_type = "Internal Server Error"
        detail = "An unexpected error occurred"
        logger.error(f"[API] Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "detail": detail
        }
    )
