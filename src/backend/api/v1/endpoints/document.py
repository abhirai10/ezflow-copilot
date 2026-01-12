from fastapi import APIRouter
from src.backend.ai.agents.sql_agent import sql_analyst_agent
from src.backend.ai.agents.doc_agent import doc_analyst_agent
from src.backend.schemas.user import ChatRequest


router = APIRouter()

@router.post("/chat", response_model=str)
async def register_user(data: ChatRequest):
    user_query = data.question
    response = await doc_analyst_agent.get_response(user_query, data.user_id)

    return response



