from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EZFLOW Copilot"
    model_api_key: SecretStr 
    azure_sql_connection_string: str
    
    class Config:
        env_file = ".env"

settings = Settings()
