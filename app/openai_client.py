from openai import OpenAI
from dotenv import load_dotenv
import os

def setup_llm() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    client = OpenAI(api_key=api_key)
    return client