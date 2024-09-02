from dataclasses import dataclass, field
import openai
from typing import List, Dict, Any
from .openai_client import setup_llm


@dataclass
class State:
    last_poem: str = ""
    client: openai.OpenAI = field(default_factory=setup_llm)

    def update_poem(self, poem: str):
        """Updates the state with the latest generated poem."""
        self.last_poem = poem

    def get_poem(self) -> str:
        """Retrieves the last generated poem from the state."""
        return self.last_poem


def get_function_definitions() -> List[Dict[str, Any]]:
    """
    Returns the list of function definitions to be used by the OpenAI client for
    tool calling based on user input.
    """
    return [
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
