from fastapi import APIRouter
from src.backend.ai.agents.doc_agent import doc_analyst_agent
from src.backend.schemas.user import ChatRequest
from src.backend.services.mongo_vectorstore_service import get_document_context


router = APIRouter()

@router.post("/chat", response_model=str)
async def register_user(data: ChatRequest):
    user_query = data.question
    response = await doc_analyst_agent.get_response(user_query, data.user_id)

    return response

@router.post("/test")
async def register_user(data: ChatRequest):
    user_query = data.question
    response = await get_document_context("5EF63283-BCD9-4D33-8044-4AA8551025DC",user_query)

    return response


