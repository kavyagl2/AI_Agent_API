from dataclasses import dataclass, field
import openai

from .openai_client import setup_llm

@dataclass
class StateManager:
    last_poem: str = ""
    client: openai.OpenAI = field(default_factory=setup_llm)

    def update_poem(self, poem: str):
        self.last_poem = poem

    def get_poem(self) -> str:
        return self.last_poem
