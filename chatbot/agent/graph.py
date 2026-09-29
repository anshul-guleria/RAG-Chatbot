from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from state import AgentState
from nodes import generate

graph = StateGraph(AgentState)

graph.add_node("generate", generate)

graph.add_edge(START, "generate")
graph.add_edge("generate", END)

# Conversation state persistence
checkpointer = InMemorySaver()

app = graph.compile(
    checkpointer=checkpointer
)