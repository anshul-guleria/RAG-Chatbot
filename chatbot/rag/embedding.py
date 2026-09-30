import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

EMBEDDING_PROVIDER=os.getenv("EMBDEDDING_PROVIDER")
GEMINI_EMBEDDING_MODEL=os.getenv("GEMINI_EMBEDDING_MODEL")
HUGGINGFACE_EMBEDDING_MODEL=os.getenv("HUGGINGFACE_EMBEDDING_MODEL")

def get_embedding_model(provider: str = EMBEDDING_PROVIDER):

    if provider=='huggingface':
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": False}

        documents_embedding_model=HuggingFaceEmbeddings(
        model_name=HUGGINGFACE_EMBEDDING_MODEL,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
        )

    elif provider=='gemini':
        documents_embedding_model=GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768
        )

    return documents_embedding_model

def embed_documents(documents):
    """Embeds a list of documents"""
    return get_embedding_model().embed_documents(documents)