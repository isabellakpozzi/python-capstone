# tests/test_integration.py
import sqlite3
import pytest
from agents.manager import ManagerAgent
from agents.qualitative_agent import QualitativeAgent
from agents.quantitative_agent import QuantitativeAgent


@pytest.fixture
def full_system(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "security_policy.txt").write_text(
        "Our security policy requires two-factor authentication for all employees."
    )

    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, month TEXT, revenue REAL)")
    conn.execute("INSERT INTO sales (month, revenue) VALUES ('Jan', 1000)")
    conn.commit()
    conn.close()

    def fake_llm(prompt: str) -> str:
        if "SQL" in prompt or "SQLite" in prompt:
            return "SELECT * FROM sales"
        return "[TEST ANSWER] Summary of the retrieved policy."

    chroma_path = str(tmp_path / "chroma_db")
    qual = QualitativeAgent(docs_path=str(docs_dir), llm_fn=fake_llm, chroma_path=chroma_path)
    quant = QuantitativeAgent(db_path=db_path, llm_fn=fake_llm)
    manager = ManagerAgent(qual, quant)
    return manager

def test_qualitative_query_end_to_end(full_system):
    result = full_system.handle_query("What is our security policy?")
    assert result["type"] == "qualitative"
    assert "security_policy.txt" in result["response"]


def test_quantitative_query_end_to_end(full_system):
    result = full_system.handle_query("Show me monthly revenue trends")
    assert result["type"] == "quantitative"
    assert "1000" in result["response"]


def test_complex_query_merges_both_agents_end_to_end(full_system):
    result = full_system.handle_query(
        "How does revenue compare and what is our security policy?"
    )
    assert result["type"] == "complex"
    assert "Qualitative" in result["response"] or "qualitative" in result["response"].lower()
    assert "1000" in result["response"]  # quantitative part came through
    assert "security_policy.txt" in result["response"]  # qualitative part came through


def test_unsupported_query_end_to_end(full_system):
    result = full_system.handle_query("asdkjhaskjdh gibberish")
    assert result["type"] == "unsupported"