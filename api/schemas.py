from pydantic import BaseModel
from typing import Literal

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    type: Literal["qualitative", "quantitative", "complex", "ambiguous", "unsupported", "error"]
    response: str

class HealthResponse(BaseModel):
    status: str
    chroma_connected: bool
    sql_connected: bool