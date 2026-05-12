from typing import Any, Generic, Optional, TypeVar, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error response detail."""
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Readable error message")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response."""
    success: bool = Field(default=True, description="Operation status")
    message: str = Field(..., description="Operation message")
    data: Optional[T] = Field(default=None, description="Response data")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed",
                "data": {}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(default=False, description="Operation status")
    error: ErrorDetail = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "ERROR_CODE",
                    "message": "Readable explanation"
                }
            }
        }


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Operation status")
    message: Optional[str] = Field(default=None, description="Operation message")
    data: Optional[T] = Field(default=None, description="Response data")
    error: Optional[ErrorDetail] = Field(default=None, description="Error details")

    @classmethod
    def success_response(cls, message: str = "Success", data: Any = None) -> "ApiResponse":
        """Create a success response."""
        return cls(
            success=True,
            message=message,
            data=data,
            error=None
        )

    @classmethod
    def error_response(cls, code: str, message: str) -> "ApiResponse":
        """Create an error response."""
        return cls(
            success=False,
            message=None,
            data=None,
            error=ErrorDetail(code=code, message=message)
        )
