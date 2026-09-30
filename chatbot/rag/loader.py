from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import json

def load_with_pypdf(pdf_path: Path):
    loader = PyPDFLoader(pdf_path)

    print("Started extracting pdf...")
    documents = loader.load()

    print(f"Number of pages extracted: {len(documents)}")

    documents=[document for document in documents if len(document.page_content)>10]

    return documents


def save_data_to_json(documents, output_path: Path):
    data = [
        {
            "page_content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]
    
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Number of pages saved: {len(documents)}")

# documents=load_with_pypdf(r"C:\Users\anshu\Desktop\RAG-Chatbot\dataset\Ebook-Agentic-AI.pdf")
# save_data_to_json(documents, r"C:\Users\anshu\Desktop\RAG-Chatbot\outputs\test.json")