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

    def update_poem(self, poem):
        """Updates the state with the latest generated poem."""
        self.last_poem = poem

    def get_poem(self):
        """Retrieves the last generated poem from the state."""
        if not self.last_poem:
            raise ValueError("No poem has been generated yet.")
        return self.last_poem


def get_function_definitions() -> List[Dict[str, Any]]:
    definitions: List[Dict[str, Any]] = []
    for schema in [
        GeneratePoemSchema,
        TrimPoemSchema,
        RecapitalizeSchema,
        DecapitalizeSchema,
        HandlePoemQuerySchema,
    ]:
        definition = schema.Config.json_schema_extra
        definitions.append({"function": definition["name"]})
    return definitions