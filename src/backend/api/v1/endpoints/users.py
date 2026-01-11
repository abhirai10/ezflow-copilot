from fastapi import APIRouter, Request
#from src.backend.api.limiter import limiter


router = APIRouter()

@router.post("/", response_model=str)
def register_user(request: Request):
    return "Hello From Fastapi"
