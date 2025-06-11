from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.schema.runnable import RunnableSequence
from typing import Tuple
import json

llm = Ollama(model="gemma3:1b")

def create_validation_chain() -> RunnableSequence:
    validation_prompt = PromptTemplate(
        input_variables=["query", "schema"],
        template="""
You are a SQL query validator. Your task is to validate if the given SQL query is:
1. Syntactically correct
2. Safe to execute (no dangerous operations)
3. Compatible with the database schema

Database Schema:
{schema}

SQL Query to validate:
{query}

Respond with a JSON object in this format:
{{
    "is_valid": true/false,
    "reason": "explanation of validation result",
    "suggested_fix": "suggested fix if invalid, empty string if valid"
}}

IMPORTANT: Your response must be a valid JSON object. Do not include any additional text or explanation outside the JSON.
"""
    )
    
    # Create a runnable sequence: prompt -> llm -> parse_json
    return validation_prompt | llm

def parse_validation_result(result: str) -> Tuple[bool, str, str]:
    """Parse the LLM response into a validation result tuple."""
    try:
        # Clean the response to ensure it's valid JSON
        cleaned_result = result.strip()
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()
        
        validation_result = json.loads(cleaned_result)
        return (
            validation_result.get("is_valid", False),
            validation_result.get("reason", "Unknown validation error"),
            validation_result.get("suggested_fix", "")
        )
    except json.JSONDecodeError as e:
        print(f"Failed to parse validation result: {e}")
        print(f"Raw result: {result}")
        return False, "Failed to parse validation result", ""

def validate_query(query: str, schema: str) -> Tuple[bool, str, str]:
    """
    Validates a SQL query using LangChain validation chain.
    Returns: (is_valid, reason, suggested_fix)
    """
    try:
        chain = create_validation_chain()
        result = chain.invoke({"query": query, "schema": schema})
        return parse_validation_result(result)
    except Exception as e:
        print(f"Error during query validation: {e}")
        return False, f"Validation error: {str(e)}", "" 