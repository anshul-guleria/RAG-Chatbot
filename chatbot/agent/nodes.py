'''All the nodes funtion for the graph'''
from state import AgentState
from llm import create_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from rich import print as rich_print

llm=create_llm(temperature=0.5)
parser=StrOutputParser()

chat_llm=(llm | parser)

SYSTEM_PROMPT = """
    You are a helpful AI assistant.
"""


def generate(state: AgentState):

    messages=[
        SystemMessage(content=f"{SYSTEM_PROMPT}"),
        *state["history"],
        HumanMessage(content=state["question"])
    ]

    rich_print("Messages sent to LLM:\n",messages)
    
    response=chat_llm.invoke(
        messages
    )

    return {
        "history": state["history"] + [HumanMessage(content=state["question"]), AIMessage(content=response)],
        "answer": response
    }
