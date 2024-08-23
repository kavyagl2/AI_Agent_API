from typing import Any
from fastapi import status
from fastapi.responses import JSONResponse


def json_response(content: dict[str, Any], status_code: int) -> JSONResponse:
    """
    Utility function for standardized JSON responses.
    """
    return JSONResponse(content=content, status_code=status_code)


def internal_error_response(msg: str, error: Exception) -> JSONResponse:
    """
    Utility function to standardize Internal Server Error Responses
    """
    return JSONResponse(
        content={"message": msg, "error": str(error)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
