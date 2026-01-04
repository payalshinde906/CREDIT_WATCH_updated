"""
Consistent response formatting
"""
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


UTC_REPLACEMENT = "+00:00"


def current_timestamp() -> str:
    """Return timezone-aware UTC timestamp as ISO string with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace(UTC_REPLACEMENT, "Z")


class ResponseFormatter:
    """Format consistent API responses"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = 200,
        request_id: Optional[str] = None,
    ) -> dict:
        """
        Success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            request_id: Request ID for tracking
            
        Returns:
            Formatted response dict
        """
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": current_timestamp(),
            "request_id": request_id or str(uuid4()),
        }

    @staticmethod
    def error(
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[dict] = None,
        request_id: Optional[str] = None,
    ) -> dict:
        """
        Error response
        
        Args:
            code: Error code
            message: Error message
            status_code: HTTP status code
            details: Additional error details
            request_id: Request ID for tracking
            
        Returns:
            Formatted error response dict
        """
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "timestamp": current_timestamp(),
            "request_id": request_id or str(uuid4()),
        }


def paginated_response(items: list, total: int, page: int, page_size: int, request_id: Optional[str] = None) -> dict:
    """
    Paginated list response
    
    Args:
        items: List of items
        total: Total count
        page: Current page
        page_size: Items per page
        request_id: Request ID
        
    Returns:
        Formatted paginated response
    """
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            },
        },
        "timestamp": current_timestamp(),
        "request_id": request_id or str(uuid4()),
    }
