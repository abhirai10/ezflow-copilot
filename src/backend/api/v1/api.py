from fastapi import APIRouter
from src.backend.api.v1.endpoints import users # Import individual endpoint modules

api_router = APIRouter()

# Register individual routers with their specific prefixes and tags
api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(items.router, prefix="/items", tags=["Items"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
