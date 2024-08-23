from typing import Optional
from app.openai_client import setup_llm

# Initialize the OpenAI client
client = setup_llm()

def generate_poem(
    prompt: str, 
    style: Optional[str] = None, 
    mood: Optional[str] = None, 
    purpose: Optional[str] = None, 
    tone: Optional[str] = None
) -> str:
    """
    Generate a poem based on the provided prompt and optional style, mood, purpose, and tone.
    
    Args:
        prompt (str): The initial text or idea for the poem.
        style (Optional[str]): The style of the poem (e.g., sonnet, haiku).
        mood (Optional[str]): The mood of the poem (e.g., happy, sad).
        purpose (Optional[str]): The purpose of the poem (e.g., for a friend, a celebration).
        tone (Optional[str]): The tone of the poem (e.g., formal, casual).
    
    Returns:
        str: The generated poem.
    """
    # Construct the detailed prompt for the model
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details}
        ]
    )
    poem = response.choices[0].message.content.strip()
    return poem

def trim_poem(poem: str) -> str:
    """
    Trim the poem by combining every two lines into one.

    Args:
        poem (str): The original poem.

    Returns:
        str: The trimmed version of the poem.
    """
    lines = poem.strip().split('\n')
    trimmed_poem = [
        lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
        for i in range(0, len(lines), 2)
    ]
    return '\n'.join(trimmed_poem)

def recapitalize(poem: str) -> str:
    """
    Recapitalize all text in the poem to uppercase.

    Args:
        poem (str): The original poem.

    Returns:
        str: The poem with all text in uppercase.
    """
    return poem.upper()

def decapitalize(poem: str) -> str:
    """
    Decapitalize all text in the poem to lowercase.

    Args:
        poem (str): The original poem.

    Returns:
        str: The poem with all text in lowercase.
    """
    return poem.lower()

def handle_poem_query(poem: str, user_query: str) -> str:
    """
    Analyze the poem and respond to a user query about it.

    Args:
        poem (str): The poem text to analyze.
        user_query (str): The user's query regarding the poem.

    Returns:
        str: The response to the user's query.
    """
    # Construct the prompt for the model to analyze the poem
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner."
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content.strip()
    return answer
