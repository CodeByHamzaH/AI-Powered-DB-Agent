from fastapi import FastAPI, HTTPException
from models import QueryRequest, QueryResponse
from sql_generator import generate_sql, load_schema
from db import run_query
from validator import is_sql_safe
from query_validator import validate_query

app = FastAPI(title="MySQL NL Query API")

@app.post("/query", response_model=QueryResponse)
async def query_to_sql(request: QueryRequest):
    try:
        # Generate initial SQL query
        sql = generate_sql(request.query)
        
        # Load schema for validation
        schema = load_schema()
        
        # Validate the query using LangChain validation chain
        is_valid, reason, suggested_fix = validate_query(sql, schema)
        
        if not is_valid:
            # If invalid, try to fix the query
            if suggested_fix:
                print("Attempting to fix query:", suggested_fix)
                is_valid, reason, _ = validate_query(suggested_fix, schema)
                if is_valid:
                    sql = suggested_fix
                else:
                    raise HTTPException(status_code=400, detail=f"Invalid query: {reason}")
            else:
                raise HTTPException(status_code=400, detail=f"Invalid query: {reason}")
        
        # Additional safety check
        if not is_sql_safe(sql):
            raise HTTPException(status_code=400, detail="Unsafe SQL detected. Query rejected.")

        results = run_query(sql)
        if results is None:
            raise HTTPException(status_code=400, detail="Failed to execute query.")
        
        return QueryResponse(result=results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

