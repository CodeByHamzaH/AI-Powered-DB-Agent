import re

# Improved blacklist to catch dangerous SQL commands
BLACKLIST = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bUPDATE\b",
]

def is_sql_safe(sql: str) -> bool:
    """
    Returns True if SQL query passes safety checks:
    - No dangerous SQL keywords (e.g. DROP, DELETE)
    - Only one statement is allowed (even with a semicolon)
    """
    # Normalize and clean input
    sql_clean = sql.strip().rstrip(";").strip()
    sql_upper = sql_clean.upper()

    # Check for dangerous keywords
    for pattern in BLACKLIST:
        if re.search(pattern, sql_upper):
            return False

    # Check for multiple statements (by counting semicolons)
    if sql.count(";") > 1:
        return False

    return True
