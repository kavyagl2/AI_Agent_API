from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from functools import wraps

def handle_exceptions(func):
    """
    Decorator to handle exceptions for FastAPI endpoints.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as http_exc:
            # Re-raise HTTP exceptions (handled specifically)
            raise http_exc
        except Exception as e:
            # Handle generic exceptions
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
    return wrapper

def json_response(content: dict, status_code: int) -> JSONResponse:
    """
    Utility function for standardized JSON responses.
    """
    return JSONResponse(content=content, status_code=status_code)
