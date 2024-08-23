from fastapi import FastAPI, HTTPException, Request, status
from typing import Optional
from .poem_logic import generate_poem, trim_poem, recapitalize, decapitalize, handle_poem_query
from .state import StateManager
from .openai_client import setup_llm
from .models import PoemResponseModel
from .utils import handle_exceptions, json_response

app = FastAPI()

# Initialize the OpenAI client and store it in the app state
app.state.llm_client = setup_llm()
app.state.state_manager = StateManager()

# Dependency to manage state
def get_state(request: Request) -> StateManager:
    return request.app.state.state_manager

@app.post("/generate_poem", response_model=PoemResponseModel)
@handle_exceptions
def generate_poem_handler(
    request: Request, 
    prompt: str, 
    style: Optional[str] = None, 
    mood: Optional[str] = None, 
    purpose: Optional[str] = None, 
    tone: Optional[str] = None
) -> PoemResponseModel:
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required to generate a poem."
        )

    state = get_state(request)
    poem = generate_poem(prompt, style, mood, purpose, tone)
    state.update_poem(poem)
    return json_response(content={"poem": poem}, status_code=status.HTTP_201_CREATED)

@app.post("/trim_poem", response_model=PoemResponseModel)
@handle_exceptions
def trim_poem_handler(request: Request) -> PoemResponseModel:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem available to trim."
        )

    trimmed_poem = trim_poem(current_poem)
    state.update_poem(trimmed_poem)
    return json_response(content={"trimmed_poem": trimmed_poem}, status_code=status.HTTP_200_OK)

@app.post("/recapitalize", response_model=PoemResponseModel)
@handle_exceptions
def recapitalize_handler(request: Request) -> PoemResponseModel:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem text available to recapitalize."
        )

    recapitalized_text = recapitalize(current_poem)
    state.update_poem(recapitalized_text)
    return json_response(content={"recapitalized_text": recapitalized_text}, status_code=status.HTTP_200_OK)

@app.post("/decapitalize", response_model=PoemResponseModel)
@handle_exceptions
def decapitalize_handler(request: Request) -> PoemResponseModel:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem text available to decapitalize."
        )

    decapitalized_text = decapitalize(current_poem)
    state.update_poem(decapitalized_text)
    return json_response(content={"decapitalized_text": decapitalized_text}, status_code=status.HTTP_200_OK)

@app.post("/handle_poem_query", response_model=PoemResponseModel)
@handle_exceptions
def handle_poem_query_handler(request: Request, user_query: str) -> PoemResponseModel:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem available to analyze."
        )
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User query is required to analyze the poem."
        )

    answer = handle_poem_query(current_poem, user_query)
    return json_response(content={"answer": answer}, status_code=status.HTTP_200_OK)
