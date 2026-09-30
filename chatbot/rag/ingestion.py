'''Ingestion service: load, chunk, embed and store'''

from loader import load_with_pypdf, save_data_to_json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_store import add_documents

FILE_PATH=r"C:\Users\anshu\Desktop\RAG-Chatbot\dataset\Ebook-Agentic-AI.pdf"

def load_and_chunk_pdf(file_path=FILE_PATH,
             chunk_size=500,
             overlap=50):
    
    documents = load_with_pypdf(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(documents)

    print(f"Chunks generated: {len(chunks)}")
    return chunks

def embed_and_store_chunks(chunks):
    try:
        store=add_documents(chunks)
        print("Documents ingested successfully.")
    except Exception as e:
        print(f"Error: {e}")
    
    return store


def main():
    chunks=load_and_chunk_pdf()
    vector_store=embed_and_store_chunks(chunks)

main()