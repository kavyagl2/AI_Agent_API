from fastapi import status

from app.models import PoemResponseModel


def internal_error_response(msg: str, error: Exception) -> PoemResponseModel:
    return PoemResponseModel(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=msg,
        data={"error": str(error)},
    )

class OpenAIException(BaseException):
    """Custom exception for handling OpenAI-related errors."""
    pass