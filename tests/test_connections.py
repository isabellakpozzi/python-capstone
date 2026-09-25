import sqlite3
import pytest
from agents.quantitative_agent import QuantitativeAgent
from agents.qualitative_agent import QualitativeAgent


def test_sqlite_connection_succeeds(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE dummy (id INTEGER)")
    conn.commit()
    conn.close()

    conn2 = sqlite3.connect(db_path)
    result = conn2.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn2.close()

    assert ("dummy",) in result


def test_sqlite_connection_fails_gracefully_on_missing_file(tmp_path):
    missing_path = str(tmp_path / "does_not_exist.db")
    agent = QuantitativeAgent(db_path=missing_path, llm_fn=lambda p: "SELECT 1")
    assert agent.schema == ""  


def test_llm_function_is_called_and_returns_string(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE sales (id INTEGER, revenue REAL)")
    conn.execute("INSERT INTO sales VALUES (1, 500)")
    conn.commit()
    conn.close()

    calls = []

    def tracking_llm(prompt):
        calls.append(prompt)
        return "SELECT * FROM sales"

    agent = QuantitativeAgent(db_path=db_path, llm_fn=tracking_llm)
    result = agent.answer("Show me sales")

    assert len(calls) == 1  # LLM was actually invoked
    assert isinstance(result, str)  

def test_chroma_connection_and_llm_call(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "doc1.txt").write_text("This is a test policy document.")

    calls = []
    def tracking_llm(prompt):
        calls.append(prompt)
        return "test answer"

    chroma_path = str(tmp_path / "chroma_db")
    agent = QualitativeAgent(docs_path=str(docs_dir), llm_fn=tracking_llm, chroma_path=chroma_path)
    result = agent.answer("What is the policy?")

    assert agent.collection.count() == 1  
    assert len(calls) == 1  # LLM was invoked
    assert isinstance(result, str)