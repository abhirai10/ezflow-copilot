from fastapi import APIRouter
from src.backend.ai.agents.analyst.agent import shared_agent
from src.backend.schemas.user import ChatRequest


router = APIRouter()

@router.post("/chat", response_model=str)
async def register_user(data: ChatRequest):
    user_query = data.question

    response = await shared_agent.get_response(user_query)

    return response


