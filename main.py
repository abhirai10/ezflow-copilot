from fastapi import FastAPI
from src.backend.api.v1.api import api_router
from src.backend.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Include all V1 routes
app.include_router(api_router, prefix="/api/v1")

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the 2026 API"}
