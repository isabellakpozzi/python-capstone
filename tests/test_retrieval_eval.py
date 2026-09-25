import pytest
from agents.qualitative_agent import QualitativeAgent


@pytest.fixture
def eval_agent(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "security_policy.txt").write_text(
        "Our security policy requires two-factor authentication and password rotation every 90 days."
    )
    (docs_dir / "code_review.txt").write_text(
        "Code review requires at least one approval before merging a pull request."
    )
    (docs_dir / "complaints.txt").write_text(
        "Customer complaints are triaged within 4 business hours and resolved within 48 hours."
    )

    def fake_llm(p):
        return "test"

    chroma_path = str(tmp_path / "chroma_db")
    return QualitativeAgent(docs_path=str(docs_dir), llm_fn=fake_llm, chroma_path=chroma_path)


RETRIEVAL_EVAL_SET = [
    ("What is our security policy?", "security_policy.txt"),
    ("How often do we rotate passwords?", "security_policy.txt"),
    ("What's the process for reviewing code?", "code_review.txt"),
    ("How do we handle customer complaints?", "complaints.txt"),
    ("How quickly are complaints resolved?", "complaints.txt"),
]


@pytest.mark.parametrize("query,expected_source", RETRIEVAL_EVAL_SET)
def test_retrieval_returns_expected_top_document(eval_agent, query, expected_source):
    results = eval_agent.collection.query(query_texts=[query], n_results=1)
    top_source = results["metadatas"][0][0]["source"]
    assert top_source == expected_source, (
        f"Query '{query}' expected top match '{expected_source}' but got '{top_source}'"
    )