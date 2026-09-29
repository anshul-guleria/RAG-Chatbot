from graph import app
import uuid
from state import AgentState

CONFIG = {
    "configurable": {"thread_id": str(uuid.uuid4())}
}

print(f"config: {CONFIG}")

if __name__ == "__main__":

    history=[]

    while True:

        question = input("> User: ")

        response = app.invoke(
            {
                "question": question,
                "history":history,
                "answer":""
            },
            config=CONFIG
        )
        history=response["history"]
        print("AI:", response["answer"])