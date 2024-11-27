from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .tools import GeneratePoem, TrimPoem, Recapitalize, Decapitalize, HandlePoemQuery 

app = FastAPI()

# Define the request body model for generating poems
class PoemRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    mood: Optional[str] = None
    tone: Optional[str] = None
    purpose: Optional[str] = None
    transformation: Optional[str] = None  

class PoemQueryRequest(BaseModel):
    poem: str 
    user_query: str  
    
@app.post("/generate_poem")
async def generate_poem(request: PoemRequest):
    # Generate the poem
    poem = GeneratePoem(prompt=request.prompt, style=request.style, mood=request.mood, tone=request.tone, purpose=request.purpose).run()
    
    # Apply transformation if requested
    if request.transformation:
        if request.transformation == "trim":
            poem = TrimPoem(poem=poem).run()
        elif request.transformation == "capitalize":
            poem = Recapitalize(poem=poem).run()
        elif request.transformation == "decapitalize":
            poem = Decapitalize(poem=poem).run()
        else:
            raise HTTPException(status_code=400, detail="Invalid transformation requested")

    return {"poem": poem}


@app.post("/handle_poem_query")
async def handle_poem_query(request: PoemQueryRequest):
    # Handle the poem query using the provided HandlePoemQuery tool
    response = HandlePoemQuery(poem=request.poem, user_query=request.user_query).run()
    return {"response": response}
