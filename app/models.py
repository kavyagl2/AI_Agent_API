from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import status

class PoemRequestModel(BaseModel):
    prompt: str
    style: Optional[str] = None
    mood: Optional[str] = None
    purpose: Optional[str] = None
    tone: Optional[str] = None

class PoemResponseModel(BaseModel):
    status_code: int = status.HTTP_200_OK
    message: str
    data: Optional[Dict[str, Any]] = None

class QueryModel(BaseModel):
    user_query: str

# OpenAI schemas (For function calling)
class GeneratePoemSchema(PoemRequestModel):
    class Config:
        json_schema_extra = {
            "name": "generate_poem",
            "description": "Generate a poem based on a prompt.",
        }

class TrimPoemSchema(BaseModel):
    class Config:
        json_schema_extra = {
            "name": "trim_poem",
            "description": "Trim a poem to half its length."
        }

class RecapitalizeSchema(BaseModel):
    class Config:
        json_schema_extra = {
            "name": "recapitalize",
            "description": "Capitalize all letters in the poem."
        }

class DecapitalizeSchema(BaseModel):
    class Config:
        json_schema_extra = {
            "name": "decapitalize",
            "description": "Lowercase all letters in the poem."
        }

class HandlePoemQuerySchema(QueryModel):
    class Config:
        json_schema_extra = {
            "name": "handle_poem_query",
            "description": "Answer a question about a generated poem."
        }
