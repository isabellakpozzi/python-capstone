from enum import Enum
import time
from logging_config import logger

class QueryType(Enum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    COMPLEX = "complex"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"

QUANT_CLARIFICATION_WORDS = ("quantitative", "numbers", "data", "the second one", "metrics", "stats")
QUAL_CLARIFICATION_WORDS = ("qualitative", "policy", "policies", "the first one", "process")

class ManagerAgent:
    def __init__(self, qual_agent, quant_agent):
        self.qual_agent = qual_agent
        self.quant_agent = quant_agent
        self.pending_clarification_query = None

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

        if self.pending_clarification_query is not None:
            result = self._resolve_clarification(query)
            elapsed = time.time() - start_time
            logger.info(f"Execution time: {elapsed:.3f}s for query {query!r}")
            return result

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
                self.pending_clarification_query = query
                result = {
                    "type": "ambiguous",
                    "response": (
                        "Your question could be answered a couple of ways — could you clarify? "
                        "For example: are you asking about documented policies/processes "
                        "(qualitative), or specific numbers/metrics (quantitative)?"
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

    def _resolve_clarification(self, response: str) -> dict:
        original_query = self.pending_clarification_query
        self.pending_clarification_query = None  
        r = response.lower().strip()

        if any(word in r for word in QUANT_CLARIFICATION_WORDS):
            logger.info(f"Clarification resolved to quantitative for original query: {original_query!r}")
            return {"type": "quantitative", "response": self.quant_agent.answer(original_query)}

        if any(word in r for word in QUAL_CLARIFICATION_WORDS):
            logger.info(f"Clarification resolved to qualitative for original query: {original_query!r}")
            return {"type": "qualitative", "response": self.qual_agent.answer(original_query)}

        # unreasonable response case to avoid looping forever
        logger.info(f"Clarification response {response!r} was not understood; giving up gracefully")
        return {
            "type": "unsupported",
            "response": (
                "I still couldn't tell which you meant — could you rephrase your original "
                "question directly instead?"
            ),
        }

    def _merge(self, qual_part, quant_part) -> str:
        return f"**Qualitative:**\n{qual_part}\n\n**Quantitative:**\n{quant_part}"