from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from .state import State
from .utils import execute_tool, parse_user_intent

app = FastAPI()

# Global state for maintaining the last generated or modified poem
state = State()

@app.post("/process_request")
async def process_request(user_input: Dict[str, Any]):
    """
    Process a dynamic request for poem generation, transformation, or query.

    Args:
        user_input (Dict[str, Any]): Input JSON containing prompt details or transformation/query request.

    Returns:
        Dict[str, Any]: Response with the generated/transformed poem or query result.
    """
    try:
        # Parse the user's intent
        parsed_intent = parse_user_intent(user_input, state)
        tool_name = parsed_intent["tool_name"]
        params = parsed_intent["params"]

        # Execute the identified tool function
        result = execute_tool(tool_name, **params)

        # Update the state if the tool modifies or generates a poem
        if tool_name == "generate_poem" or tool_name in ["trim_poem", "recapitalize", "decapitalize"]:
            state.update_poem(str(result))
        # Return the result
        return {"result": result}

    except ValueError as e:
        # Handle invalid user input
        raise HTTPException(status_code=400, detail=str(e))
