import os
import sys
from pathlib import Path
import uuid
from flask import Flask, render_template, request, jsonify

# Ensure the root project directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from chatbot.agent.graph import app as agent_app

UI_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = UI_DIR / "templates"
STATIC_DIR = UI_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR)
)


def is_production() -> bool:
    """Check if app is running in production mode."""
    prod_env = os.environ.get("PROD", "").lower() in ("true", "1", "yes")
    env_mode = os.environ.get("ENV", "").lower() in ("production", "prod")
    return prod_env or env_mode


@app.route("/")
def index():
    return render_template("index.html", is_prod=is_production())


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        question = data.get("message", "").strip()
        thread_id = data.get("thread_id") or str(uuid.uuid4())

        if not question:
            return jsonify({"error": "Message cannot be empty"}), 400

        config = {
            "configurable": {"thread_id": thread_id}
        }

        # Invoke the LangGraph agent
        response = agent_app.invoke(
            {"question": question},
            config=config
        )

        answer = response.get("answer", "No answer generated.")
        retrieve_triggered = bool(response.get("retrieve", False))
        rag_query = response.get("rag_query")

        # Format retrieved chunks
        raw_context = response.get("context", []) or []
        retrieved_chunks = []

        for item in raw_context:
            doc = item.get("doc") if isinstance(item, dict) else None
            score = item.get("score") if isinstance(item, dict) else None

            if doc is not None:
                metadata = getattr(doc, "metadata", {})
                page_content = getattr(doc, "page_content", "")
                page_label = metadata.get("page_label", metadata.get("page", "N/A"))
                source = metadata.get("source", metadata.get("file_name", "Document"))

                retrieved_chunks.append({
                    "content": page_content,
                    "metadata": metadata,
                    "page_label": page_label,
                    "source": source,
                    "score": round(float(score), 4) if score is not None else None
                })

        return jsonify({
            "thread_id": thread_id,
            "answer": answer,
            "retrieve": retrieve_triggered,
            "rag_query": rag_query,
            "chunks": retrieved_chunks,
            "chunks_count": len(retrieved_chunks)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/api/new-thread", methods=["POST"])
def new_thread():
    return jsonify({
        "thread_id": str(uuid.uuid4())
    })


@app.route("/api/ingest", methods=["POST"])
def ingest():
    if is_production():
        return jsonify({"error": "Ingestion is disabled in production mode. Utilizing existing vector data."}), 403

    try:
        from chatbot.rag.ingestion import load_and_chunk_pdf, embed_and_store_chunks
        chunks = load_and_chunk_pdf()
        embed_and_store_chunks(chunks)
        return jsonify({"message": f"Ingestion complete! {len(chunks)} chunks indexed."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1")
    print(f"Starting Flask RAG UI at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
