'''Create LLM Client - Using Gemini and Groq'''
import os
from dotenv import load_dotenv
load_dotenv()

gemini_model=os.getenv("GEMINI_MODEL", "gemini...")
groq_model=os.getenv("GROQ_MODEL", "gpt...")

def create_llm(provider: str, temperature: float = 0.0):
    
    if provider=='google' or provider=='gemini':
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm=ChatGoogleGenerativeAI(model=gemini_model,
                                       temperature=temperature)

        except Exception as e:
            print(f"Error: {e}")

    elif provider=='groq':
        try: 
            from langchain_groq import ChatGroq

            llm=ChatGroq(model=groq_model,
                         temperature=temperature)

        except Exception as e:
                    print(f"Error: {e}")

    return llm