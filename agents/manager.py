from enum import Enum
import time
from logging_config import logger

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
        start_time = time.time()
        logger.info(f"Incoming query: {query!r}")

        qtype = self.classify(query)
        logger.info(f"Selected agent: {qtype.value}")

        try:
            if qtype == QueryType.QUALITATIVE:
                response = self.qual_agent.answer(query)
                result = {"type": "qualitative", "response": response}
            elif qtype == QueryType.QUANTITATIVE:
                response = self.quant_agent.answer(query)
                result = {"type": "quantitative", "response": response}
            elif qtype == QueryType.COMPLEX:
                qual_part = self.qual_agent.answer(query)
                quant_part = self.quant_agent.answer(query)
                result = {"type": "complex", "response": self._merge(qual_part, quant_part)}
            elif qtype == QueryType.AMBIGUOUS:
                result = {
                    "type": "ambiguous",
                    "response": (
                        "Your question could be answered a couple of ways — could you "
                        "clarify? For example: policies/processes, or specific numbers/metrics?"
                    ),
                }
            else:
                result = {"type": "unsupported", "response": "I can't answer that yet — try rephrasing."}

        except Exception as e:
            logger.error(f"Error handling query {query!r}: {e}")
            result = {"type": "error", "response": f"Something went wrong: {e}"}

        elapsed = time.time() - start_time
        logger.info(f"Execution time: {elapsed:.3f}s for query {query!r}")

        return result

    def _merge(self, qual_part, quant_part) -> str:
        return f"**Qualitative:**\n{qual_part}\n\n**Quantitative:**\n{quant_part}"