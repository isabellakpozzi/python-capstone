from fastapi import FastAPI, HTTPException
from api.schemas import QueryRequest, QueryResponse, HealthResponse
from system import build_system
from llm import call_llm
from config import DB_PATH, DOCS_PATH, CHROMA_PATH
from logging_config import logger

app = FastAPI(
    title="Enterprise Docs Assistant API",
    description="Multi-agent RAG system for enterprise documentation queries",
    version="1.0.0",
)

manager = build_system(llm_fn=call_llm)


@app.get("/health", response_model=HealthResponse)
def health_check():
    chroma_ok = True
    sql_ok = True
    try:
        manager.qual_agent.collection.count()
    except Exception:
        chroma_ok = False
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        sql_ok = False

    return HealthResponse(
        status="ok" if (chroma_ok and sql_ok) else "degraded",
        chroma_connected=chroma_ok,
        sql_connected=sql_ok,
    )


@app.post("/query", response_model=QueryResponse)
def query_manager(request: QueryRequest):
    """Routes a query through the full multi-agent Manager."""
    try:
        result = manager.handle_query(request.query)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"API /query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/qualitative", response_model=QueryResponse)
def query_qualitative(request: QueryRequest):
    """Bypasses the Manager and calls the Qualitative agent directly."""
    response = manager.qual_agent.answer(request.query)
    return QueryResponse(type="qualitative", response=response)


@app.post("/query/quantitative", response_model=QueryResponse)
def query_quantitative(request: QueryRequest):
    """Bypasses the Manager and calls the Quantitative agent directly."""
    response = manager.quant_agent.answer(request.query)
    return QueryResponse(type="quantitative", response=response)