from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from chatbot.agent.state import AgentState
from chatbot.agent.nodes import generate_answer, retrievel, route_query, retrieval_router

graph = StateGraph(AgentState)

graph.add_node("query_router", route_query)
graph.add_node("generate", generate_answer)
graph.add_node("retrievel", retrievel)

graph.add_edge(START, "query_router")
graph.add_conditional_edges("query_router", retrieval_router, {
    "retrievel": 'retrievel',
    "generate": "generate"
})
graph.add_edge("retrievel", "generate")
graph.add_edge("generate", END)

# Conversation state persistence
checkpointer = InMemorySaver()

app = graph.compile(
    checkpointer=checkpointer
)