from pydantic import BaseModel, Field
from typing import Optional

class OpenAISchema(BaseModel):
    def run(self) -> str:
        raise NotImplementedError

class GeneratePoem(OpenAISchema):
    prompt: str = Field(..., description="The initial idea for the poem")
    style: Optional[str] = Field(None, description="Optional style of the poem")
    mood: Optional[str] = Field(None, description="Optional mood of the poem")
    purpose: Optional[str] = Field(None, description="Optional purpose of the poem")
    tone: Optional[str] = Field(None, description="Optional tone of the poem")

    def run(self) -> str:
        return f"Generating a {self.style or 'free-style'} poem with {self.mood or 'neutral'} mood for {self.purpose or 'general'} in a {self.tone or 'neutral'} tone."

class TrimPoem(OpenAISchema):
    poem: str = Field(..., description="The full text of the poem")

    def run(self) -> str:
        lines: list[str] = self.poem.strip().split("\n")
        trimmed_poem: list[str] = [
            lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
            for i in range(0, len(lines), 2)
        ]
        return "\n".join(trimmed_poem)

class Recapitalize(OpenAISchema):
    poem: str = Field(..., description="The poem text")

    def run(self) -> str:
        return self.poem.upper()

class Decapitalize(OpenAISchema):
    poem: str = Field(..., description="The poem text")

    def run(self) -> str:
        return self.poem.lower()

class HandlePoemQuery(OpenAISchema):
    poem: str = Field(..., description="The poem to analyze")
    user_query: str = Field(..., description="The user's question about the poem")

    def run(self) -> str:
        return f"Analyzing the poem and answering: {self.user_query}"
