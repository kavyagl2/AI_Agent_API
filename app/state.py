from dataclasses import dataclass, field
import openai
from typing import List, Dict, Any
from .openai_client import setup_llm
from .models import (
    GeneratePoemSchema,
    TrimPoemSchema,
    RecapitalizeSchema,
    DecapitalizeSchema,
    HandlePoemQuerySchema
)


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
    return [
        GeneratePoemSchema.model_json_schema(),
        TrimPoemSchema.model_json_schema(),
        RecapitalizeSchema.model_json_schema(),
        DecapitalizeSchema.model_json_schema(),
        HandlePoemQuerySchema.model_json_schema(),
    ]