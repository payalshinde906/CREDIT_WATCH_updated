"""
Error handling middleware
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.exceptions import AppException
from app.utils.response import ResponseFormatter
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", "")
        
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            logger.warning(f"[{request_id}] AppException: {exc.code} - {exc.message}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ResponseFormatter.create_error(
                    exc.code,
                    exc.message,
                    exc.status_code,
                    exc.details,
                    request_id,
                ),
            )
        except Exception as exc:
            logger.error(f"[{request_id}] Unexpected error: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=ResponseFormatter.create_error(
                    "INTERNAL_SERVER_ERROR",
                    "An unexpected error occurred",
                    500,
                    {},
                    request_id,
                ),
            )
