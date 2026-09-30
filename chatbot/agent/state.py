from typing import TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class RetrievedDoc(TypedDict):
    doc: Document
    score: float

class AgentState(TypedDict, total=False):
    question: str
    rag_query: str 
    retrieve: bool
    history: list[BaseMessage]
    context: list[RetrievedDoc]
    answer: str