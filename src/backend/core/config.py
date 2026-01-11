from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EZFLOW Copilot"
    model_api_key: SecretStr = Field(..., alias="MODEL_API_KEY")
    azure_sql_connection_string: str = Field(..., alias="AZURE_SQL_CONNECTION_STRING")
    langsmith_tracing: str = Field(default="true", alias="LANGSMITH_TRACING")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langsmith_api_key: SecretStr = Field(default="", alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="", alias="LANGSMITH_PROJECT")
    
    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()
