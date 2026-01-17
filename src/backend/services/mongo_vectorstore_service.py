from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from src.backend.core.config import settings


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


async def get_document_context(submission_id,query):
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5, 
            "score_threshold": 0.8, 
            "pre_filter": {"SubmissionID": {"$eq": submission_id}}
            })
    
    try:
        docs = await retriever.ainvoke(query)
        return docs
    except Exception as e:
        print(f"Error during vector search: {e}")
        return []

