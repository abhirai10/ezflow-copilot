import threading
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from src.backend.core.config import settings

class DatabaseManager:
    _db_instance = None
    _lock = threading.Lock()

    @classmethod
    def get_shared_db(cls):
        """Returns a thread-safe globally shared database instance."""
        if cls._db_instance is None:
            with cls._lock:
                # Double-check pattern to prevent race conditions
                if cls._db_instance is None:
                    # Best practice: use pool_pre_ping for long-lived agent connections
                    engine = create_engine(
                        settings.azure_sql_connection_string, 
                        pool_pre_ping=True, 
                        pool_size=10, 
                        max_overflow=20
                    )
                    cls._db_instance = SQLDatabase(engine)
        return cls._db_instance
    

    @classmethod
    def get_tools(cls, model):
        """
        Factory method to generate SQL tools for an agent.
        Ensures tools are always linked to the singleton DB instance.
        """
        db = cls.get_shared_db()
        # Initialize the standard SQL toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        
        # Returns the list of standard tools: 
        # sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker
        return toolkit.get_tools()
