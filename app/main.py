from fastapi import FastAPI, Request, status
from typing import Optional, Union

from starlette.responses import JSONResponse
from .poem_logic import (
    generate_poem,
    trim_poem,
    recapitalize,
    decapitalize,
    handle_poem_query,
)
from .state import StateManager
from .models import PoemResponseModel
from .utils import internal_error_response

app = FastAPI()

# Initialize StateManager and store it in the app state
app.state.state_manager = StateManager()

# Dependency to manage state
def get_state(request: Request) -> StateManager:
    return request.app.state.state_manager

@app.post("/generate_poem", response_model=PoemResponseModel)
async def generate_poem_handler(
    request: Request,
    prompt: str,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    purpose: Optional[str] = None,
    tone: Optional[str] = None,
) -> Union[PoemResponseModel, JSONResponse]:
    if not prompt:
        return PoemResponseModel(message="Prompt is required to generate a poem.").json_response(status.HTTP_400_BAD_REQUEST)

    try:
        state = get_state(request)
        poem = generate_poem(state.client, prompt, style, mood, purpose, tone)
        state.update_poem(poem)
        return PoemResponseModel(message="Poem generated successfully", data={"poem": poem}).json_response(status.HTTP_201_CREATED)
    except Exception as e:
        return internal_error_response("Failed to generate poem", e)

@app.put("/trim_poem", response_model=PoemResponseModel)
async def trim_poem_handler(request: Request) -> Union[PoemResponseModel, JSONResponse]:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(message="No poem available to trim.").json_response(status.HTTP_404_NOT_FOUND)

    try:
        trimmed_poem = trim_poem(current_poem)
        state.update_poem(trimmed_poem)
        return PoemResponseModel(message="Poem trimmed successfully", data={"trimmed_poem": trimmed_poem}).json_response(status.HTTP_200_OK)
    except Exception as e:
        return internal_error_response("Failed to trim poem", e)

@app.put("/recapitalize", response_model=PoemResponseModel)
async def recapitalize_handler(request: Request) -> Union[PoemResponseModel, JSONResponse]:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(message="No poem text available to recapitalize.").json_response(status.HTTP_404_NOT_FOUND)

    try:
        recapitalized_text = recapitalize(current_poem)
        state.update_poem(recapitalized_text)
        return PoemResponseModel(message="Poem recapitalized successfully", data={"recapitalized_text": recapitalized_text}).json_response(status.HTTP_200_OK)
    except Exception as e:
        return internal_error_response("Failed to recapitalize poem", e)

@app.put("/decapitalize", response_model=PoemResponseModel)
async def decapitalize_handler(request: Request) -> Union[PoemResponseModel, JSONResponse]:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(message="No poem text available to decapitalize.").json_response(status.HTTP_404_NOT_FOUND)

    try:
        decapitalized_text = decapitalize(current_poem)
        state.update_poem(decapitalized_text)
        return PoemResponseModel(message="Poem decapitalized successfully", data={"decapitalized_text": decapitalized_text}).json_response(status.HTTP_200_OK)
    except Exception as e:
        return internal_error_response("Failed to decapitalize poem", e)

@app.post("/handle_poem_query", response_model=PoemResponseModel)
async def handle_poem_query_handler(
    request: Request, user_query: str
) -> Union[PoemResponseModel, JSONResponse]:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(message="No poem available to analyze.").json_response(status.HTTP_404_NOT_FOUND)
    if not user_query:
        return PoemResponseModel(message="User query is required to analyze the poem.").json_response(status.HTTP_400_BAD_REQUEST)

    try:
        answer = handle_poem_query(state.client, current_poem, user_query)
        return PoemResponseModel(message="Query handled successfully", data={"answer": answer}).json_response(status.HTTP_200_OK)
    except Exception as e:
        return internal_error_response("Failed to handle poem query", e)
