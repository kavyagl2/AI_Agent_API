from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Optional
from .poem_logic import generate_poem, trim_poem, recapitalize, decapitalize, handle_poem_query
from .state import StateManager
from .openai_client import setup_llm

app = FastAPI()

# Initializing the OpenAI client and storing it in the app state
app.state.llm_client = setup_llm()
app.state.state_manager = StateManager() 

# Dependency to manage state
def get_state(request: Request) -> StateManager:
    return request.app.state.state_manager

@app.post("/generate_poem", response_model=dict)
def generate_poem_handler(
    request: Request, 
    prompt: str, 
    style: Optional[str] = None, 
    mood: Optional[str] = None, 
    purpose: Optional[str] = None, 
    tone: Optional[str] = None
) -> JSONResponse:
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required to generate a poem."
        )
    try:
        state = get_state(request)
        poem = generate_poem(prompt, style, mood, purpose, tone)
        state.update_poem(poem)
        return JSONResponse(content={"poem": poem}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate poem: {str(e)}"
        )

@app.post("/trim_poem", response_model=dict)
def trim_poem_handler(request: Request) -> JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem available to trim."
        )
    try:
        trimmed_poem = trim_poem(current_poem)
        state.update_poem(trimmed_poem)
        return JSONResponse(content={"trimmed_poem": trimmed_poem}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trim poem: {str(e)}"
        )

@app.post("/recapitalize", response_model=dict)
def recapitalize_handler(request: Request) -> JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem text available to recapitalize."
        )
    try:
        recapitalized_text = recapitalize(current_poem)
        state.update_poem(recapitalized_text)
        return JSONResponse(content={"recapitalized_text": recapitalized_text}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recapitalize poem: {str(e)}"
        )

@app.post("/decapitalize", response_model=dict)
def decapitalize_handler(request: Request) -> JSONResponse:
    state = get_state(request)
    current_poem = state.get_poem()
    if not current_poem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No poem text available to decapitalize."
        )
    try:
        decapitalized_text = decapitalize(current_poem)
        state.update_poem(decapitalized_text)
        return JSONResponse(content={"decapitalized_text": decapitalized_text}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decapitalize poem: {str(e)}"
        )

@app.post("/handle_poem_query", response_model=dict)
def handle_poem_query_handler(request: Request, user_query: str) -> JSONResponse:
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
    try:
        answer = handle_poem_query(current_poem, user_query)
        return JSONResponse(content={"answer": answer}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle poem query: {str(e)}"
        )

# return types on all functions (function types of all the arguments)
# data classes python 
# exceptions handling - return a json response (explicit status code HTTP)