from fastapi import status
from fastapi.responses import JSONResponse


def internal_error_response(msg: str, error: Exception) -> JSONResponse:
    """
    Utility function to standardize Internal Server Error Responses
    """
    return JSONResponse(
        content={"message": msg, "error": str(error)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
