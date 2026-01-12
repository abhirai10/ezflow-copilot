from fastapi import APIRouter
from src.backend.api.v1.endpoints import database, document # Import individual endpoint modules

api_router = APIRouter()

# Register individual routers with their specific prefixes and tags
api_router.include_router(database.router, prefix="/database", tags=["Database"])
api_router.include_router(document.router, prefix="/document", tags=["Document"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
