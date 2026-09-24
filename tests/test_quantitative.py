import sqlite3
import pytest
from agents.quantitative_agent import QuantitativeAgent

@pytest.fixture
def test_db_path(tmp_path):
    """Creates a small, known SQLite DB for this test only."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY, month TEXT, region TEXT, revenue REAL
        )
    """)
    conn.execute("INSERT INTO sales (month, region, revenue) VALUES ('Jan', 'West', 1000)")
    conn.execute("INSERT INTO sales (month, region, revenue) VALUES ('Feb', 'West', 1500)")
    conn.commit()
    conn.close()
    return db_path

def make_fake_llm(sql_to_return):
    def fake_llm(prompt):
        return sql_to_return
    return fake_llm

def test_answer_executes_valid_sql_and_returns_results(test_db_path):
    fake_llm = make_fake_llm("SELECT * FROM sales WHERE region = 'West'")
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    result = agent.answer("Show me West region sales")

    assert "1000" in result
    assert "1500" in result
    assert "West" in result


def test_answer_includes_generated_sql_in_output(test_db_path):
    fake_llm = make_fake_llm("SELECT * FROM sales")
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    result = agent.answer("Show me all sales")

    assert "SELECT * FROM sales" in result

def test_answer_handles_invalid_sql_gracefully(test_db_path):
    fake_llm = make_fake_llm("SELEKT * FORM sales")  # intentionally malformed
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    result = agent.answer("This will generate broken SQL")

    assert "failed" in result.lower() or "error" in result.lower()
    # Should NOT raise an exception — pytest would fail this test automatically if it did


def test_answer_handles_query_referencing_nonexistent_table(test_db_path):
    fake_llm = make_fake_llm("SELECT * FROM nonexistent_table")
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    result = agent.answer("Query a table that doesn't exist")

    assert "failed" in result.lower() or "error" in result.lower()

def test_answer_handles_query_with_no_matching_rows(test_db_path):
    fake_llm = make_fake_llm("SELECT * FROM sales WHERE region = 'Nonexistent'")
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    result = agent.answer("Show me sales for a region with no data")

    assert "no results" in result.lower()

def test_agent_loads_schema_on_init(test_db_path):
    fake_llm = make_fake_llm("SELECT 1")
    agent = QuantitativeAgent(db_path=test_db_path, llm_fn=fake_llm)

    assert "sales" in agent.schema.lower()
    assert "revenue" in agent.schema.lower()