from fastapi import status
from app.models import PoemResponseModel

class OpenAIException(BaseException):
    """Custom exception for handling OpenAI-related errors."""
    pass

class FunctionNotFoundException(OpenAIException):
    """Custom exception for handling function not found errors."""
    pass


class PoemProcessingException(OpenAIException):
    """Custom exception for errors during poem processing."""
    pass


class UserInputException(OpenAIException):
    """Custom exception for invalid user input or missing required input."""
    pass


def internal_error_response(msg: str, error: Exception) -> PoemResponseModel:
    return PoemResponseModel(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=msg,
        data={"error": str(error)},
    )
