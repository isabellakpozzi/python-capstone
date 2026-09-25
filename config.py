import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DB_PATH = os.environ.get("DB_PATH", "data/enterprise.db")
DOCS_PATH = os.environ.get("DOCS_PATH", "data/docs")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_db")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")