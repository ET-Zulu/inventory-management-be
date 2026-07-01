"""Common utilities and helpers for API responses."""

from typing import Any, Optional
from app.schemas.response import ApiResponse, ErrorDetail, SuccessResponse, ErrorResponse


def success_response(message: str = "Success", data: Any = None , total: Optional[int] = None) -> dict:
    """
    Create a standardized success response.
    
    Args:
        message: Success message
        data: Response data
        total: Total number of items (for pagination)
        
    Returns:
        Standardized success response dict
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "total": total
    }


def error_response(code: str, message: str) -> dict:
    """
    Create a standardized error response.
    
    Args:
        code: Error code identifier
        message: Readable error message
        
    Returns:
        Standardized error response dict
    """
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }


# Common error codes
class ErrorCode:
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    INVALID_OPERATION = "INVALID_OPERATION"
    DATABASE_ERROR = "DATABASE_ERROR"
