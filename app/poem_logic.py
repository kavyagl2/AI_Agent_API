from typing import Optional
from openai import OpenAI
from .utils import OpenAIException

def generate_poem(
    client: OpenAI,
    prompt: str,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    purpose: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    """
    Generate a poem based on the provided prompt and optional style, mood, purpose, and tone.

    Args:
        client (OpenAI): The OpenAI client for making API requests.
        prompt (str): The initial text or idea for the poem.
        style (Optional[str]): The style of the poem (e.g., sonnet, haiku).
        mood (Optional[str]): The mood of the poem (e.g., happy, sad).
        purpose (Optional[str]): The purpose of the poem (e.g., for a friend, a celebration).
        tone (Optional[str]): The tone of the poem (e.g., formal, casual).

    Returns:
        str: The generated poem.
    """
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details},
        ],
    )
    answer = response.choices[0].message.content
    if answer is None:
        raise OpenAIException()
    return answer.strip()


def trim_poem(poem: str) -> str:
    lines = poem.strip().split("\n")
    trimmed_poem = [
        lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
        for i in range(0, len(lines), 2)
    ]
    return "\n".join(trimmed_poem)


def recapitalize(poem: str) -> str:
    return poem.upper()


def decapitalize(poem: str) -> str:
    return poem.lower()


def handle_poem_query(client: OpenAI, poem: str, user_query: str) -> str:
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes poems.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    answer = response.choices[0].message.content
    if answer is None:
        raise OpenAIException()
    return answer.strip()
