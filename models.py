from pydantic import BaseModel
from typing import List, Any

class QueryRequest(BaseModel):
    query: str  # Natural language input

class QueryResponse(BaseModel):
    result: List[Any]  # SQL query results as a list of rows
