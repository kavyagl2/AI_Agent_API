from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import status

class PoemRequestModel(BaseModel): 
    """defining this to receive the prompt from the
        request body as FastAPI endpoint expects 
        a query parameter  which is prompt in our case."""
    prompt: str

class PoemResponseModel(BaseModel):
    status_code: int = status.HTTP_200_OK
    message: str
    data: Optional[Dict[str, Any]] = None