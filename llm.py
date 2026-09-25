import os
from dotenv import load_dotenv
from openai import OpenAI
from config import LLM_MODEL


load_dotenv()

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def call_llm(prompt: str) -> str:
    """Real LLM call — swap in whichever provider you have API access to."""
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

def mock_llm(prompt: str) -> str:
    if "SQL query" in prompt:
        return "SELECT * FROM sales LIMIT 5;"
    return "[MOCK ANSWER] Based on the provided context, here is a summary."