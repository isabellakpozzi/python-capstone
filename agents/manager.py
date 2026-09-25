from enum import Enum

class QueryType(Enum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    COMPLEX = "complex"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"

class ManagerAgent:
    def __init__(self, qual_agent, quant_agent):
        self.qual_agent = qual_agent
        self.quant_agent = quant_agent

    def classify(self, query: str) -> QueryType:
        q = query.lower()
        
        quant_keywords = ["revenue", "churn", "trend", "compare", "how many", "average", "analyze"]
        qual_keywords = ["policy", "policies", "process", "how do we", "explain"]
        vague_keywords = ["performance", "results", "review", "data", "numbers", "how are we doing"]

        has_quant = any(k in query.lower() for k in quant_keywords)
        has_qual = any(k in query.lower() for k in qual_keywords)
        has_vague = any(k in q for k in vague_keywords)

        if has_quant and has_qual:
            return QueryType.COMPLEX
        if has_quant:
            return QueryType.QUANTITATIVE
        if has_qual:
            return QueryType.QUALITATIVE
        if has_vague:
            return QueryType.AMBIGUOUS
        return QueryType.UNSUPPORTED

    def handle_query(self, query: str) -> dict:
        qtype = self.classify(query)

        if qtype == QueryType.QUALITATIVE:
            return {"type": "qualitative", "response": self.qual_agent.answer(query)}
        elif qtype == QueryType.QUANTITATIVE:
            return {"type": "quantitative", "response": self.quant_agent.answer(query)}
        elif qtype == QueryType.COMPLEX:
            qual_part = self.qual_agent.answer(query)
            quant_part = self.quant_agent.answer(query)
            return {"type": "complex", "response": self._merge(qual_part, quant_part)}
        elif qtype == QueryType.AMBIGUOUS:
            return {
                "type": "ambiguous",
                "response": (
                    "Your question could be answered a couple of ways — could you clarify? "
                    "For example: are you asking about documented policies/processes "
                    "(qualitative), or specific numbers/metrics (quantitative)?"
                ),
            }
        else:
            return {"type": "unsupported", "response": "I can't answer that yet — try rephrasing."}

    def _merge(self, qual_part, quant_part) -> str:
        return f"**Qualitative:**\n{qual_part}\n\n**Quantitative:**\n{quant_part}"