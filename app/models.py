from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import status
from starlette.responses import JSONResponse

class PoemResponseModel(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

    def json_response(self, status_code: int = status.HTTP_200_OK) -> JSONResponse:
        return JSONResponse(content=self.model_dump(), status_code=status_code)
