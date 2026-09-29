from typing import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    question: str
    history: list[BaseMessage]
    answer: str