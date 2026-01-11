from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from src.backend.api.v1.api import api_router
from src.backend.core.config import settings
from src.backend.api.limiter import limiter

app = FastAPI(title=settings.PROJECT_NAME)

# Link limiter to app state and register error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Include all V1 routes
app.include_router(api_router, prefix="/api/v1")
