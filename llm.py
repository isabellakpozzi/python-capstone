# llm.py
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm(prompt: str) -> str:
    """Real LLM call — swap in whichever provider you have API access to."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def mock_llm(prompt: str) -> str:
    if "SQL query" in prompt:
        return "SELECT * FROM sales LIMIT 5;"
    return "[MOCK ANSWER] Based on the provided context, here is a summary."