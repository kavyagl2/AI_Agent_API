from typing import List, Dict, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam
from .tools import GeneratePoem, TrimPoem, Recapitalize, Decapitalize, HandlePoemQuery


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
) -> str | None:
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
            return (completion_message.content)
        else:
            messages.append({k: str(v) for k, v in completion_message.to_dict().items()})

        # Process tool calls
        for tool_call in completion_message.tool_calls:
            tool_call_dict = tool_call.to_dict()  
            tool_result = execute_tool(tool_call_dict, tool_functions)
            if isinstance(tool_result, int):
                tool_result = str(tool_result)
            messages.append({
                "tool_call_id": tool_call.id, 
                "role": "tool", 
                "name": tool_call.function.name, 
                "content": str(tool_result)})
            return tool_result            
 
def execute_tool(tool_call_dict: Dict[str, Any], tool_functions: List[Any],) -> Union[str, int, None]:
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


