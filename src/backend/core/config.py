from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI 2026 Project"
    DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
