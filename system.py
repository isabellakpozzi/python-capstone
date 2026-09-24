from agents.manager import ManagerAgent
from agents.qualitative_agent import QualitativeAgent
from agents.quantitative_agent import QuantitativeAgent

def build_system(llm_fn):
    qual = QualitativeAgent(docs_path="data/docs", llm_fn=llm_fn)
    quant = QuantitativeAgent(db_path="data/enterprise.db", llm_fn=llm_fn)
    return ManagerAgent(qual, quant)