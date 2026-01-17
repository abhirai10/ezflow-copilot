from typing import List

from sqlalchemy import text
from src.backend.services.sql_service import DatabaseManager


def get_audit_rules_from_db() -> List[dict]:
    """
    Fetch audit rules from Azure SQL database.
    
    Expected table structure:
    - audit_rules (rule_id, rule_name, rule_description, severity, is_active, created_at)
    
    Returns:
        List of audit rules from database
    """
    db = DatabaseManager.get_shared_db()
    
    # Query to fetch active audit rules from the database
    query = text("""
        SELECT 
            rule_id,
            rule_name,
            rule_description,
            severity
        FROM rules_master
        ORDER BY rule_id
    """)
    
    # Execute the query using the underlying SQLAlchemy engine
    with db._engine.connect() as connection:
        result = connection.execute(query)
        
        # Convert rows directly to list of dictionaries
        rules = [dict(row._mapping) for row in result]
    
    return rules
