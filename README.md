# Document RAG Backend

A **Retrieval-Augmented Generation (RAG)** backend built with **FastAPI**, **Qdrant**, **Redis**, and **Groq LLM**. This system provides two core REST APIs: one for document ingestion with selectable chunking strategies, and one for conversational multi-turn question answering with built-in interview booking support.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Modules Explained](#core-modules-explained)
   - [Document Ingestion API](#1-document-ingestion-api)
   - [Conversational RAG API](#2-conversational-rag-api)
   - [Chunking Strategies](#3-chunking-strategies)
   - [Embedding Provider](#4-embedding-provider)
   - [Vector Store (Qdrant)](#5-vector-store-qdrant)
   - [Redis Chat Memory](#6-redis-chat-memory)
   - [LLM Provider (Groq)](#7-llm-provider-groq)
   - [Interview Booking](#8-interview-booking)
   - [Prompt Builder](#9-prompt-builder)
   - [Database Models](#10-database-models)
6. [API Reference](#api-reference)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Setup & Installation](#setup--installation)
9. [Environment Variables](#environment-variables)
10. [Running the Server](#running-the-server)
11. [Running Tests](#running-tests)
12. [Design Decisions](#design-decisions)

---

## Project Overview

This backend was built as a technical assignment for **Palm Mind AI**. The goal was to implement a custom RAG pipeline from scratch — **without** using high-level abstractions like `RetrievalQAChain`, FAISS, or Chroma — following clean, modular, industry-standard Python architecture.

### What It Does

| Feature | Detail |
|---|---|
| Document Upload | Accepts `.pdf` and `.txt` files |
| Text Extraction | Uses **PyMuPDF** for PDF, native UTF-8 for TXT |
| Chunking | Two strategies: **Fixed-size with overlap** and **Sentence-based** |
| Embeddings | Generated using **BAAI/bge-small-en-v1.5** via `sentence-transformers` |
| Vector Storage | Stored in **Qdrant** (not FAISS/Chroma) |
| Metadata Storage | Saved in **SQLite** via SQLAlchemy ORM |
| Chat Memory | Multi-turn history stored per-session in **Redis** |
| LLM | **Groq API** with `llama-3.3-70b-versatile` model |
| Interview Booking | Detected from natural language and extracted via LLM |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                     FastAPI App                       │
│                                                      │
│  ┌─────────────┐          ┌──────────────────────┐   │
│  │ POST /upload│          │    POST /chat         │   │
│  └──────┬──────┘          └──────────┬───────────┘   │
│         │                            │               │
│         ▼                            ▼               │
│  ┌─────────────┐          ┌──────────────────────┐   │
│  │UploadService│          │     ChatService       │   │
│  └──────┬──────┘          └──────────┬───────────┘   │
│         │                            │               │
│  ┌──────┴──────┐          ┌──────────┴───────────┐   │
│  │  Parser     │          │  BookingService       │   │
│  │  Chunker    │          │  Retriever            │   │
│  │  Embedder   │          │  PromptBuilder        │   │
│  │  VectorStore│          │  LLMProvider          │   │
│  │  SQL DB     │          │  RedisMemory          │   │
│  └─────────────┘          └──────────────────────┘   │
└──────────────────────────────────────────────────────┘
        │                            │
        ▼                            ▼
  ┌──────────┐              ┌─────────────────┐
  │  Qdrant  │              │  Redis          │
  │ (Vectors)│              │ (Chat History)  │
  └──────────┘              └─────────────────┘
        │
        ▼
  ┌──────────┐
  │  SQLite  │
  │(Metadata)│
  └──────────┘
```

The application follows a **layered architecture**:
- **API Layer** → handles HTTP requests/responses
- **Service Layer** → contains all business logic
- **Provider Layer** → wraps external integrations (Redis, Qdrant, Groq)
- **Repository Layer** → handles database persistence
- **Schema Layer** → Pydantic models for validation

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Web Framework | **FastAPI** | Async REST API with automatic OpenAPI docs |
| LLM | **Groq API** (llama-3.3-70b-versatile) | Chat generation & booking extraction |
| Embeddings | **sentence-transformers** (BAAI/bge-small-en-v1.5) | Dense vector generation |
| Vector DB | **Qdrant** | Semantic search over document chunks |
| Chat Memory | **Redis** | Per-session conversation history |
| SQL Database | **SQLite + SQLAlchemy** | Document & booking metadata persistence |
| PDF Parsing | **PyMuPDF (fitz)** | Text extraction from PDF pages |
| Validation | **Pydantic v2** | Request/response schema validation |
| Config | **pydantic-settings** | Type-safe environment variable loading |
| Testing | **pytest** | Unit tests for all services |
| Logging | **loguru** | Structured application logging |

---

## Project Structure

```
document-rag-backend/
│
├── app/
│   ├── main.py                    # FastAPI app, lifespan startup/shutdown
│   │
│   ├── api/                       # HTTP route handlers
│   │   ├── upload.py              # POST /upload
│   │   ├── chat.py                # POST /chat
│   │   ├── document.py            # GET /documents
│   │   ├── health.py              # GET /health
│   │   └── dependencies.py        # FastAPI dependency injection wiring
│   │
│   ├── services/                  # Core business logic
│   │   ├── upload.py              # Document ingestion orchestration
│   │   ├── chat.py                # RAG chat orchestration
│   │   ├── parser.py              # PDF/TXT text extraction
│   │   ├── chunker.py             # Fixed & sentence chunking strategies
│   │   ├── retriever.py           # Embedding query + Qdrant search
│   │   ├── prompt_builder.py      # Prompt assembly with history & context
│   │   ├── booking.py             # LLM-powered interview booking
│   │   └── embedding.py           # (utility)
│   │
│   ├── providers/                 # External service wrappers
│   │   ├── embedding_provider.py  # sentence-transformers wrapper
│   │   ├── vector_store.py        # Qdrant client wrapper
│   │   ├── redis_memory.py        # Redis conversation history wrapper
│   │   └── llm.py                 # Groq API wrapper
│   │
│   ├── repositories/              # Database access layer
│   │   └── booking_repository.py  # Booking CRUD operations
│   │
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── upload.py              # UploadResponse schema
│   │   ├── chat.py                # ChatRequest, ChatResponse, Source schemas
│   │   ├── booking.py             # BookingExtraction, BookingResponse schemas
│   │   ├── document.py            # Document schema
│   │   └── common.py              # Shared schemas
│   │
│   ├── db/                        # Database configuration
│   │   ├── database.py            # SQLAlchemy engine & SessionLocal
│   │   ├── models.py              # ORM models (Document, ChunkMetadata, Booking)
│   │   └── crud.py                # Generic CRUD helpers
│   │
│   ├── config/
│   │   ├── settings.py            # pydantic-settings config loader
│   │   └── logging.py             # Logging setup
│   │
│   └── utils/
│       ├── constants.py
│       ├── helpers.py
│       └── validators.py
│
├── tests/                         # Pytest test suite
│   ├── test_upload_service.py
│   ├── test_chat_service.py
│   ├── test_chunker.py
│   ├── test_parser.py
│   ├── test_retriever.py
│   ├── test_embedding.py
│   ├── test_vector_store.py
│   ├── test_memory.py
│   ├── test_booking.py
│   ├── test_prompt_builder.py
│   ├── test_chat_memory.py
│   ├── test_groq.py
│   └── test_settings.py
│
├── .env                           # Local secrets (not committed)
├── .env.example                   # Template for environment variables
├── requirements.txt               # Python dependencies
├── document_rag.db                # SQLite database file (auto-created)
└── README.md
```

---

## Core Modules Explained

### 1. Document Ingestion API

**Endpoint:** `POST /upload/`  
**File:** `app/api/upload.py` → `app/services/upload.py`

This endpoint accepts a file upload along with a chosen chunking strategy. Internally, the `UploadService` class orchestrates the full ingestion pipeline:

**Step-by-step flow:**

```
Upload Request
     │
     ▼
1. Validate file type (.pdf or .txt only)
     │
     ▼
2. Save file to a temporary path
     │
     ▼
3. DocumentParser.parse(file_path)
   → PDF: iterate pages via PyMuPDF, join text
   → TXT: read UTF-8 content
     │
     ▼
4. TextChunker.chunk(text, strategy)
   → "fixed":    overlapping fixed-size windows
   → "sentence": split on sentence boundaries
     │
     ▼
5. EmbeddingProvider.encode(chunks)
   → BAAI/bge-small-en-v1.5 generates 384-dim vectors
     │
     ▼
6. VectorStore.upsert(embeddings, payloads)
   → Stored in Qdrant with document_id, chunk_number, text payload
     │
     ▼
7. SQLAlchemy: save Document row + ChunkMetadata rows
     │
     ▼
8. Return UploadResponse (document_id, chunks, vectors count)
```

**Request (multipart/form-data):**
```
file:           <binary file>
chunk_strategy: "fixed" | "sentence"   (default: "fixed")
```

**Response:**
```json
{
  "document_id": 1,
  "filename": "report.pdf",
  "filetype": ".pdf",
  "chunk_strategy": "fixed",
  "chunks": 42,
  "vectors": 42
}
```

---

### 2. Conversational RAG API

**Endpoint:** `POST /chat`  
**File:** `app/api/chat.py` → `app/services/chat.py`

The `ChatService` handles both normal RAG queries and interview booking requests within the same endpoint. It uses a **session_id** to maintain independent conversation memory per user.

**Step-by-step flow:**

```
Chat Request (session_id, question, top_k)
     │
     ▼
1. Load conversation history from Redis (by session_id)
     │
     ▼
2. BookingService.process(question)
   → Send question to Groq LLM with extraction prompt
   → LLM returns JSON: { is_booking, name, email, date, time }
     │
     ├── is_booking = True → Save booking to SQLite → Return confirmation
     │
     └── is_booking = False
           │
           ▼
3. Retriever.retrieve(question, top_k)
   → Embed question with same model
   → Qdrant cosine search → top_k relevant chunks
           │
           ▼
4. PromptBuilder.build(question, contexts, history)
   → Assembles: system_prompt + history + context + question
           │
           ▼
5. LLMProvider.generate(prompt, model)
   → Groq API call → answer string
           │
           ▼
6. Save user message + assistant answer to Redis
           │
           ▼
7. Return ChatResponse (answer, sources, is_booking, history_size)
```

**Request:**
```json
{
  "session_id": "user-abc-123",
  "question": "What are the main findings in the document?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The main findings include...",
  "sources": [
    {
      "document_id": 1,
      "chunk_number": 3,
      "score": 0.91,
      "text": "The study concluded that..."
    }
  ],
  "is_booking": false,
  "history_size": 4
}
```

---

### 3. Chunking Strategies

**File:** `app/services/chunker.py`

The `TextChunker` class supports two strategies selectable at upload time via the `ChunkStrategy` enum:

#### Strategy 1: Fixed-Size Chunking (`"fixed"`)
Splits text into overlapping windows of a fixed character count.

```
Text: "ABCDEFGHIJ..."
chunk_size = 5, overlap = 2

Chunk 1: "ABCDE"
Chunk 2: "DEFGH"    ← starts 3 chars ahead (5 - 2 = step)
Chunk 3: "GHIJ..."
```

- **Default chunk_size:** 500 characters
- **Default overlap:** 50 characters
- **Use case:** Consistent chunk sizes, good for structured documents

#### Strategy 2: Sentence-Based Chunking (`"sentence"`)
Uses regex to split on sentence boundaries (`.`, `!`, `?` followed by whitespace).

```python
sentences = re.split(r"(?<=[.!?])\s+", text)
```

- **Use case:** Preserves semantic sentence units, better for natural language documents

---

### 4. Embedding Provider

**File:** `app/providers/embedding_provider.py`

Wraps the `sentence-transformers` library to generate dense vector embeddings.

- **Model:** `BAAI/bge-small-en-v1.5`
- **Output dimension:** 384
- **Distance metric used in Qdrant:** Cosine similarity
- The model is loaded **once at startup** via the `lifespan` event and shared across all requests via `app.state.embedding`.

---

### 5. Vector Store (Qdrant)

**File:** `app/providers/vector_store.py`

The `VectorStore` class wraps the official `qdrant-client` and provides:

| Method | Description |
|---|---|
| `_create_collection()` | Creates the Qdrant collection on first run if it doesn't exist |
| `upsert(embeddings, payloads)` | Stores vectors with UUID-based point IDs and metadata payloads |
| `search(query_vector, limit)` | Returns top-k similar points using cosine distance |
| `delete_document(document_id)` | Deletes all vectors associated with a document ID |
| `collection_info()` | Returns current collection statistics |

Each stored point in Qdrant has this payload structure:
```json
{
  "document_id": 1,
  "chunk_number": 3,
  "text": "The actual chunk text..."
}
```

---

### 6. Redis Chat Memory

**File:** `app/providers/redis_memory.py`

The `RedisMemory` class stores conversation history as a **Redis List** keyed by `session_id`. Each message is a JSON-serialized object.

```
Redis Key:   "user-abc-123"
Redis Value: [ {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ... ]
```

| Method | Description |
|---|---|
| `save_message(session_id, role, content)` | Appends a message to the session list (`RPUSH`) |
| `load_history(session_id)` | Fetches full list (`LRANGE 0 -1`) and deserializes |
| `clear_history(session_id)` | Deletes the session key (`DEL`) |
| `ping()` | Health check for Redis connectivity |

This enables true **multi-turn conversations** — each new question is answered in the context of all previous exchanges.

---

### 7. LLM Provider (Groq)

**File:** `app/providers/llm.py`

The `LLMProvider` class wraps the **Groq Python SDK**, which provides extremely fast inference on open-source models.

- **Client:** `groq.Groq` (OpenAI-compatible API)
- **Default model:** `llama-3.3-70b-versatile`
- The LLM is used for **two distinct purposes**:
  1. **Answer generation** in the RAG pipeline
  2. **Structured extraction** for interview booking detection

---

### 8. Interview Booking

**File:** `app/services/booking.py`

The `BookingService` uses the LLM itself to detect and extract interview booking intent from natural language — no keyword matching or rule-based parsing.

**How it works:**

1. Every chat message is sent to the LLM with a special extraction prompt:
   ```
   Determine whether the user's message is requesting an interview booking.
   Return ONLY valid JSON: { "is_booking": true/false, "name": "", "email": "", "date": "", "time": "" }
   ```

2. If `is_booking = true` and all fields are present, the booking is saved to the SQLite `bookings` table via `BookingRepository`.

3. A confirmation message is returned and the booking is also stored in Redis memory so the conversation flow is preserved.

**Example booking message:**
```
"I'd like to book an interview for Sandeep Thapa at sandeep@example.com on 2026-08-10 at 14:00"
```

**Booking table columns:**

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-generated ID |
| `name` | String | Candidate name |
| `email` | String | Candidate email |
| `date` | Date | Interview date (YYYY-MM-DD) |
| `time` | Time | Interview time (HH:MM) |
| `created_at` | DateTime | Record creation timestamp |

---

### 9. Prompt Builder

**File:** `app/services/prompt_builder.py`

The `PromptBuilder` assembles structured prompts from three components:

```
[System Prompt]
You are a helpful AI assistant. Answer using only the provided context...

[Conversation History]
user: What is the company's revenue?
assistant: The company reported $5M in revenue last year.

[Context]
[Document 1 | Chunk 3]
The annual revenue for fiscal year 2025 was...

[Document 1 | Chunk 7]
Revenue growth was primarily driven by...

[Question]
What products contributed most to revenue?
```

This structure gives the LLM full situational awareness: what it already knows from past turns, what the documents say, and the current user question.

---

### 10. Database Models

**File:** `app/db/models.py`

Three SQLAlchemy ORM models are defined:

**`Document`** — tracks uploaded files
```python
id, filename, filetype, chunk_strategy, uploaded_at
```

**`ChunkMetadata`** — links SQL records to Qdrant vector IDs
```python
id, document_id (FK), chunk_number, vector_id (UUID), chunk_size
```

**`Booking`** — stores interview bookings
```python
id, name, email, date, time, created_at
```

The `Document → ChunkMetadata` relationship uses `cascade="all, delete-orphan"`, so deleting a document automatically removes all associated chunk metadata rows.

---

## API Reference

### `GET /`
Health check root endpoint.

**Response:**
```json
{"message": "Document RAG Backend is running"}
```

---

### `GET /health`
Detailed health status of all services.

---

### `POST /upload/`
Upload and ingest a document.

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | file |  | — | `.pdf` or `.txt` file |
| `chunk_strategy` | string |  | `fixed` | `"fixed"` or `"sentence"` |

**Response `200 OK`:**
```json
{
  "document_id": 1,
  "filename": "document.pdf",
  "filetype": ".pdf",
  "chunk_strategy": "fixed",
  "chunks": 35,
  "vectors": 35
}
```

**Error `400`:** If file type is not `.pdf` or `.txt`.

---

### `POST /chat`
Ask a question or book an interview.

**Content-Type:** `application/json`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `session_id` | string | | — | Unique session identifier |
| `question` | string | | — | User's question or booking request |
| `top_k` | integer |  | `5` | Number of chunks to retrieve (1–20) |

**Response `200 OK` (RAG answer):**
```json
{
  "answer": "The document states that...",
  "sources": [
    {"document_id": 1, "chunk_number": 2, "score": 0.88, "text": "..."}
  ],
  "is_booking": false,
  "history_size": 6
}
```

**Response `200 OK` (booking):**
```json
{
  "answer": "Interview booked successfully for John Doe on 2026-08-10 at 14:00.",
  "sources": [],
  "is_booking": true,
  "history_size": 2
}
```

---

### `GET /documents`
List all uploaded documents with metadata.

---

## Data Flow Diagrams

### Document Ingestion Flow

```
User uploads file (PDF/TXT)
         │
         ▼
   FastAPI validates
   file extension
         │
         ▼
  DocumentParser extracts
  raw text from file
         │
         ▼
  TextChunker splits text
  (fixed-size OR sentence)
         │
         ▼
  EmbeddingProvider encodes
  all chunks → 384-dim vectors
         │
      ┌──┴──┐
      │     │
      ▼     ▼
  Qdrant  SQLite
  (vectors) (metadata)
```

### RAG Query Flow

```
User sends question + session_id
         │
         ▼
  Redis: load history
         │
         ▼
  BookingService: detect intent
  (LLM JSON extraction)
         │
    ┌────┴────┐
    │         │
  Booking   RAG
  intent    query
    │         │
    ▼         ▼
  Save      Embed question
  to DB     → Qdrant search
    │         → top_k chunks
    │         │
    │         ▼
    │      PromptBuilder:
    │      assemble prompt
    │         │
    │         ▼
    │      Groq LLM
    │      generates answer
    │         │
    └────┬────┘
         │
         ▼
  Save to Redis memory
         │
         ▼
  Return ChatResponse
```

---

## Setup & Installation

### Prerequisites

Make sure the following are installed and running on your machine:

- Python 3.11+
- **Qdrant** (Docker recommended)
- **Redis** (Docker recommended)
- A valid **Groq API Key** from [console.groq.com](https://console.groq.com)

### 1. Start Qdrant (Docker)

```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### 2. Start Redis (Docker)

```bash
docker run -d -p 6379:6379 redis
```

### 3. Clone & Install

```bash
git clone <your-repo-url>
cd document-rag-backend

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values (see below)
```

---

## Environment Variables

All configuration is loaded from a `.env` file using `pydantic-settings`. Reference the `.env.example` for the full template.

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Document RAG Backend` | Application display name |
| `DEBUG` | `True` | Enable debug mode |
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `DATABASE_URL` | `sqlite:///document_rag.db` | SQLAlchemy DB connection string |
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `QDRANT_HOST` | `localhost` | Qdrant server hostname |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `QDRANT_COLLECTION` | `document_chunks` | Qdrant collection name |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | HuggingFace embedding model name |

**Example `.env`:**
```env
APP_NAME=Document RAG Backend
DEBUG=True

GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=llama-3.3-70b-versatile

DATABASE_URL=sqlite:///document_rag.db

REDIS_HOST=localhost
REDIS_PORT=6379

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=document_chunks

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server starts at: **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

Alternative API docs (ReDoc): **http://localhost:8000/redoc**

---

## Running Tests

```bash
pytest tests/ -v
```

Run a specific test file:
```bash
pytest tests/test_chunker.py -v
pytest tests/test_chat_service.py -v
pytest tests/test_upload_service.py -v
```

### Test Coverage

| Test File | What It Tests |
|---|---|
| `test_chunker.py` | Fixed and sentence chunking strategies |
| `test_parser.py` | PDF and TXT text extraction |
| `test_embedding.py` | Embedding generation shape and type |
| `test_vector_store.py` | Qdrant upsert and search |
| `test_memory.py` | Redis save/load/clear history |
| `test_retriever.py` | End-to-end retrieval from Qdrant |
| `test_prompt_builder.py` | Prompt assembly with history/context |
| `test_booking.py` | LLM-based booking detection |
| `test_chat_service.py` | Full RAG chat pipeline |
| `test_upload_service.py` | Full document ingestion pipeline |
| `test_settings.py` | Environment variable loading |
| `test_groq.py` | Groq API connectivity |
| `test_chat_memory.py` | Redis multi-turn memory |

---

## Design Decisions

### Why Qdrant over FAISS/Chroma?
Qdrant is a production-grade vector database with a client-server architecture, persistent storage, and filtering capabilities. FAISS is an in-memory library and Chroma is a local dev tool — both unsuitable for scalable deployments. Qdrant was specifically required by the task constraints.

### Why no RetrievalQAChain?
The custom RAG pipeline gives full control over every step: retrieval strategy, prompt structure, memory management, and output parsing. High-level chains obscure implementation details and make it harder to customize behavior for specific requirements like interview booking detection.

### Why Groq?
Groq provides extremely fast LLM inference (often 10–20x faster than OpenAI) on open-source models like LLaMA 3.3, making it ideal for a responsive chat API.

### Why Redis for memory?
Redis Lists provide O(1) append and O(n) retrieval, making them ideal for append-only conversation logs. Each session is a separate Redis key, enabling instant isolation and cleanup between users.

### Dependency Injection Pattern
All providers (embedding model, Qdrant client, Redis client, LLM client) are initialized **once at startup** in the `lifespan` context manager and stored on `app.state`. The `dependencies.py` module uses FastAPI's `Depends` system to inject them into services per-request, avoiding repeated initialization overhead.

### SQLAlchemy ORM
Using the declarative ORM with typed `Mapped` columns (SQLAlchemy 2.x style) provides full type safety, relationship management, and easy migration support, while keeping the codebase clean and maintainable.

---

*Built by Sandeep Regmi — AI/ML Intern Assignment for Palm Mind AI.*
