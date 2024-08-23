from typing import Optional
from app.openai_client import setup_llm

client = setup_llm()

def generate_poem(
    prompt: str, 
    style: Optional[str] = None, 
    mood: Optional[str] = None, 
    purpose: Optional[str] = None, 
    tone: Optional[str] = None
) -> str:
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
    lines = poem.strip().split('\n')
    trimmed_poem = [
        lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
        for i in range(0, len(lines), 2)
    ]
    return '\n'.join(trimmed_poem)

def recapitalize(poem: str) -> str:
    return poem.upper()

def decapitalize(poem: str) -> str:
    return poem.lower()

def handle_poem_query(poem: str, user_query: str) -> str:
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

#initilization logic should run together
