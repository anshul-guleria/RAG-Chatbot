import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()

EMBEDDING_MODEL=os.getenv("GEMINI_EMBEDDING_MODEL")

query_embedding_model=GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    task_type="RETRIEVAL_QUERY",
    output_dimensionality=768
    )

documents_embedding_model=GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    task_type="RETRIEVAL_DOCUMENT",
    output_dimensionality=768
    )

def embed_query(query):
    """Embeds a query"""
    return query_embedding_model.embed_query(query)

def embed_documents(documents):
    """Embeds a list of documents"""
    return documents_embedding_model.embed_documents(documents)