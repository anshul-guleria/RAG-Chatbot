# Agentic RAG Chatbot

An intelligent Retrieval-Augmented Generation (RAG) assistant with conversational memory, dynamic query routing, and multi-provider support.

> **Note**: The core chatbot architecture, graph nodes, query router, vector store integrations, and ingestion pipeline were built from scratch using the official LangChain and LangGraph documentation. The Flask web interface was created with the help of AI.

---

## Overview and How It Works

Instead of querying the vector database on every single message (like simple greetings or casual conversation), this chatbot uses a LangGraph agent workflow:

```
[User Question]
       │
       ▼
┌──────────────────┐
│   Query Router   │ ──(retrieve = false)──► [Direct Answer Generation] ──► End
└──────────────────┘
       │
  (retrieve = true)
       ▼
┌──────────────────┐
│ Rewrite Query &  │
│ Vector Retrieval │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Grounded Answer  │ ──► End
│   Generation     │
└──────────────────┘
```

### Key Workflow Features:
1. **Smart Query Router**: 
   - Uses structured outputs to decide if a query actually requires document retrieval (`retrieve: true/false`).
   - Resolves pronouns and context from conversation history (e.g., rewriting *"tell me more about that"* into *"What is an orchestrator in a multi-agent system?"*).
2. **Context-Grounded Answers**:
   - Only uses retrieved source chunks as ground truth to prevent hallucinations.
3. **Conversational Memory**:
   - Powered by LangGraph's `InMemorySaver` checkpointer using per-session thread IDs.
4. **Flexible LLM & Vector Store Backends**:
   - **LLM Providers**: Google Gemini (`gemini-2.5-flash`) or Groq (`llama-3.3-70b-versatile`).
   - **Vector Stores**: **Qdrant** (local disk/embedded) and **PostgreSQL** (`pgvector`).

## Installation and Setup with UV

This project uses `uv` for fast dependency management.

### 1. Create and Activate Virtual Environment
```bash
# Create a virtual environment
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install all locked dependencies from uv.lock
uv sync
```

Alternatively, you can run any project command directly with `uv run` without manually activating the virtual environment:
```bash
uv run python -m chatbot.ui.app
```

---

## Environment Configuration

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

### Sample `.env` Setup:

```env
# Model Provider ('google' or 'groq')
MODEL_PROVIDER=google

# Google Gemini API Settings
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Groq API Settings (if using MODEL_PROVIDER=groq)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Vector Store Selection ('qdrant' or 'pgvector')
VECTOR_STORE=qdrant
QDRANT_PATH=./qdrant_data

# PostgreSQL / PGVector (Only needed if VECTOR_STORE=pgvector)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

PORT=5000
```

---

## Document Ingestion

The ingestion pipeline loads PDFs placed in the `dataset/` directory, chunks them with `RecursiveCharacterTextSplitter`, generates vector embeddings, and stores them in your vector database.

### How to Ingest:
- **Via Web UI**: Open the UI and click the **"Ingest Docs"** button in the top navigation bar.
- **Via CLI**: Run the ingestion script directly:
  ```bash
  python -m chatbot.rag.ingestion
  ```

### Ingestion Duration:
- Embeddings are sent in batches of up to 90 chunks.
- To stay within free-tier rate limits for embedding APIs, the script waits ~60 seconds between batches.
- A typical document (~100–200 chunks) takes around **2 to 3 minutes** to ingest.
- Once ingested, vectors are stored permanently (in `./qdrant_data` or Postgres) and subsequent searches are instant.
- During ingestion, the qdrant will get locked so cant chat for that duration (~3 minutes)

---

## 3 Ways to Run the Project

### 1. Terminal / CLI Mode
Run the conversational agent directly in your command line:

```bash
python -m chatbot.agent.app
```

---

### 2. Interactive Web UI (Flask)
Start the local web interface to chat with the assistant and inspect retrieved document chunks and similarity scores:

```bash
python -m chatbot.ui.app
```

Then visit **http://127.0.0.1:5000** in your browser.

---

### 3. Docker and Docker Compose (One-Click Deployment)
Run both the application and the database in isolated containers:

```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f

# Stop containers
docker compose down
```

Access the UI at **http://localhost:5000**.
