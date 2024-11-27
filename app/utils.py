from typing import List, Dict, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam
from .tools import GeneratePoem, TrimPoem, Recapitalize, Decapitalize, HandlePoemQuery
from .state import State

TOOL_FUNCTIONS = {
    "generate_poem": GeneratePoem,
    "trim_poem": TrimPoem,
    "recapitalize": Recapitalize,
    "decapitalize": Decapitalize,
    "handle_poem_query": HandlePoemQuery,
}

def get_completion(
    messages: List[Dict[str, str]],  # List of messages
    tool_functions: List[Any],       # List of available tool functions
    client: OpenAI,                 
    model: str                       
) -> str:
    while True:
        # Request completion from OpenAI
        messages_params: List[ChatCompletionSystemMessageParam] = [
    ChatCompletionSystemMessageParam(role='system', **msg)
    for msg in messages
]
        completion = client.chat.completions.create(
            model=model,
            messages=messages_params,  
            tools=[{"type": "function", "function": func.openai_schema} for func in tool_functions],
            tool_choice="auto",
            temperature=0.5,
            max_tokens=4096,
        )

        # Get the first response message
        completion_message = completion.choices[0].message
        
        # If no tool calls, return the content
        if completion_message.tool_calls is None:
            return completion_message.content if completion_message.content else ""

        # Process tool calls
        for tool_call in completion_message.tool_calls:
            tool_call_dict = tool_call.to_dict()  
            tool_result = execute_tool(tool_call_dict, tool_functions)
            messages.append({
                "tool_call_id": tool_call.id, 
                "role": "tool", 
                "name": tool_call.function.name, 
                "content": str(tool_result),
    })


def execute_tool(tool_call_dict: Dict[str, Any], tool_functions: List[Any]) -> Union[str, int, None]:
    """
    Executes the requested tool based on the tool call dictionary.

    Args:
        tool_call_dict (Dict[str, Any]): The dictionary containing tool details.
        tool_functions (List[Any]): The list of available tool functions.

    Returns:
        Union[str, int, None]: The result of the tool execution.
    """
    tool_name = tool_call_dict["function"]
    kwargs = tool_call_dict.get("arguments", {})
    
    if tool_name not in TOOL_FUNCTIONS:
        raise ValueError(f"Tool '{tool_name}' not found.")
    
    try:
        tool = TOOL_FUNCTIONS[tool_name](**kwargs)
        return tool.run()
    except TypeError as e:
        raise ValueError(f"Error in executing tool '{tool_name}': {e}")


def parse_user_intent(user_input: Dict[str, Any], state: State) -> Dict[str, Any]:
    """
    Parses the user's input to determine the appropriate tool and its parameters.

    Args:
        user_input (Dict[str, Any]): The user's input as a dictionary.
        state (State): The state object managing the last generated poem.

    Returns:
        Dict[str, Any]: A dictionary containing the tool name and parameters.
    """
    tool_name: str = ""  
    params: Dict[str, Any] = {}

    if "prompt" in user_input:
        # Generate a new poem
        tool_name = "generate_poem"
        params = {key: user_input[key] for key in ["prompt", "style", "mood", "tone", "purpose"] if key in user_input}

    elif "transformation" in user_input:
        # Apply a transformation to the last poem
        tool_name = user_input["transformation"]
        last_poem = state.get_poem()
        if not last_poem:
            raise ValueError("No poem found in the current state to apply the transformation.")
        params = {"poem": last_poem}

    elif "user_query" in user_input:
        # Handle a query about the poem
        tool_name = "handle_poem_query"
        last_poem = state.get_poem()
        if not last_poem:
            raise ValueError("No poem found in the current state to handle the query.")
        params = {
            "poem": last_poem,
            "user_query": user_input["user_query"]
        }
    else:
        raise ValueError("Invalid input. Please provide a valid prompt or action.")
    
    return {"tool_name": tool_name, "params": params}
