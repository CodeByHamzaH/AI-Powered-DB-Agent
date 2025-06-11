import mysql.connector
from mysql.connector import Error
from typing import List, Tuple
import re

# Update with your actual DB credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "OfficeDB"
}

def clean_sql_query(query: str) -> str:
    """
    Removes Markdown-style SQL code block markers like ```sql ... ```
    """
    # Remove triple backticks and optional 'sql' prefix
    query = re.sub(r"```(?:sql)?", "", query, flags=re.IGNORECASE)
    query = query.replace("```", "")
    return query.strip()

def run_query(sql_query: str) -> List[Tuple]:
    """
    Connect to MySQL, execute the SQL query, and fetch all results.
    Raises an exception if there's an error.
    """
    try:
        clean_query = clean_sql_query(sql_query)
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(clean_query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Error as e:
        print(f"Error while executing query: {e}")
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {str(e)}")