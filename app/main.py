from fastapi import FastAPI, Request, status
from typing import Optional

from starlette.responses import JSONResponse
from .poem_logic import (
    generate_poem,
    trim_poem,
    recapitalize,
    decapitalize,
    handle_poem_query,
)
from .state import StateManager
from .openai_client import setup_llm
from .models import PoemResponseModel
from .utils import internal_error_response, json_response

app = FastAPI()

# Initialize the OpenAI client and store it in the app state
app.state.llm_client = setup_llm()
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
) -> PoemResponseModel | JSONResponse:
    if not prompt:
        return json_response(
            {"message": "Prompt is required to generate a poem."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        state = get_state(request)
        poem = generate_poem(prompt, style, mood, purpose, tone)
        state.update_poem(poem)
        return json_response(
            {"message": "Poem generated successfully", "data": {"poem": poem}},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return internal_error_response("Failed to generate poem", e)


@app.put("/trim_poem", response_model=PoemResponseModel)
async def trim_poem_handler(request: Request) -> PoemResponseModel | JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return json_response(
            {"message": "No poem available to trim."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        trimmed_poem = trim_poem(current_poem)
        state.update_poem(trimmed_poem)
        return json_response(
            {
                "message": "Poem trimmed successfully",
                "data": {"trimmed_poem": trimmed_poem},
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return internal_error_response("Failed to trim poem", e)


@app.put("/recapitalize", response_model=PoemResponseModel)
async def recapitalize_handler(request: Request) -> PoemResponseModel | JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return json_response(
            {"message": "No poem text available to recapitalize."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        recapitalized_text = recapitalize(current_poem)
        state.update_poem(recapitalized_text)
        return json_response(
            {
                "message": "Poem recapitalized successfully",
                "data": {"recapitalized_text": recapitalized_text},
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return internal_error_response("Failed to recapitalize poem", e)


@app.put("/decapitalize", response_model=PoemResponseModel)
async def decapitalize_handler(request: Request) -> PoemResponseModel | JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return json_response(
            {"message": "No poem text available to decapitalize."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        decapitalized_text = decapitalize(current_poem)
        state.update_poem(decapitalized_text)
        return json_response(
            {
                "message": "Poem decapitalized successfully",
                "data": {"decapitalized_text": decapitalized_text},
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return internal_error_response("Failed to decapitalize poem", e)


@app.post("/handle_poem_query", response_model=PoemResponseModel)
async def handle_poem_query_handler(
    request: Request, user_query: str
) -> PoemResponseModel | JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        return json_response(
            {"message": "No poem available to analyze."},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if not user_query:
        return json_response(
            {"message": "User query is required to analyze the poem."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        answer = handle_poem_query(current_poem, user_query)
        return json_response(
            {"message": "Query handled successfully", "data": {"answer": answer}},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return internal_error_response("Failed to handle poem query", e)
