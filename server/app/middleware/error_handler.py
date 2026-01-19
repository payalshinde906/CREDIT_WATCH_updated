"""
Error handling middleware
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.exceptions import AppException
from app.utils.response import ResponseFormatter
import logging
import socket

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
        except (socket.gaierror, ConnectionError, OSError) as exc:
            # Database connection errors
            error_str = str(exc)
            if "getaddrinfo failed" in error_str or "11001" in error_str:
                logger.error(f"[{request_id}] Database connection error: {error_str}")
                return JSONResponse(
                    status_code=503,
                    content=ResponseFormatter.create_error(
                        "DATABASE_CONNECTION_ERROR",
                        "Database connection failed. Please ensure PostgreSQL is running and DATABASE_URL is configured correctly.",
                        503,
                        {
                            "hint": "Check your .env file or environment variables for DATABASE_URL",
                            "default_url": "postgresql+asyncpg://user:password@localhost/creditdatawatch"
                        },
                        request_id,
                    ),
                )
            else:
                logger.error(f"[{request_id}] Connection error: {error_str}")
                return JSONResponse(
                    status_code=503,
                    content=ResponseFormatter.create_error(
                        "SERVICE_UNAVAILABLE",
                        "Service temporarily unavailable. Please try again later.",
                        503,
                        {},
                        request_id,
                    ),
                )
        except Exception as exc:
            logger.error(f"[{request_id}] Unexpected error: {str(exc)}", exc_info=True)
            # Check if it's a database-related error
            error_str = str(exc)
            if "database" in error_str.lower() or "connection" in error_str.lower() or "asyncpg" in error_str.lower():
                return JSONResponse(
                    status_code=503,
                    content=ResponseFormatter.create_error(
                        "DATABASE_ERROR",
                        "Database service is unavailable. Please check your database configuration and ensure PostgreSQL is running.",
                        503,
                        {},
                        request_id,
                    ),
                )
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
