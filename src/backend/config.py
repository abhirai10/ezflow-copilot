import os

class Config:
    """Central configuration for the application."""
    AZURE_SQL_URL = os.getenv("AZURE_SQL_CONNECTION_STRING")
    AZURE_STORAGE_URL = os.getenv("AZURE_STORAGE_URL")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER")
    LLM_MODEL = os.getenv("LLM_MODEL")
    
    # Validation to catch errors early
    @classmethod
    def validate(cls):
        if not cls.AZURE_SQL_URL:
            raise ValueError("AZURE_SQL_CONNECTION_STRING is missing from .env")