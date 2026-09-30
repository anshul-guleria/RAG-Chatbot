'''All the nodes funtion for the graph'''
from chatbot.agent.state import AgentState
from chatbot.agent.llm import create_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from chatbot.rag.retrieval import retrieve_with_scores
from chatbot.agent.model import QueryRouter
from rich import print as rich_print

llm=create_llm(temperature=0.5)
parser=StrOutputParser()

chat_llm=(llm | parser)

def retrieval_router(state: AgentState) -> str:

    if state.get("retrieve", False):
        return "retrievel"

    return "generate"

def route_query(state: AgentState):
    ROUTER_PROMPT = """
    You are a query router for a RAG chatbot.

    Your job is to:
    1. Decide whether the user's current message requires searching the
    knowledge base.
    2. If retrieval is required, rewrite the user's question into a
    standalone, retrieval-optimized query.

    Rules:

    RETRIEVE = true when:
    - The user asks a factual question that may require knowledge-base information.
    - The user asks about a document, topic, concept, or information that may exist
    in the knowledge base.
    - The user asks a follow-up question that requires information from the
    knowledge base.
    - Resolve references such as "this", "that", "it", "the above", etc. using
    conversation history.

    RETRIEVE = false when:
    - The user says hello, hi, hey, etc.
    - The user says ok, thanks, thank you, bye, etc.
    - The user is making casual conversation.
    - No knowledge-base information is needed.

    For retrieval:
    - Rewrite the question as a standalone search query.
    - Include important entities, concepts, and constraints from the conversation.
    - Remove conversational filler.
    - Do not answer the question.
    - Do not add facts that aren't present in the user's question or conversation.
    - Keep the query concise.

    Examples:

    User: "what is multi agent system?"
    => retrieve=true
    => rag_query="What is a multi-agent system?"

    User: "what's this?"
    Previous conversation: "What are multi-agent systems?"
    => retrieve=true
    => rag_query="What are multi-agent systems?"

    User: "tell me more about that"
    Previous conversation: "What is an orchestrator in a multi-agent system?"
    => retrieve=true
    => rag_query="What is an orchestrator in a multi-agent system?"

    User: "ok"
    => retrieve=false
    => rag_query=null

    User: "thanks"
    => retrieve=false
    => rag_query=null
    """
    history = state.get("history", [])
    question = state["question"]

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        *history,
        HumanMessage(content=question),
    ]
    routerllm=create_llm(temperature=0)
    structured_llm = routerllm.with_structured_output(QueryRouter)

    try:
        result: QueryRouter = structured_llm.invoke(messages)
    except Exception:
        return {"retrieve": False, "rag_query": None}

    return {
        "retrieve": result.retrieve,
        "rag_query": result.rag_query,
    }

def generate_answer(state: AgentState):

    SYSTEM_PROMPT = """
    You are a helpful AI assistant that answers questions using the provided context.
    * Use the context as the source of truth for factual answers.
    * The context is retrieved and prepended to user actual question.
    * If user query is generic or ambiguos to the context ask for clarification.
    * Do not rely on outside knowledge or invent information.
    * If the answer cannot be found in the context, say that you don't have enough information to answer.
    * Use conversation history to understand the user's question and follow-ups.
    * Give clear, concise, and relevant answers.
    """
    history=state.get("history",[])
    raw_context=state.get("context",[])
    retrievel=state.get("retrieve", False)

    if raw_context!=[]:
        context = "\n\n".join(
            f"Source {i + 1}:\n{item['doc'].page_content}[Page: {item['doc'].metadata["page_label"]}]"
            for i, item in enumerate(raw_context)
        )
        context=f"""\nRetrieved reference documents:\n<context>\n{context}</context>\n\nUse these documents only as reference material for answering the user's
                question."""
    else:
        context=""

    messages=[
        SystemMessage(content=f"{SYSTEM_PROMPT}\n\nHeres the context: {context}"),
        *history,
        HumanMessage(content=f"""User question: {state["question"]}""")
    ]

    rich_print("Messages sent to LLM:\n",messages)
    if retrievel:
        print("RAG Query:", state["rag_query"])
    response=chat_llm.invoke(
        messages
    )

    return {
        "history": history + [HumanMessage(content=state["question"]), AIMessage(content=response)],
        "answer": response
    }


def retrievel(state: AgentState):
    rag_query=state["rag_query"] if state.get("rag_query", None) is not None else state["question"]

    results=retrieve_with_scores(rag_query)

    return {
        "context": [{"doc":doc,
                     "score":score} for doc, score in results]
    }    


