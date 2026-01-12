from langchain.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from src.backend.core.config import settings
#from langchain.embeddings import init_embeddings

client = MongoClient(settings.mongodb_atlas_cluster_uri)
db_name = "underwriting_accelerator_db"
collection_name = "underwriting_accelerator_vectorstores"
collection = client[db_name][collection_name]
index_name = "underwriting_accelerator-index-vectorstores"

#embeddings=init_embeddings("models/gemini-embedding-001", provider="google_genai", api_key=settings.google_api_key)
model="models/gemini-embedding-001"
embeddings = GoogleGenerativeAIEmbeddings(model=model, api_key=settings.google_api_key)

vector_store=MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=index_name,
            relevance_score_fn="cosine",
        )

@tool(response_format="content_and_artifact")
def retrieve_context_tool(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs