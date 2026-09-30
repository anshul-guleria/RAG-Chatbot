import os
import time
from dotenv import load_dotenv
import psycopg
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from chatbot.rag.embedding import get_embedding_model
from langchain_qdrant import QdrantVectorStore
from langchain_postgres import PGVector

load_dotenv()

VECTOR_STORE = os.getenv("VECTOR_STORE", "qdrant")
COLLECTION_NAME = "document_chunks"

documents_embedding_model=get_embedding_model()

def get_qdrant_client():
    return QdrantClient(
        path=os.getenv(
            "QDRANT_PATH",
            "./qdrant_data"
        )
    )

def get_qdrant_store():
    client = get_qdrant_client()

    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
            size=768,               
            distance=Distance.COSINE
        )
    )
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=documents_embedding_model
    )

def get_pgvector_store():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB","postgres")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")

    connection = (
        f"postgresql+psycopg://"
        f"{user}:{password}@{host}:{port}/{db}"
    )

    return PGVector(
        embeddings=documents_embedding_model,
        collection_name=COLLECTION_NAME,
        connection=connection,
        use_jsonb=True,
    )


def get_vector_store():
    if VECTOR_STORE == "qdrant":
        return get_qdrant_store()
    if VECTOR_STORE == "pgvector":
        return get_pgvector_store()

    raise ValueError(
        f"Invalid VECTOR_STORE: {VECTOR_STORE}"
    )

def add_documents(chunks):
    vector_store = get_vector_store()

    batch_size=90
    for i in range(0, len(chunks), batch_size):
        vector_store.add_documents(chunks[i:i+batch_size])
        count=len(chunks[i:i+batch_size])
        print("Ingested", count, "chunks...")
        if count<batch_size:
            print("Ingestion completed...")
            break
        else:
            if os.getenv("EMDEDDING_PROVIDER")=='gemini':
                print("Waiting ~60s for rate limit cooldown....")
                time.sleep(61)
    return vector_store