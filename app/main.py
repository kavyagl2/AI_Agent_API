from fastapi import FastAPI, HTTPException
from .utils import execute_tool, get_completion
from .state import State
from .openai_client import setup_llm
from .tools import GeneratePoem, TrimPoem, Recapitalize, Decapitalize, HandlePoemQuery

app = FastAPI()

state = State()

TOOLS_FUNCTIONS = [GeneratePoem, TrimPoem, Recapitalize, Decapitalize, HandlePoemQuery]

@app.post("/process_prompt")
async def process_prompt(user_input: str):
    try:
        messages = [
            {"role": "system", "content": "Analyze the user's input and determine the appropriate tool to use."},
            {"role": "user", "content": user_input},
        ]

        # Get completion from OpenAI API to analyze the user query and select the right tool
        result = get_completion(
            messages=messages,
            tool_functions=TOOLS_FUNCTIONS,
            client=setup_llm(), 
            model="gpt-4-turbo"
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
