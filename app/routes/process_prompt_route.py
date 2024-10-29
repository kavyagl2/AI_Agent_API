from fastapi import APIRouter, status
from app.poem_logic import (
    generate_poem,
    trim_poem,
    recapitalize,
    decapitalize,
    handle_poem_query,
)
from app.state import State, get_function_definitions
from app.models import (
    PoemResponseModel, 
    PoemRequestModel, 
    GeneratePoemSchema, 
    TrimPoemSchema, 
    RecapitalizeSchema, 
    DecapitalizeSchema, 
    HandlePoemQuerySchema)

from app.utils import (
    OpenAIException,
    FunctionNotFoundException,
    PoemProcessingException,
    UserInputException,
    internal_error_response
)

import json
from typing import Callable, Any, Dict
from openai.types.chat import ChatCompletionToolParam

router = APIRouter()

# Initialize StateManager and store it in the app state
state = State()

def handle_function_call(function_name: str, function_to_call: Callable[..., Any], function_args: Dict[str, Any]) -> PoemResponseModel:
    """
    Utility function to handle function calls and manage exceptions consistently.
    """
    try:
        if function_name == "generate_poem":
            params = GeneratePoemSchema(**function_args)
            poem = function_to_call(client=state.client,**params.model_dump())
            state.update_poem(poem)
            return PoemResponseModel(
                message="Poem generated successfully",
                data={"poem": poem},
                status_code=status.HTTP_201_CREATED
            )

        elif function_name == "trim_poem":
            TrimPoemSchema.model_validate(function_args)
            current_poem = state.get_poem()
            if not current_poem:
                raise PoemProcessingException("No poem available to trim.")
            trimmed_poem = function_to_call(current_poem)
            state.update_poem(trimmed_poem)
            return PoemResponseModel(
                message="Poem trimmed successfully",
                data={"trimmed_poem": trimmed_poem},
                status_code=status.HTTP_200_OK
            )

        elif function_name == "recapitalize":
            RecapitalizeSchema.model_validate(function_args)
            current_poem = state.get_poem()
            if not current_poem:
                raise PoemProcessingException("No poem text available to recapitalize.")
            recapitalized_text = function_to_call(current_poem)
            state.update_poem(recapitalized_text)
            return PoemResponseModel(
                message="Poem recapitalized successfully",
                data={"recapitalized_text": recapitalized_text},
                status_code=status.HTTP_200_OK
            )

        elif function_name == "decapitalize":
            DecapitalizeSchema.model_validate(function_args)
            current_poem = state.get_poem()
            if not current_poem:
                raise PoemProcessingException("No poem text available to decapitalize.")
            decapitalized_text = function_to_call(current_poem)
            state.update_poem(decapitalized_text)
            return PoemResponseModel(
                message="Poem decapitalized successfully",
                data={"decapitalized_text": decapitalized_text},
                status_code=status.HTTP_200_OK
            )

        elif function_name == "handle_poem_query":
            params = HandlePoemQuerySchema(**function_args)
            current_poem = state.get_poem()
            if not current_poem:
                raise PoemProcessingException("No poem available to analyze.")
            user_query = function_args.get("user_query")
            if not user_query:
                raise UserInputException("User query is required to analyze the poem.")
            answer = function_to_call(state.client, current_poem, params.user_query)
            return PoemResponseModel(
                message="Query handled successfully",
                data={"answer": answer},
                status_code=status.HTTP_200_OK
            )

        else:
            raise FunctionNotFoundException(f"Function {function_name} not found.")

    except OpenAIException:
        return PoemResponseModel(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An OpenAI error occurred.",
            data={}
        )

    except Exception as e:
        return internal_error_response(f"An error occurred while processing {function_name}.", e)

@router.post("/process_prompt", response_model=PoemResponseModel)
async def process_prompt(request: PoemRequestModel):
    prompt = request.prompt 
    tools = [ChatCompletionToolParam(**tool) for tool in get_function_definitions()]
    try:
        response = state.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are an assistant that decides which function to call based on user input."},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="required"  
        )
        
    # Extract the message from the OpenAI response
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Ensuring there's a valid function call suggested by the model
        if tool_calls:
            available_functions = {
                "generate_poem": generate_poem,
                "trim_poem": trim_poem,
                "recapitalize": recapitalize,
                "decapitalize": decapitalize,
                "handle_poem_query": handle_poem_query
            }

            for tool_call in tool_calls:
                # Extract the function name and arguments from the tool call
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments) #change
                
                # Retrieve the function to call from the available functions
                if function_name in available_functions:
                    function_to_call = available_functions[function_name]

                    # Call the function and return the result
                    return handle_function_call(function_name, function_to_call, function_args)
                else:
                    return PoemResponseModel(
                        message=f"Function {function_name} not found.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

        # If no tool calls were found, return an error response
        return PoemResponseModel(
            message="No valid tool calls were found.",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return internal_error_response("Failed to process prompt", e)



