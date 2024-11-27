from typing import List, Dict, Any
from openai import OpenAI

def get_completion(
    messages: List[Dict[str, str]],  # List of message dictionaries
    tool_functions: List[Any],       # List of available tool functions
    client: OpenAI,                  # OpenAI API client
    model: str                       # Model name (e.g., "gpt-4-turbo")
) -> str:
    while True:
        # Request completion from OpenAI
        completion = client.chat.completions.create(
            model=model,
            messages=messages,  
            tools=[{"type": "function", "function": func.openai_schema} for func in tool_functions],
            tool_choice="auto",
            temperature=0.5,
            max_tokens=4096,
        )

        # Get the first response message
        completion_message = completion.choices[0].message
        
        # If no tool calls, return the content
        if completion_message.get("tool_calls") is None:
            return completion_message.get("content", "")

        # Process tool calls
        for tool_call in completion_message["tool_calls"]:
            tool_result = execute_tool(tool_call, tool_functions)
            messages.append({
                "role": "tool",
                "name": tool_call["function"]["name"],
                "content": tool_result,
            })


def execute_tool(tool_call: Dict[str, Any], funcs: List[Any]) -> str:
    # Find the function that matches the tool call name
    func = next((func for func in funcs if func.__name__ == tool_call["function"]["name"]), None)
    if not func:
        return f"Error: Function {tool_call['function']['name']} not found."

    try:
        # Execute the tool with the provided arguments
        func_instance = func(**tool_call["function"]["arguments"])
        return func_instance.run()
    except Exception as e:
        return f"Error: {str(e)}"
