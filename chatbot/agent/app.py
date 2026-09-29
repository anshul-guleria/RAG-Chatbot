'''Testing agent in CLI'''

from graph import app
import uuid
from state import AgentState

CONFIG = {
    "configurable": {"thread_id": str(uuid.uuid4())}
}

if __name__ == "__main__":
    while True:
        print(f"config: {CONFIG}")
        question = input("> User: ")
        response = app.invoke(
            {
                "question": question
            },
            config=CONFIG
        )
        # history=response["history"]
        print("AI:", response["answer"])