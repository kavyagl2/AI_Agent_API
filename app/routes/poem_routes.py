from fastapi import APIRouter, Request, status
from typing import Optional
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.poem_logic import (
    generate_poem,
    trim_poem,
    recapitalize,
    decapitalize,
    handle_poem_query,
)
from app.state import State
from app.models import PoemResponseModel

router = APIRouter()
state = State()

@router.get("/generate_poem", response_model=PoemResponseModel)
async def generate_poem_handler(
    request: Request,
    prompt: str,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    purpose: Optional[str] = None,
    tone: Optional[str] = None,
) -> PoemResponseModel:
    if not prompt:
        return PoemResponseModel(
            message="Prompt is required", status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        poem = generate_poem(state.client, prompt, style, mood, purpose, tone)
        state.update_poem(poem)
        return PoemResponseModel(
            message="Poem generated successfully",
            data={"poem": poem},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return PoemResponseModel(
            message="Failed to generate poem",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put("/trim_poem", response_model=PoemResponseModel)
async def trim_poem_handler(request: Request) -> PoemResponseModel:
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(
            message="No poem available to trim.", 
            status_code=status.HTTP_404_NOT_FOUND
        )

    try:
        trimmed_poem = trim_poem(current_poem)
        state.update_poem(trimmed_poem)
        return PoemResponseModel(
            message="Poem trimmed successfully", 
            data={"trimmed_poem": trimmed_poem},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return PoemResponseModel(
            message="Failed to trim poem",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put("/recapitalize", response_model=PoemResponseModel)
async def recapitalize_handler(request: Request) -> PoemResponseModel:
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(
            message="No poem text available to recapitalize.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    try:
        recapitalized_text = recapitalize(current_poem)
        state.update_poem(recapitalized_text)
        return PoemResponseModel(
            message="Poem recapitalized successfully",
            data={"recapitalized_text": recapitalized_text},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return PoemResponseModel(
            message="Failed to recapitalize poem",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put("/decapitalize", response_model=PoemResponseModel)
async def decapitalize_handler(request: Request) -> PoemResponseModel:
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(
            message="No poem text available to decapitalize.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    try:
        decapitalized_text = decapitalize(current_poem)
        state.update_poem(decapitalized_text)
        return PoemResponseModel(
            message="Poem decapitalized successfully",
            data={"decapitalized_text": decapitalized_text},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return PoemResponseModel(
            message="Failed to decapitalize poem",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/handle_poem_query", response_model=PoemResponseModel)
async def handle_poem_query_handler(
    request: Request, user_query: str
) -> PoemResponseModel:
    current_poem = state.get_poem()
    if not current_poem:
        return PoemResponseModel(
            message="No poem available to analyze.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    if not user_query:
        return PoemResponseModel(
            message="User query is required to analyze the poem.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        answer = handle_poem_query(state.client, current_poem, user_query)
        return PoemResponseModel(
            message="Query handled successfully",
            data={"answer": answer},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return PoemResponseModel(
            message="Failed to handle poem query",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
