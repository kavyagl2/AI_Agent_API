from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import status


class PoemResponseModel(BaseModel):
    status_code: int = status.HTTP_200_OK
    message: str
    data: Optional[Dict[str, Any]] = None