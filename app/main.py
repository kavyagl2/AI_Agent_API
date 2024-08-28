from fastapi import FastAPI, status
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from .poem_logic import (
    generate_poem,
    trim_poem,
    recapitalize,
    decapitalize,
    handle_poem_query,
)
from .state import State
from .models import PoemResponseModel, PoemRequestModel 
import json
from typing import Callable, Any, Dict


app = FastAPI()

# Initialize StateManager and store it in the app state
state = State()


@app.post("/process_prompt", response_model=PoemResponseModel)
async def process_prompt(request: PoemRequestModel):  # Change the parameter type to PoemRequestModel
    prompt = request.prompt  # Access the prompt from the request model

    if not prompt:
        return PoemResponseModel(
            message="Prompt is required", status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Use OpenAI to determine which function to call
        response = state.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that decides which function to call based on user input."},
                {"role": "user", "content": prompt}
            ],
            functions=[
                {
                    "name": "generate_poem",
                    "description": "Generate a poem based on a prompt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "style": {"type": "string"},
                            "mood": {"type": "string"},
                            "purpose": {"type": "string"},
                            "tone": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "trim_poem",
                    "description": "Trim a poem to half its length."
                },
                {
                    "name": "recapitalize",
                    "description": "Capitalize all letters in the poem."
                },
                {
                    "name": "decapitalize",
                    "description": "Lowercase all letters in the poem."
                },
                {
                    "name": "handle_poem_query",
                    "description": "Answer a question about a generated poem.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_query": {"type": "string"}
                        },
                        "required": ["user_query"]
                    }
                }
            ]
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        
        """typing available_functions as Dict[str, Callable[..., Any]], 
        so as to indicate that any callable can be present in the dictionary, 
        and it can accept any number of arguments with any type."""
        available_functions: Dict[str, Callable[..., Any]] = {
            "generate_poem": generate_poem,
            "trim_poem": trim_poem,
            "recapitalize": recapitalize,
            "decapitalize": decapitalize,
            "handle_poem_query": handle_poem_query
        }

        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                function_args = json.loads(tool_call.function.arguments)

                if function_to_call:
                    if function_name == "generate_poem":
                        poem = function_to_call(
                            **function_args
                        )
                        state.update_poem(poem)
                        return PoemResponseModel(
                            message="Poem generated successfully",
                            data={"poem": poem},
                            status_code=status.HTTP_201_CREATED
                        )

                    elif function_name == "trim_poem":
                        current_poem = state.get_poem()
                        if not current_poem:
                            return PoemResponseModel(
                                message="No poem available to trim.",
                                status_code=status.HTTP_404_NOT_FOUND
                            )
                        trimmed_poem = function_to_call(current_poem)
                        state.update_poem(trimmed_poem)
                        return PoemResponseModel(
                            message="Poem trimmed successfully",
                            data={"trimmed_poem": trimmed_poem},
                            status_code=status.HTTP_200_OK
                        )

                    elif function_name == "recapitalize":
                        current_poem = state.get_poem()
                        if not current_poem:
                            return PoemResponseModel(
                                message="No poem text available to recapitalize.",
                                status_code=status.HTTP_404_NOT_FOUND
                            )
                        recapitalized_text = function_to_call(current_poem)
                        state.update_poem(recapitalized_text)
                        return PoemResponseModel(
                            message="Poem recapitalized successfully",
                            data={"recapitalized_text": recapitalized_text},
                            status_code=status.HTTP_200_OK
                        )

                    elif function_name == "decapitalize":
                        current_poem = state.get_poem()
                        if not current_poem:
                            return PoemResponseModel(
                                message="No poem text available to decapitalize.",
                                status_code=status.HTTP_404_NOT_FOUND
                            )
                        decapitalized_text = function_to_call(current_poem)
                        state.update_poem(decapitalized_text)
                        return PoemResponseModel(
                            message="Poem decapitalized successfully",
                            data={"decapitalized_text": decapitalized_text},
                            status_code=status.HTTP_200_OK
                        )

                    elif function_name == "handle_poem_query":
                        current_poem = state.get_poem()
                        if not current_poem:
                            return PoemResponseModel(
                                message="No poem available to analyze.",
                                status_code=status.HTTP_404_NOT_FOUND
                            )
                        user_query = function_args.get("user_query")
                        if not user_query:
                            return PoemResponseModel(
                                message="User query is required to analyze the poem.",
                                status_code=status.HTTP_400_BAD_REQUEST
                            )
                        answer = function_to_call(state.client, current_poem, user_query)
                        return PoemResponseModel(
                            message="Query handled successfully",
                            data={"answer": answer},
                            status_code=status.HTTP_200_OK
                        )

        return PoemResponseModel(
            message="No valid tool calls were found.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return PoemResponseModel(
            message="Failed to process prompt",
            data={"error": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
