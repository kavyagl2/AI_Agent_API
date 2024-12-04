from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from openai import OpenAI
from .state import State
from .utils import execute_tool, TOOL_FUNCTIONS

app = FastAPI()

# Global state for maintaining the last generated or modified poem
state = State()

# Create an OpenAI client instance
client = OpenAI()

def parse_user_intent(user_input: str, state: State) -> Dict[str, Any]:
    """
    Parse the user input to determine the appropriate tool and parameters.

    Args:
        user_input (str): The user's prompt or request.
        state (State): The current state containing the last generated poem.

    Returns:
        Dict[str, Any]: A dictionary with `tool_name` and `params`.
    """
    last_poem = state.get_poem()
    tool_name = ""
    params = {}

    # Example logic to determine the tool and parameters based on user input
    if "generate" in user_input.lower():
        tool_name = "generate_poem"
        params = {"prompt": user_input}
    elif "trim" in user_input.lower():
        tool_name = "trim_poem"
        params = {"poem": last_poem}
    elif "recapitalize" in user_input.lower():
        tool_name = "recapitalize"
        params = {"poem": last_poem}
    elif "decapitalize" in user_input.lower():
        tool_name = "decapitalize"
        params = {"poem": last_poem}
    elif "analyze" in user_input.lower():
        tool_name = "handle_poem_query"
        params = {"poem": last_poem, "user_query": user_input}
    else:
        raise HTTPException(status_code=400, detail="Invalid user input")

    return {"tool_name": tool_name, "params": params}

@app.post("/process_prompt")
async def process_prompt(user_input: str):
    """
    Analyze the user input and call the appropriate tool.

    Args:
        user_input (str): The user's prompt or request.

    Returns:
        Any: The result from the executed tool.
    """
    try:
        intent = parse_user_intent(user_input, state)
        tool_name = intent["tool_name"]
        params = intent["params"]
        result = execute_tool({"function": tool_name, "arguments": params}, list(TOOL_FUNCTIONS.values()))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))