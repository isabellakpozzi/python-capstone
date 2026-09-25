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

def test_clarification_response_resolves_to_quantitative():
    quant = FakeAgent("quant answer")
    manager = ManagerAgent(FakeAgent(), quant)

    ambiguous_result = manager.handle_query("Tell me about our results")
    assert ambiguous_result["type"] == "ambiguous"
    assert manager.pending_clarification_query == "Tell me about our results"

    follow_up = manager.handle_query("the numbers one")
    assert follow_up["type"] == "quantitative"
    assert follow_up["response"] == "quant answer"
    assert quant.last_query == "Tell me about our results" 
    assert manager.pending_clarification_query is None  


def test_clarification_response_resolves_to_qualitative():
    qual = FakeAgent("qual answer")
    manager = ManagerAgent(qual, FakeAgent())

    manager.handle_query("How are we doing on performance?")
    follow_up = manager.handle_query("I mean the policy side")
    assert follow_up["type"] == "qualitative"
    assert qual.last_query == "How are we doing on performance?"


def test_unreasonable_clarification_response_gives_up_gracefully():
    manager = ManagerAgent(FakeAgent(), FakeAgent())
    manager.handle_query("Tell me about our results")

    follow_up = manager.handle_query("asdkjhaskjdh")
    assert follow_up["type"] == "unsupported"
    assert "rephrase" in follow_up["response"].lower()
    assert manager.pending_clarification_query is None  # no infinite loop


def test_clarification_state_does_not_persist_after_resolution():
    manager = ManagerAgent(FakeAgent("qual"), FakeAgent("quant"))
    manager.handle_query("Tell me about our results")
    manager.handle_query("the numbers one")  # resolves and clears state

    result = manager.handle_query("What is our security policy?")
    assert result["type"] == "qualitative"