from fastapi import APIRouter
from src.backend.schemas.user import ChatRequest


router = APIRouter()

@router.post("/create", response_model=str)
async def register_user(data: ChatRequest):
    user_query = data.question
    response = await doc_analyst_agent.get_response(user_query, data.user_id)

    return response



