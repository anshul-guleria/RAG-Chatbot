from llm import create_llm
import os
from dotenv import load_dotenv
load_dotenv()

from rich import print as rich_print

model_provider=os.getenv("MODEL_PROVIDER","")

if __name__=='__main__':

    llm=create_llm(model_provider, temperature=0.7)

    while True:
        query=input("> User: ")

        response=llm.invoke(query)

        # rich_print(response)

        print(f"Assistant: {response.content}\n\n")
        