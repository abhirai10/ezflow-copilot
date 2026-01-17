from langchain.tools import tool
from pydantic import Field
from src.backend.services.mongo_vectorstore_service import get_document_context

@tool
async def retrieve_context_tool(
    submission_id: str = Field(..., description="The unique identifier of the submission to retrieve context for"),
    query: str = Field(..., description="The search query describing what information you need (e.g., 'policy coverage details', 'broker information')")
):
    """
    Retrieve relevant documents and context from the vector store for a given submission.
    
    Use this tool to fetch documents, policies, or contextual information related to a submission
    based on semantic similarity to your query. This is essential for providing accurate answers
    about submission details, document contents, and policy information.
    
    Returns:
        Retrieved context/documents from the vector store that match the query
    """
    return await get_document_context("5EF63283-BCD9-4D33-8044-4AA8551025DC", query)

# To Do