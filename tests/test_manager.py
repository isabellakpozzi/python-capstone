from agents.manager import ManagerAgent, QueryType


class FakeAgent:
    """Stands in for QualitativeAgent/QuantitativeAgent in tests."""
    def __init__(self, canned_response="fake response"):
        self.canned_response = canned_response
        self.last_query = None

    def answer(self, query):
        self.last_query = query
        return self.canned_response

def test_classifies_qualitative_query():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    result = manager.classify("What is our security policy?")
    assert result == QueryType.QUALITATIVE


def test_classifies_quantitative_query():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    result = manager.classify("Show me monthly revenue trends")
    assert result == QueryType.QUANTITATIVE


def test_classifies_complex_query():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    result = manager.classify(
        "How does our employee satisfaction compare and what policy affects it?"
    )
    assert result == QueryType.COMPLEX


def test_classifies_unsupported_query():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    result = manager.classify("asdkjhaskjdh random gibberish")
    assert result == QueryType.UNSUPPORTED

def test_routes_qualitative_to_qual_agent_only():
    qual = FakeAgent("qual answer")
    quant = FakeAgent("quant answer")
    manager = ManagerAgent(qual, quant)

    result = manager.handle_query("What is our security policy?")

    assert result["type"] == "qualitative"
    assert result["response"] == "qual answer"
    assert qual.last_query == "What is our security policy?"
    assert quant.last_query is None  # quant agent should NOT have been called


def test_routes_quantitative_to_quant_agent_only():
    qual = FakeAgent("qual answer")
    quant = FakeAgent("quant answer")
    manager = ManagerAgent(qual, quant)

    result = manager.handle_query("Show me monthly revenue trends")

    assert result["type"] == "quantitative"
    assert result["response"] == "quant answer"
    assert quant.last_query == "Show me monthly revenue trends"
    assert qual.last_query is None


def test_complex_query_merges_both_agents():
    qual = FakeAgent("qual part")
    quant = FakeAgent("quant part")
    manager = ManagerAgent(qual, quant)

    result = manager.handle_query(
        "How does employee satisfaction compare and what policy affects it?"
    )

    assert result["type"] == "complex"
    assert "qual part" in result["response"]
    assert "quant part" in result["response"]
    # both agents should have been called
    assert qual.last_query is not None
    assert quant.last_query is not None

def test_unsupported_query_does_not_call_any_agent():
    qual = FakeAgent()
    quant = FakeAgent()
    manager = ManagerAgent(qual, quant)

    result = manager.handle_query("asdkjhaskjdh")

    assert result["type"] == "unsupported"
    assert "rephrasing" in result["response"].lower()
    assert qual.last_query is None
    assert quant.last_query is None

def test_classifies_ambiguous_query():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    result = manager.classify("How are we doing on performance?")
    assert result == QueryType.AMBIGUOUS


def test_ambiguous_query_asks_for_clarification_without_calling_agents():
    qual = FakeAgent()
    quant = FakeAgent()
    manager = ManagerAgent(qual, quant)

    result = manager.handle_query("Tell me about our results")

    assert result["type"] == "ambiguous"
    assert "clarify" in result["response"].lower()
    assert qual.last_query is None
    assert quant.last_query is None