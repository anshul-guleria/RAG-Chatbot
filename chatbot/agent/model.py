from typing import Literal, Optional
from pydantic import BaseModel, Field

class QueryRouter(BaseModel):
    retrieve: bool = Field(
        description="Whether the knowledge base should be searched."
    )

    rag_query: Optional[str] = Field(
        default=None,
        description=(
            "A standalone, retrieval-optimized query. "
            "Rewrite the user's question using conversation context. "
            "Only provide this when retrieve=True."
        )
    )