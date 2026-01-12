import threading
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
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
    