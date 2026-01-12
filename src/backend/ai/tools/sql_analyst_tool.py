from langchain_community.agent_toolkits import SQLDatabaseToolkit
from src.backend.services.sql_service import DatabaseManager

def get_sql_analyst_tools(db ,model):
        """
        Factory method to generate SQL tools for an agent.
        Ensures tools are always linked to the singleton DB instance.
        """

        # Initialize the standard SQL toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        
        # Returns the list of standard tools: 
        # sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker
        return toolkit.get_tools()
