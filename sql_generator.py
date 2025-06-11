from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import os
import re

llm = Ollama(model="gemma3:1b")

# Load schema from .sql file
def load_schema(path: str = "officedb.sql") -> str:
    if not os.path.exists(path):
        return "Schema not available."
    with open(path, "r") as f:
        return f.read()

def extract_sql_error(error_msg: str) -> str:
    """Extract the relevant part of the SQL error message."""
    # Common MySQL error patterns
    patterns = [
        r"Unknown column '([^']+)'",
        r"Table '([^']+)' doesn't exist",
        r"Column '([^']+)' in field list is ambiguous"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error_msg)
        if match:
            return match.group(1)
    return error_msg

def generate_sql(nl_query: str, max_attempts: int = 5) -> str:
    schema_context = load_schema()
    attempts = 0
    last_error = None
    last_sql = None
    
    while attempts < max_attempts:
        print(f"\nAttempt {attempts + 1} of {max_attempts}")
        
        if attempts == 0:
            # Initial prompt
            prompt = PromptTemplate(
                input_variables=["schema", "query"],
                template="""
You are a SQL expert and act as an SQL Assistant.

Understand the given database schema carefully:
{schema}

Important Schema Relationships:
- Employee salaries are stored in the Payroll table, not in the Employees table
- To get an employee's salary, you need to JOIN the Employees table with the Payroll table
- The Payroll table has a foreign key employee_id that references Employees.employee_id
- For current salary queries, you might want to use the most recent pay_date

Translate the following natural language request into a valid and accurate SQL query, using the correct tables and column references.

- Do not guess column locations — use only columns that exist in the appropriate tables
- Use JOINs if data comes from multiple tables
- Do not use GROUP BY unless aggregation (e.g., SUM, COUNT, AVG) is required
- Show identifying employee information (e.g., names) when relevant
- For salary queries, always JOIN with the Payroll table

Query: "{query}"

SQL:
"""
            )
            sql_query = llm.invoke(prompt.format(schema=schema_context, query=nl_query))
        else:
            # Correction prompt with detailed schema and error analysis
            error_detail = extract_sql_error(last_error)
            print(f"\nPrevious error: {last_error}")
            print(f"Error detail: {error_detail}")
            print(f"Previous SQL: {last_sql}")
            
            prompt = PromptTemplate(
                input_variables=["schema", "query", "error", "previous_sql", "error_detail"],
                template="""
You are a SQL expert and act as an SQL Assistant. The previous SQL query failed with this error:
{error}

The specific issue was related to: {error_detail}

The incorrect SQL was:
{previous_sql}

IMPORTANT - Database Schema and Relationships:
{schema}

CRITICAL POINTS TO FIX:
1. Check the schema to verify which table contains each column you're trying to use
2. For salary-related columns, they are in the Payroll table, not in Employees
3. Make sure to JOIN the correct tables based on the columns you need
4. Use proper table aliases and reference columns from their correct tables

Please fix the SQL query following these rules:
1. Review the schema to identify which table contains each column
2. Add necessary JOINs to access columns from different tables
3. Use proper table aliases and reference columns correctly
4. Ensure all column references exist in their respective tables

Original Query: "{query}"

Please provide the corrected SQL that follows these rules:
"""
            )
            sql_query = llm.invoke(prompt.format(
                schema=schema_context,
                query=nl_query,
                error=last_error,
                previous_sql=last_sql,
                error_detail=error_detail
            ))
        
        # Clean the SQL query
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()
        
        print(f"\nGenerated SQL (Attempt {attempts + 1}):")
        print(sql_query)
        
        # Store the current SQL for next iteration if needed
        last_sql = sql_query
        
        # Try to execute the query to check for errors
        try:
            from db import run_query
            results = run_query(sql_query)
            print(f"\nQuery executed successfully!")
            return sql_query  # Only return if query executes successfully
        except Exception as e:
            last_error = str(e)
            print(f"\nQuery failed: {last_error}")
            attempts += 1
            if attempts >= max_attempts:
                print(f"\nFailed to generate valid SQL after {max_attempts} attempts.")
                print(f"Last error: {last_error}")
                raise Exception(f"Failed to generate valid SQL after {max_attempts} attempts. Last error: {last_error}")
            continue  # Continue to next attempt
    
    # This should never be reached due to the raise in the loop
    raise Exception("Failed to generate valid SQL")
