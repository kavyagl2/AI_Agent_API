from app.openai_client import setup_llm
from typing import Optional
from pydantic import Field
from instructor import OpenAISchema
from .utils import get_completion
from .state import State 

state = State()
class GeneratePoem(OpenAISchema):
    prompt: str = Field(..., description="The initial idea for the poem")
    style: Optional[str] = Field(None, description="Optional style of the poem")
    mood: Optional[str] = Field(None, description="Optional mood of the poem")
    purpose: Optional[str] = Field(None, description="Optional purpose of the poem")
    tone: Optional[str] = Field(None, description="Optional tone of the poem")

    def __init__(self, prompt, style=None, mood=None, purpose=None, tone=None):
        
        self.prompt = prompt
        self.style = style
        self.mood = mood
        self.purpose = purpose
        self.tone = tone
        self.client = setup_llm()

    def run(self):
        # Create the prompt message
        openai_prompt = (
            f"Write a poem based on the following details:\n"
            f"Prompt: {self.prompt}\n"
            f"Style: {self.style or 'free-style'}\n"
            f"Mood: {self.mood or 'neutral'}\n"
            f"Purpose: {self.purpose or 'general'}\n"
            f"Tone: {self.tone or 'neutral'}\n"
        )

        messages = [
            {"role": "system", "content": "You are a creative assistant that generates poems."},
            {"role": "user", "content": openai_prompt},
        ]

        try:
            result = get_completion(messages, [GeneratePoem], self.client, model="gpt-4-turbo")
            state.update_poem(result)
        except Exception as e:
            return f"Error generating poem: {str(e)}"


class TrimPoem(OpenAISchema):
    poem: Optional[str] = Field(None, description="The full text of the poem")

    def run(self):
        poem = self.poem or state.get_poem() 
        # Trimming the poem by combining alternate lines into a shorter poem
        lines = poem.strip().split("\n")
        trimmed_poem = [
            lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
            for i in range(0, len(lines), 2)
        ]
        return "\n".join(trimmed_poem)


class Recapitalize(OpenAISchema):
    poem: Optional[str] = Field(None, description="The poem text")

    def run(self):
        poem = self.poem or state.get_poem()
        return poem.upper()


class Decapitalize(OpenAISchema):
    poem: Optional[str] = Field(None, description="The poem text")

    def run(self):        
        poem = self.poem or state.get_poem() 
        return poem.lower()


class HandlePoemQuery(OpenAISchema):
    poem: Optional[str] = Field(None, description="The poem to analyze")
    user_query: str = Field(..., description="The user's question about the poem")

    def __init__(self, poem, user_query):
        self.poem = poem or state.get_poem()
        self.user_query = user_query
        self.client = setup_llm()

    def run(self):
        openai_prompt = (
            f"The user has a query about this poem:\n\n{self.poem}\n\n"
            f"User Query: {self.user_query}\n"
            f"Provide a detailed and insightful response based on the poem."
        )

        messages = [
            {"role": "system", "content": "You are an expert at analyzing poems and answering questions about them."},
            {"role": "user", "content": openai_prompt},
        ]

        try:
            return get_completion(messages, [HandlePoemQuery], self.client, model="gpt-4-turbo")
        except Exception as e:
            return f"Error analyzing poem: {str(e)}"
