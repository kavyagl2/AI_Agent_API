from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam

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
            tool_call_dict = tool_call.to_dict()  # assuming to_dict() method exists
            tool_result = execute_tool(tool_call_dict, tool_functions)
            messages.append({
                "tool_call_id": tool_call.id, 
                "role": "tool", 
                "name": tool_call.function.name, 
                "content": tool_result  ,
    })


def execute_tool(tool_call: Dict[str, Any], funcs: List[Any]) -> str:
    # Find the function that matches the tool call name
    func = next(iter([func for func in funcs if func.__name__ == tool_call['function']['name']]), None)
    if not func:
        return f"Error: Function {tool_call['function']['name']} not found."

    try:
        # Execute the tool with the provided arguments
        func_instance = func(**eval(tool_call['function']['arguments']))
        output = func_instance.run()
        return output
    except Exception as e:
        return f"Error: {str(e)}"