# CBP Training Assistant — AI-Powered Training Chatbot

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Functional Features](#2-functional-features)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Local Models Setup](#5-local-models-setup)
6. [Docker Deployment](#6-docker-deployment)
7. [Environment Configuration](#7-environment-configuration)
8. [API Reference](#8-api-reference)
9. [RAG Pipeline](#9-rag-pipeline)
10. [Prompt Engineering (Gemma 4)](#10-prompt-engineering-gemma-4)
11. [508 Accessibility Compliance](#11-508-accessibility-compliance)

---

## 1. Project Overview

**CBP Training Assistant** is a full-stack, AI-powered training chatbot designed to help U.S. Customs and Border Protection personnel learn about policies, procedures, and best practices. It combines a **Retrieval-Augmented Generation (RAG)** pipeline with a **large language model (LLM)** to deliver contextually accurate, educational guidance drawn from a curated knowledge base of CBP training materials.

### Key Capabilities

| Capability | Description |
|---|---|
| **Hybrid Search** | Combines dense embeddings (nomic-embed-text-v1.5 with MRL) and sparse embeddings (BM25) using reciprocal rank fusion |
| **Local Embedding Models** | Pre-downloaded models via Qdrant FastEmbed stored in `./models` directory |
| **Local LLM** | Ollama running locally with gemma4:latest model |
| **Gemma 4 Prompt Engineering** | Optimized system prompts, sampling parameters, and optional thinking mode per official Gemma 4 docs |
| **WebSocket Streaming** | Real-time response streaming for better user experience |
| **Global Chat History** | All Q&A pairs visible to all users with configurable display limit |
| **5-Star Rating System** | Trainees can rate bot responses from 1-5 stars |
| **508 Accessibility** | Full ARIA support, keyboard navigation, screen reader compatible |
| **Responsive Design** | Dark UI for desktop, tablet, and mobile |

---

## 2. Functional Features

### 2.1 Chat Interface
- **Welcome Screen**: Bot avatar with welcome message
- **Message Input**: Text input with Enter-key submission
- **User Messages**: Right-aligned blue bubbles with timestamp
- **Bot Messages**: Left-aligned white bubbles with markdown rendering

### 2.2 Global Chat History
- All Q&A pairs are stored in the database and visible to all users
- Sidebar displays individual questions (most recent first)
- Click any question to view the full answer in a popup dialog
- Configurable display limit (default: 20, options: 10/20/30/50/100) via sidebar settings
- History updates dynamically after each answered question (no page refresh needed)

### 2.3 5-Star Rating System
- Interactive star rating for each bot response
- Ratings persisted to PostgreSQL
- Aggregated in analytics dashboard

### 2.4 WebSocket Streaming
- Real-time character-by-character response display
- Streaming status indicators
- Automatic REST API fallback

### 2.5 Analytics Dashboard
- **Usage Metrics**: Total messages, sessions, ratings
- **Performance Metrics**: RAG latency, LLM latency, retrieval scores
- Scrollable layout for all dashboard content

---

## 3. Technology Stack

### 3.1 Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 19.1.0 | UI framework |
| **Axios** | 1.9.0 | HTTP client |
| **Recharts** | 2.15.3 | Analytics charts |
| **Lucide React** | 0.507.0 | Icons |
| **Shadcn UI** | — | Dialog, Button, and other UI components |

### 3.2 Backend

| Technology | Version | Purpose |
|---|---|---|
| **Django** | 5.2 | Web framework |
| **Django REST Framework** | 3.16.1 | REST API |
| **Django Channels** | 4.3.2 | WebSocket support |
| **Daphne** | 4.2.1 | ASGI server |

### 3.3 AI / ML

| Technology | Purpose |
|---|---|
| **Qdrant FastEmbed** | Local embedding generation (ONNX) |
| **nomic-embed-text-v1.5** | Dense embeddings (768d -> 256d MRL) |
| **Qdrant/bm25** | Sparse embeddings (BM25) |
| **Ollama** | Local LLM server |
| **gemma4:latest** | Language model for response generation |

### 3.4 Databases

| Technology | Version | Purpose |
|---|---|---|
| **PostgreSQL** | 15 | Sessions, messages, ratings |
| **Qdrant** | 1.17 | Vector similarity search |

### 3.5 Infrastructure

| Technology | Purpose |
|---|---|
| **Docker Compose** | Container orchestration |
| **Nginx** | Reverse proxy |

---

## 4. System Architecture

```
+-----------------------------------------------------------------------+
|                              DOCKER COMPOSE                            |
+-----------------------------------------------------------------------+
|                                                                        |
|  +-----------+    +-------------+    +-----------+                     |
|  |   nginx   |    |  frontend   |    |  backend  |                     |
|  |  (proxy)  |<---|   (React)   |    |  (Django) |                     |
|  |  :8080    |    |   :3000     |    |   :8001   |                     |
|  +-----+-----+    +-------------+    +-----+-----+                    |
|        |                                    |                          |
|        |           +------------------------+------------------+       |
|        |           |                        |                  |       |
|        |           v                        v                  v       |
|        |    +-----------+           +-----------+    +-----------+     |
|        |    |  postgres |           |  qdrant   |    |  ollama   |     |
|        |    |   (DB)    |           | (vectors) |    |  (LLM)    |     |
|        |    |   :5432   |           |   :6333   |    |  :11434   |     |
|        |    +-----------+           +-----------+    +-----------+     |
|        |                                                               |
|        +---------------------------------------------------------------+
|                                                                        |
|  VOLUMES:                                                              |
|  +-- postgres_data     (PostgreSQL data)                               |
|  +-- qdrant_data       (Vector database)                               |
|  +-- ./models          (Embedding + LLM models)                        |
|      +-- models--nomic-ai--nomic-embed-text-v1.5/   (FastEmbed)        |
|      +-- models--Qdrant--bm25/                      (FastEmbed)        |
|      +-- ollama/                                    (Ollama models)    |
|                                                                        |
+------------------------------------------------------------------------+
```

### Services

| Service | Container | Port | Purpose |
|---|---|---|---|
| **postgres** | cbp-postgres | 5432 | Relational database |
| **qdrant** | cbp-qdrant | 6333 | Vector database |
| **ollama** | cbp-ollama | 11434 | Local LLM server |
| **backend** | cbp-backend | 8001 | Django API + WebSocket |
| **frontend** | cbp-frontend | 3000 | React application |
| **nginx** | cbp-proxy | 8080 | Reverse proxy (entry point) |

---

## 5. Local Models Setup

All models are stored locally in the `./models` directory for offline deployment.

### 5.1 Embedding Models (FastEmbed)

| Model | Type | Size | Purpose |
|---|---|---|---|
| `nomic-ai/nomic-embed-text-v1.5` | Dense | ~547 MB | Semantic similarity (768d -> 256d MRL) |
| `Qdrant/bm25` | Sparse | ~20 MB | Keyword matching |

**Download embedding models:**
```bash
pip install fastembed
python download_models.py
```

### 5.2 LLM Model (Ollama)

| Model | Size | Purpose |
|---|---|---|
| `gemma4:latest` | ~5 GB | Response generation |

**Download Ollama model:**
```bash
python download_ollama_model.py
```

This script:
1. Starts a temporary Ollama Docker container
2. Downloads the model to `./models/ollama/`
3. Cleans up the temporary container

### 5.3 Model Directory Structure

```
models/
+-- models--nomic-ai--nomic-embed-text-v1.5/
|   +-- blobs/
|   |   +-- model.onnx              # Dense embedding model
|   +-- snapshots/
+-- models--Qdrant--bm25/
|   +-- ...                         # BM25 sparse model
+-- ollama/
    +-- models/
        +-- blobs/                  # Model weights (~5 GB)
        +-- manifests/              # Model metadata
```

---

## 6. Docker Deployment

### 6.1 Prerequisites

| Requirement | Minimum |
|---|---|
| Docker Engine | 24.0+ |
| Docker Compose | 2.20+ |
| RAM | 8 GB |
| Disk | 15 GB (models + images + data) |

### 6.2 Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd cbp-training-assistant

# 2. Download embedding models
pip install fastembed
python download_models.py

# 3. Download Ollama model
python download_ollama_model.py

# 4. Create environment file
cp .env.docker .env

# 5. Start all services
docker compose up -d --build

# 6. View logs
docker compose logs -f backend

# 7. Access the application
open http://localhost:8080
```

### 6.3 Docker Compose Services

```yaml
services:
  postgres:      # PostgreSQL 15
  qdrant:        # Qdrant v1.17
  ollama:        # Ollama with gemma4:latest
  backend:       # Django 5 + Daphne
  frontend:      # React 19 + Nginx
  nginx:         # Reverse proxy
```

### 6.4 Useful Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f backend
docker compose logs -f ollama

# Rebuild specific service
docker compose up -d --build backend

# Check service status
docker compose ps
```

---

## 7. Environment Configuration

### 7.1 Docker Environment (`.env.docker`)

```bash
# PostgreSQL
PG_DB_NAME=cbp_db
PG_DB_USER=cbp_user
PG_DB_PASSWORD=cbp_pass

# Qdrant
QDRANT_COLLECTION=cbp_training

# Ollama (local container)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma4:latest

# Embedding Models
MODELS_DIR=/app/models
DENSE_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
SPARSE_MODEL_NAME=Qdrant/bm25
MRL_EMBEDDING_DIM=256

# Ports
PROXY_PORT=8080
```

### 7.2 Key Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API endpoint (local container) |
| `OLLAMA_MODEL` | `gemma4:latest` | LLM model for response generation |
| `DENSE_MODEL_NAME` | `nomic-ai/nomic-embed-text-v1.5` | Dense embedding model |
| `SPARSE_MODEL_NAME` | `Qdrant/bm25` | Sparse embedding model |
| `MRL_EMBEDDING_DIM` | `256` | Truncated embedding dimension |
| `QDRANT_COLLECTION` | `cbp_training` | Vector collection name |

---

## 8. API Reference

### 8.1 Health Check

```
GET /api/
Response: {"message": "CBP Training Assistant API is running", "status": "ok"}
```

### 8.2 Service Status

```
GET /api/status/
Response: {
  "connected": true,
  "services": {
    "ollama": true,
    "qdrant": true,
    "postgresql": true
  }
}
```

### 8.3 Send Message (RAG + LLM)

```
POST /api/chat/
Content-Type: application/json

{"message": "What are primary inspection procedures?"}

Response: {
  "session_id": "<uuid>",
  "user_message": {...},
  "bot_message": {
    "text": "Based on our CBP training materials...",
    "sources": [
      {"title": "Primary Inspection Procedures", "score": 0.85}
    ]
  }
}
```

### 8.4 Global Conversations (Q&A History)

```
GET /api/conversations/?limit=20

Response: [
  {
    "id": "<uuid>",
    "question": "What are customs regulations?",
    "answer": "Based on our CBP training materials...",
    "answer_id": "<uuid>",
    "timestamp": "2026-04-13T16:00:00Z",
    "rating": null,
    "sources": [{"title": "...", "score": 0.85}]
  },
  ...
]
```

Query parameters:
- `limit` (int, default 20, max 100): Number of most recent Q&A pairs to return

### 8.5 WebSocket Streaming

```
ws://localhost:8080/ws/chat/{session_id}/

Send: {"message": "What is ESTA?"}
Receive: {"type": "status", "status": "Searching knowledge base..."}
Receive: {"type": "chunk", "text": "The Electronic System..."}
Receive: {"type": "done", "sources": [...]}
```

### 8.6 Ingest Training Data

```
POST /api/ingest/
Response: {"status": "success", "documents_ingested": 12}
```

### 8.7 Sessions & Feedback

```
GET    /api/sessions/                         # List all sessions
GET    /api/sessions/{id}/                    # Session detail with messages
DELETE /api/sessions/{id}/                    # Delete a session
DELETE /api/sessions/{id}/clear/              # Clear messages in session
PATCH  /api/messages/{id}/feedback/           # Rate a response (1-5 stars)
       Body: {"rating": 5}
```

### 8.8 Analytics

```
GET /api/analytics/usage/    # Usage stats, messages over time, rating distribution
GET /api/analytics/rag/      # RAG/LLM latency, score quality, performance trends
```

---

## 9. RAG Pipeline

### 9.1 Hybrid Search

The RAG pipeline uses hybrid search combining:

1. **Dense Search**: Semantic similarity using nomic-embed-text (256d MRL)
2. **Sparse Search**: Keyword matching using BM25
3. **Fusion**: Reciprocal Rank Fusion (RRF) combines results

### 9.2 Matryoshka Representation Learning (MRL)

nomic-embed-text is trained with MRL, allowing truncation from 768 to 256 dimensions with minimal quality loss:
- ~3x faster similarity search
- ~3x less memory usage
- Semantic features preserved in first 256 dims

### 9.3 Knowledge Base

12 CBP training modules covering:
- Primary & Secondary Inspection Procedures
- Immigration Document Verification
- Customs Declaration & Duty Assessment
- Agricultural Inspection
- Currency Reporting
- Visa Waiver Program & ESTA
- Trusted Traveler Programs
- Human Trafficking Indicators
- Use of Force & De-escalation
- TECS & Database Queries
- Ethics & Professional Conduct

---

## 10. Prompt Engineering (Gemma 4)

The system prompt and generation parameters are optimized for Gemma 4 following the official documentation:

- **References**:
  - [Gemma 4 Prompt Formatting](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4)
  - [Gemma 4 Model Card & Best Practices](https://ai.google.dev/gemma/docs/core/model_card_4)

### 10.1 Sampling Parameters

Per the Gemma 4 model card recommended configuration:

| Parameter | Value |
|---|---|
| `temperature` | 1.0 |
| `top_p` | 0.95 |
| `top_k` | 64 |

### 10.2 System Prompt Architecture

- **System message** defines the assistant's identity, role scope, and response guidelines
- **User message** carries only the RAG context and the trainee's question (no role duplication)
- Centralized in `backend/chat/llm_service.py` as `SYSTEM_PROMPT` constant

### 10.3 Thinking Mode (Optional)

Gemma 4 supports step-by-step reasoning via the `think=True` parameter in the Ollama API:
- A separate `SYSTEM_PROMPT_THINKING` variant includes an adaptive-thought-efficiency hint
- Reduces thinking tokens by ~20% while preserving output quality
- Can be toggled per-request for complex policy interpretation tasks

---

## 11. 508 Accessibility Compliance

### 11.1 ARIA Support
- `role` attributes for semantic meaning
- `aria-label` for interactive elements
- `aria-live` for dynamic content

### 11.2 Keyboard Navigation
- Tab navigation through all interactive elements
- Enter key to submit messages
- Visible focus indicators

### 11.3 Screen Reader Support
- Descriptive labels for all actions
- Hidden decorative elements with `aria-hidden`
- Semantic HTML structure

---

## License

This project is for U.S. Customs and Border Protection training purposes.
