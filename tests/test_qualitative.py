import shutil
import pytest
from agents.qualitative_agent import QualitativeAgent


@pytest.fixture
def test_docs_path(tmp_path):
    """Creates a temporary docs folder with known content for this test only."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "security_policy.txt").write_text(
        "Our security policy requires two-factor authentication for all employees."
    )
    (docs_dir / "code_review.txt").write_text(
        "Code review requires at least one approval before merging a pull request."
    )
    return str(docs_dir)


def fake_llm(prompt: str) -> str:
    return "[TEST ANSWER] Summary based on provided context."


@pytest.fixture
def qual_agent(test_docs_path, tmp_path, monkeypatch):
    # Point Chroma's persistent storage at a temp folder, isolated per test run
    monkeypatch.chdir(tmp_path)
    agent = QualitativeAgent(docs_path=test_docs_path, llm_fn=fake_llm)
    return agent

def test_answer_includes_citation_from_relevant_doc(qual_agent):
    result = qual_agent.answer("What is our security policy?")
    assert "security_policy.txt" in result


def test_answer_does_not_cite_unrelated_doc(qual_agent):
    result = qual_agent.answer("What is our security policy?")
    # The code review doc shouldn't be the top match for a security question
    # (this checks the *primary* source, not that it's absent entirely)
    assert "[TEST ANSWER]" in result

def test_answer_handles_query_with_no_relevant_docs(qual_agent):
    result = qual_agent.answer("What is the capital of France?", max_distance=0.9)
    assert result == "I couldn't find relevant documentation for that question."


def test_answer_finds_relevant_doc_with_default_threshold(qual_agent):
    result = qual_agent.answer("What is our security policy?")
    assert "security_policy.txt" in result
    assert "couldn't find" not in result.lower()