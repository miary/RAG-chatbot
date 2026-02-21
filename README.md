# PSPD Guardian — AI-Powered Incident Support Chatbot

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Functional Features](#2-functional-features)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Backend Technical Documentation](#5-backend-technical-documentation)
6. [Frontend Technical Documentation](#6-frontend-technical-documentation)
7. [RAG Pipeline — Deep Dive](#7-rag-pipeline--deep-dive)
8. [Database Schema](#8-database-schema)
9. [API Reference](#9-api-reference)
10. [Knowledge Base — Ingested Documents](#10-knowledge-base--ingested-documents)
11. [Environment Configuration](#11-environment-configuration)
12. [Docker Deployment](#12-docker-deployment)
13. [Deployment & Infrastructure (Non-Docker)](#13-deployment--infrastructure-non-docker)
14. [Performance Characteristics](#14-performance-characteristics)
15. [Error Handling & Resilience](#15-error-handling--resilience)
16. [Project Structure](#16-project-structure)

---

## 1. Project Overview

**PSPD Guardian** is a full-stack, AI-powered technical support chatbot designed to help operations teams rapidly diagnose and resolve system incidents. It combines a **Retrieval-Augmented Generation (RAG)** pipeline with a **large language model (LLM)** to deliver contextually accurate, actionable troubleshooting guidance drawn from a curated knowledge base of historical Guardian system incidents.

The application presents a dark-themed, responsive chat interface — faithfully cloned from the original PSPD Guardian Axure prototype — where users can ask natural-language questions about technical issues, error codes, and troubleshooting procedures. The system semantically searches its vector database for the most relevant incident documentation, then feeds that context to the LLM to synthesize a clear, human-readable answer.

### Key Capabilities

| Capability | Description |
|---|---|
| **Semantic Search** | Cosine-similarity search over 384-dimensional sentence embeddings stored in Qdrant |
| **LLM Response Generation** | Ollama-hosted Llama 3.1 (8B) with system-prompt engineering and RAG context injection |
| **Multi-Turn Conversations** | Persistent sessions stored in PostgreSQL, enabling follow-up questions within the same context |
| **Feedback Collection** | Thumbs-up / thumbs-down per bot message, stored in the database for quality monitoring |
| **Real-Time Service Monitoring** | Live health checks for Ollama, Qdrant, and PostgreSQL displayed in the UI |
| **Graceful Degradation** | Deterministic RAG-context fallback when the LLM is unreachable |
| **Responsive Design** | Pixel-perfect dark UI for desktop, tablet, and mobile with collapsible sidebar |

---

## 2. Functional Features

### 2.1 Chat Interface

- **Welcome Screen**: Displays on first load or after clearing a chat. Shows the PSPD Guardian bot avatar, a welcome heading, and a brief description of the system's capabilities.
- **Message Input**: A text input field pinned to the bottom of the viewport. Supports both click-to-send (blue gradient send button) and Enter-key submission. Input is disabled while a response is being generated.
- **User Messages**: Displayed as right-aligned blue bubbles with a user avatar and timestamp.
- **Bot Messages**: Displayed as left-aligned white bubbles with the PSPD Guardian robot avatar, formatted text (bold, newlines), and a timestamp.
- **Typing Indicator**: An animated spinner with "Searching Guardian incidents..." text appears while the RAG + LLM pipeline is processing.
- **Markdown-Like Rendering**: Bot responses render `**bold text**` as `<strong>` elements and preserve line breaks.

### 2.2 Feedback System

Each bot response includes a "Was this helpful?" section with:
- **Thumbs Up** button — highlights in blue (`#6893ff`) when selected
- **Thumbs Down** button — highlights in red when selected
- Feedback is persisted to PostgreSQL via a PATCH API call and can be used for response quality analytics.

### 2.3 Chat History Sidebar

- **Session List**: Displays all past conversation sessions ordered by most recent activity. Each entry shows a truncated title (derived from the first user message) and a date.
- **Session Loading**: Clicking a sidebar entry loads the full conversation from the backend, restoring all messages with their original timestamps and feedback states.
- **New Chat Button** (`+`): Resets the current view to the welcome screen and creates a fresh session on the next message.
- **Empty State**: When no sessions exist, shows a chat-bubble icon with "No chat history yet / Start a new conversation."

### 2.4 Clear Chat

The "Clear Chat" button in the sub-header:
1. Sends a DELETE request to `/api/sessions/<id>/clear/` to remove all messages from the current session in PostgreSQL.
2. Resets the UI to the welcome screen.
3. Clears the active `session_id` so the next message creates a new session.

### 2.5 Service Status Monitoring

- **ADK Agent Status** (sidebar footer): Shows a colored status dot (teal = connected, red = disconnected) and descriptive text. Indicates the health of the Qdrant vector search service.
- **Connected Badge** (sub-header): Displays aggregate connection status. Polls `/api/status/` every 30 seconds.
- **Service Account Authentication Banner**: A teal-accented banner below the header confirming authentication status.

### 2.6 Responsive & Mobile Design

| Viewport | Behavior |
|---|---|
| **Desktop** (≥1024px) | Sidebar always visible. Full header with settings/user icons. |
| **Tablet / Mobile** (<1024px) | Sidebar hidden by default. Hamburger menu icon appears in the header. Sidebar slides in as an overlay with a dark backdrop. Sub-header buttons stack vertically. Floating chatbot FAB hidden on mobile. |

---

## 3. Technology Stack

### 3.1 Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 19.0.0 | UI component framework |
| **React Router DOM** | 7.5.1 | Client-side routing |
| **Axios** | 1.8.4 | HTTP client for API calls |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS framework |
| **Lucide React** | 0.507.0 | SVG icon library (Settings, User, Send, ThumbsUp, ThumbsDown, Plus, Menu, etc.) |
| **shadcn/ui** | — | Pre-built Radix UI components (available, used for design system foundation) |
| **Inter** | Google Fonts | Primary typeface |
| **CRACO** | 7.1.0 | Create React App configuration override |

### 3.2 Backend

| Technology | Version | Purpose |
|---|---|---|
| **Django** | 5.1.6 | Web framework (views, ORM, migrations) |
| **Django REST Framework** | 3.16.1 | RESTful API serialization and views |
| **django-cors-headers** | — | Cross-Origin Resource Sharing middleware |
| **Gunicorn** | 25.1.0 | WSGI HTTP server (production-grade) |
| **python-dotenv** | — | Environment variable management |

### 3.3 AI / ML

| Technology | Version | Purpose |
|---|---|---|
| **Ollama** (Python Client) | 0.6.1 | LLM inference client — connects to local or remote Ollama server |
| **Llama 3.1 8B** | `llama3.1:8b` | Large language model for response generation |
| **Sentence Transformers** | 5.2.3 | Embedding model loading and inference |
| **all-MiniLM-L6-v2** | — | 384-dimensional sentence embedding model for semantic search |

### 3.4 Databases

| Technology | Version | Purpose |
|---|---|---|
| **PostgreSQL** | 15.16 | Primary relational database — stores sessions, messages, feedback |
| **Qdrant** | 1.12.1 | Vector similarity search engine — stores document embeddings |
| **psycopg2-binary** | 2.9.11 | PostgreSQL adapter for Python |
| **qdrant-client** | 1.17.0 | Python client for Qdrant REST + gRPC API |

### 3.5 Infrastructure

| Technology | Purpose |
|---|---|
| **Supervisor** | Process manager — runs Gunicorn, React dev server, Nginx proxy |
| **Nginx** | Reverse proxy — routes `/api/*` to port 8001, all else to port 3000 |

---

## 4. System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                             │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  React 19 SPA                                                │    │
│  │  ├── TopHeader    (branding, settings, user icon)            │    │
│  │  ├── SubHeader    (auth badge, clear chat, connection badge) │    │
│  │  ├── Sidebar      (chat history, ADK status)                 │    │
│  │  ├── ChatArea     (messages, welcome, typing indicator)      │    │
│  │  └── MessageInput (text field, send button)                  │    │
│  └──────────────────────────┬───────────────────────────────────┘    │
│                              │  Axios HTTP                           │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Nginx Proxy       │
                    │  /api/* → :8001     │
                    │  /*     → :3000     │
                    └──────────┬──────────┘
                               │
              ┌────────────────▼─────────────────┐
              │     Django 5 + DRF (port 8001)   │
              │     Gunicorn WSGI Server          │
              │                                   │
              │  ┌─── views.py ────────────────┐  │
              │  │ health_check                │  │
              │  │ service_status               │  │
              │  │ session_list / session_detail│  │
              │  │ send_message (RAG + LLM)    │  │
              │  │ message_feedback             │  │
              │  │ ingest_data                  │  │
              │  └──────────┬──────────────────┘  │
              │             │                      │
              │  ┌──────────▼──────────────────┐  │
              │  │      RAG Pipeline            │  │
              │  │  1. Encode query → 384-d vec │  │
              │  │  2. Qdrant cosine search     │  │
              │  │  3. Build RAG prompt         │  │
              │  │  4. Ollama LLM generation    │  │
              │  │  5. Fallback if LLM offline  │  │
              │  └──┬──────────────┬───────────┘  │
              │     │              │                │
              └─────┼──────────────┼────────────────┘
                    │              │
        ┌───────────▼───┐  ┌──────▼────────────┐
        │  PostgreSQL   │  │  Qdrant (6333)    │
        │  (port 5432)  │  │  Vector DB         │
        │               │  │                    │
        │ • ChatSession │  │ • guardian_incidents│
        │ • ChatMessage │  │   collection       │
        │   (feedback,  │  │ • 384-d vectors    │
        │    sources)   │  │ • Cosine distance  │
        └───────────────┘  └────────────────────┘

                    ┌───────────────────────┐
                    │  Ollama Server         │
                    │  (Remote: 31.220.21   │
                    │   .156:11434)          │
                    │                       │
                    │  Model: llama3.1:8b   │
                    │  Context: 128k tokens │
                    └───────────────────────┘
```

### Request Flow — `POST /api/chat/`

```
User types "How do I fix error API-503?"
    │
    ▼
1. Frontend sends POST /api/chat/ { message, session_id }
    │
    ▼
2. Django view validates input (SendMessageSerializer)
    │
    ▼
3. Session: get existing or create new (title = first 60 chars)
    │
    ▼
4. Save user ChatMessage to PostgreSQL
    │
    ▼
5. RAG Search:
   a. Encode query with all-MiniLM-L6-v2 → 384-d vector
   b. Qdrant query_points(collection="guardian_incidents", limit=3)
   c. Returns top-3 documents with cosine similarity scores
    │
    ▼
6. LLM Generation:
   a. Build RAG prompt (system prompt + context docs + user question)
   b. Send to Ollama llama3.1:8b via HTTP
   c. If Ollama fails → _fallback_response() formats RAG context
    │
    ▼
7. Save bot ChatMessage to PostgreSQL (with sources JSON)
    │
    ▼
8. Return { session_id, user_message, bot_message } to frontend
    │
    ▼
9. Frontend renders bot response with FormatText component
   Displays "Was this helpful?" with thumbs up/down
```

---

## 5. Backend Technical Documentation

### 5.1 Django Project Structure

```
backend/
├── guardian_project/          # Django project configuration
│   ├── settings.py            # Database, middleware, app config, Ollama/Qdrant settings
│   ├── urls.py                # Root URL conf → includes chat.urls under /api/
│   ├── wsgi.py                # WSGI entry point for Gunicorn
│   └── asgi.py                # ASGI entry point (unused, available for WebSocket future)
├── chat/                      # Main application
│   ├── models.py              # ChatSession, ChatMessage Django ORM models
│   ├── views.py               # 8 API view functions (DRF @api_view decorators)
│   ├── urls.py                # 8 URL patterns mapped to views
│   ├── serializers.py         # 5 DRF serializers for request/response validation
│   ├── rag_service.py         # Qdrant + SentenceTransformer vector search service
│   ├── llm_service.py         # Ollama client + prompt engineering + fallback logic
│   ├── mock_data.py           # 12 Guardian incident documents for knowledge base
│   └── migrations/            # Django database migrations
├── manage.py                  # Django management CLI
└── .env                       # Environment variables
```

### 5.2 Service Layer Design

The backend follows a **layered service architecture**:

| Layer | File | Responsibility |
|---|---|---|
| **API Layer** | `views.py` | HTTP request handling, validation, response formatting |
| **Serialization Layer** | `serializers.py` | Input validation and output serialization (DRF) |
| **RAG Service** | `rag_service.py` | Embedding generation, Qdrant collection management, vector search |
| **LLM Service** | `llm_service.py` | Prompt construction, Ollama API calls, fallback logic |
| **Data Layer** | `models.py` | Django ORM models mapped to PostgreSQL tables |
| **Knowledge Base** | `mock_data.py` | Static incident document corpus for RAG ingestion |

### 5.3 Lazy-Loaded Singletons

Both the embedding model and database clients use a **lazy-loading singleton pattern** to avoid cold-start penalties on every request:

```python
# rag_service.py
_embedder = None     # SentenceTransformer('all-MiniLM-L6-v2')
_qdrant_client = None  # QdrantClient(host, port)

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder
```

```python
# llm_service.py
_ollama_client = None  # ollama.Client(host=OLLAMA_BASE_URL)

def get_ollama_client():
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = Client(host=settings.OLLAMA_BASE_URL)
    return _ollama_client
```

This means the first request incurs a ~2-3 second delay to load the embedding model into memory, but all subsequent requests reuse the cached instance.

### 5.4 RAG Prompt Engineering

The `build_rag_prompt()` function constructs a structured prompt that:

1. **System Role**: Defines the bot persona — "PSPD Guardian, a technical support assistant"
2. **Context Injection**: Inserts the top-3 retrieved documents with their title, category, severity, content, and resolution
3. **User Question**: Appends the original user query
4. **Instruction**: Asks the model to be "concise but thorough" and reference specific error codes

```
You are PSPD Guardian, a technical support assistant...

=== Retrieved Context ===
--- Document 1 ---
Title: API Gateway 503 Service Unavailable
Category: API
Severity: Critical
Content: A 503 Service Unavailable error from the Guardian API gateway...
Resolution: Check pod status, review logs, verify resource limits, check HPA.
--- Document 2 ---
...
=== End Context ===

User Question: How do I fix error API-503?

Provide a helpful, accurate response...
```

### 5.5 LLM Fallback Mechanism

When the remote Ollama server is unreachable (network timeout, server down, out of memory), the `_fallback_response()` function provides a **deterministic, structured response** based solely on the RAG-retrieved documents:

- If **no documents** match: Returns a "no information found" message with support contact info.
- If the **top match has low relevance** (score < 0.05): Presents the closest match with a caveat.
- If the **top match is relevant**: Formats a detailed answer with:
  - Document title, category, and severity
  - Full content
  - Recommended resolution
  - List of related incidents (from documents 2-3 with score > 0.1)

This ensures the chatbot **never returns an empty or broken response**, even when the LLM is offline.

---

## 6. Frontend Technical Documentation

### 6.1 Component Architecture

```
App.js (ChatApp)
├── Sidebar.jsx            # Chat history list, ADK agent status, new chat button
├── TopHeader.jsx          # PSPD Guardian branding, settings icon, user icon, mobile hamburger
├── SubHeader.jsx          # Auth badge, "Guardian Support Chat" title, Clear Chat, Connected badge
└── ChatArea.jsx           # Main content area
    ├── WelcomeState       # Centered robot icon + welcome text (shown when no messages)
    ├── BotMessage          # Left-aligned white bubble with avatar, formatted text, feedback
    │   └── FormatText     # Parses **bold** and \n newlines in bot responses
    ├── UserMessage         # Right-aligned blue bubble with user avatar
    └── TypingIndicator    # Animated spinner shown during LLM processing
```

### 6.2 State Management

All state is managed with React's `useState` and `useCallback` hooks in the root `ChatApp` component:

| State Variable | Type | Description |
|---|---|---|
| `messages` | `Array<Message>` | Current conversation messages |
| `chatHistory` | `Array<Session>` | All past sessions for the sidebar |
| `inputValue` | `string` | Current text in the message input |
| `showWelcome` | `boolean` | Whether to show the welcome screen vs. messages |
| `sidebarOpen` | `boolean` | Mobile sidebar open/closed state |
| `sessionId` | `string \| null` | Active session UUID |
| `isLoading` | `boolean` | Whether a chat request is in-flight |
| `serviceStatus` | `object` | Ollama/Qdrant/PostgreSQL connection status |
| `agentStatus` | `object` | ADK agent display status (dot color + text) |

### 6.3 Optimistic UI Updates

When a user sends a message:

1. A **temporary user message** is immediately added to the `messages` array (with a `temp-` prefixed ID) for instant visual feedback.
2. The input field is cleared and `isLoading` is set to `true`.
3. The `TypingIndicator` component renders while the backend processes.
4. Upon receiving the backend response, the temporary message is **replaced** with the server-confirmed message, and the bot response is appended.
5. If the API call fails, an error message is displayed as a bot bubble.

### 6.4 Color Palette

| Element | Hex Code | Usage |
|---|---|---|
| Main Background | `#0a1628` | Sidebar, input bar |
| Chat Area Background | `#111b2e` | Message viewport |
| Header Gradient | `#0c1a32 → #0a387b` | Top header bar |
| Primary Blue | `#6893ff` | Bot avatar border, accent color, active feedback |
| User Bubble | `#3b6fe0` | User message background |
| Send Button Gradient | `#8080ff → #00429d` | Send button |
| Clear Chat Gradient | `#1d2d49 → #0a387b` | Clear chat button |
| Status Teal | `#00AAAA` | Connected indicators, auth checkmarks |
| Status Red | `#ff4444` | Disconnected indicator |
| Light Text | `#BCCBF2` | Secondary sidebar text |
| Border | `#2a3a5c` | Sidebar borders, separators |

### 6.5 Typography

- **Font Family**: Inter (loaded via Google Fonts CDN), with system fallbacks
- **Weights Used**: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Icon Library**: Lucide React — all icons are SVG-based, tree-shakable

---

## 7. RAG Pipeline — Deep Dive

### 7.1 Embedding Model

| Property | Value |
|---|---|
| Model | `all-MiniLM-L6-v2` (Sentence Transformers) |
| Dimensions | 384 |
| Max Sequence Length | 256 tokens |
| Architecture | 6-layer MiniLM (distilled from BERT) |
| Size | ~80 MB |
| Inference Speed | ~5ms per query on CPU |

### 7.2 Vector Database Configuration

| Property | Value |
|---|---|
| Engine | Qdrant v1.12.1 |
| Collection Name | `guardian_incidents` |
| Vector Size | 384 |
| Distance Metric | Cosine Similarity |
| Documents Stored | 12 |
| Storage Path | `/var/lib/qdrant/storage` |
| API Port | 6333 (HTTP), 6334 (gRPC) |

### 7.3 Search Parameters

| Parameter | Value | Description |
|---|---|---|
| `top_k` | 3 | Number of documents retrieved per query |
| Distance | Cosine | Normalized similarity (0 = orthogonal, 1 = identical) |
| Score Threshold | 0.05 | Below this, the fallback labels the match as "may not directly address your question" |

### 7.4 Ingestion Pipeline

```
mock_data.py (12 documents)
    │
    ▼
ingest_documents()
    │
    ├── Extract 'content' field from each document
    ├── Batch-encode all texts with all-MiniLM-L6-v2
    ├── Create PointStruct(id, vector, payload) for each
    └── Upsert into Qdrant collection "guardian_incidents"
```

Each document's **payload** in Qdrant contains:
- `title` — Incident title
- `content` — Full descriptive text (used for embedding)
- `category` — Incident category (e.g., "API", "Security")
- `severity` — Critical / High / Medium / Low
- `resolution` — Recommended fix
- `error_code` — Machine-readable error identifier

---

## 8. Database Schema

### 8.1 PostgreSQL — `chat_chatsession`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PRIMARY KEY, auto-generated | Unique session identifier |
| `title` | `VARCHAR(255)` | BLANK allowed | Derived from first user message (truncated to 60 chars) |
| `created_at` | `TIMESTAMP WITH TZ` | Auto-set on creation | Session creation time |
| `updated_at` | `TIMESTAMP WITH TZ` | Auto-set on every save | Last activity time |

**Ordering**: `-updated_at` (most recent first)

### 8.2 PostgreSQL — `chat_chatmessage`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PRIMARY KEY, auto-generated | Unique message identifier |
| `session_id` | `UUID` | FOREIGN KEY → ChatSession, CASCADE DELETE | Parent session |
| `message_type` | `VARCHAR(4)` | `'user'` or `'bot'` | Who sent the message |
| `text` | `TEXT` | NOT NULL | Message content |
| `timestamp` | `TIMESTAMP WITH TZ` | Auto-set on creation | When the message was created |
| `feedback` | `VARCHAR(4)` | `'none'`, `'up'`, `'down'` | User feedback on bot responses |
| `sources` | `JSONB` | Default `[]` | RAG source documents `[{title, score}]` |

**Ordering**: `timestamp` (chronological within a session)

### 8.3 Qdrant — `guardian_incidents` Collection

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Document identifier (1–12) |
| `vector` | `float[384]` | all-MiniLM-L6-v2 embedding of the `content` field |
| `payload.title` | `string` | Incident title |
| `payload.content` | `string` | Full incident description |
| `payload.category` | `string` | One of 12 categories |
| `payload.severity` | `string` | Critical, High, Medium, Low |
| `payload.resolution` | `string` | Recommended fix |
| `payload.error_code` | `string` | Machine-readable code (e.g., `API-503`) |

---

## 9. API Reference

**Base URL**: `http://<host>/api`

### 9.1 Health Check

```
GET /api/
```

**Response** `200 OK`:
```json
{
  "message": "PSPD Guardian API is running",
  "status": "ok"
}
```

---

### 9.2 Service Status

```
GET /api/status/
```

**Response** `200 OK`:
```json
{
  "connected": true,
  "services": {
    "ollama": true,
    "qdrant": true,
    "postgresql": true
  }
}
```

The `connected` field is `true` only when **all three** services are reachable.

---

### 9.3 List Sessions

```
GET /api/sessions/
```

**Response** `200 OK`:
```json
[
  {
    "id": "675137fe-7c05-4235-aec8-32631b28e1c8",
    "title": "How do I fix error API-503?",
    "created_at": "2026-02-21T16:42:39.100Z",
    "updated_at": "2026-02-21T16:43:46.100Z",
    "message_count": 2,
    "last_message_preview": "Based on the retrieved context, the 503 Service Unavailable error is rela..."
  }
]
```

---

### 9.4 Create Session

```
POST /api/sessions/
Content-Type: application/json

{
  "title": "Optional session title"
}
```

**Response** `201 Created`:
```json
{
  "id": "<uuid>",
  "title": "Optional session title",
  "created_at": "...",
  "updated_at": "...",
  "messages": [],
  "last_message": null
}
```

---

### 9.5 Get Session Detail

```
GET /api/sessions/<uuid:session_id>/
```

**Response** `200 OK`:
```json
{
  "id": "<uuid>",
  "title": "...",
  "created_at": "...",
  "updated_at": "...",
  "messages": [
    {
      "id": "<uuid>",
      "session": "<uuid>",
      "message_type": "user",
      "text": "How do I fix error API-503?",
      "timestamp": "2026-02-21T16:42:39.163Z",
      "feedback": "none",
      "sources": []
    },
    {
      "id": "<uuid>",
      "session": "<uuid>",
      "message_type": "bot",
      "text": "Based on the retrieved context...",
      "timestamp": "2026-02-21T16:43:46.076Z",
      "feedback": "up",
      "sources": [
        { "title": "API Gateway 503 Service Unavailable", "score": 0.573 },
        { "title": "Authentication Failure - Service Account Lockout", "score": 0.328 }
      ]
    }
  ],
  "last_message": { ... }
}
```

**Error** `404 Not Found`: `{"error": "Session not found"}`

---

### 9.6 Delete Session

```
DELETE /api/sessions/<uuid:session_id>/
```

**Response** `204 No Content`

---

### 9.7 Clear Session Messages

```
DELETE /api/sessions/<uuid:session_id>/clear/
```

Removes all messages but **keeps the session record**.

**Response** `200 OK`:
```json
{ "status": "cleared" }
```

---

### 9.8 Send Message (RAG + LLM)

```
POST /api/chat/
Content-Type: application/json

{
  "message": "How do I resolve a 503 service unavailable error?",
  "session_id": "<uuid>"  // optional — omit to auto-create session
}
```

**Response** `200 OK`:
```json
{
  "session_id": "792c70e5-8cc4-4e0d-9f72-cd051cfe011c",
  "user_message": {
    "id": "c8c491fb-1945-451d-8120-4c7a55ef0172",
    "session": "792c70e5-...",
    "message_type": "user",
    "text": "How do I resolve a 503 service unavailable error?",
    "timestamp": "2026-02-21T16:42:39.163091Z",
    "feedback": "none",
    "sources": []
  },
  "bot_message": {
    "id": "a3a769da-59b3-48d6-95a7-8417c55d1843",
    "session": "792c70e5-...",
    "message_type": "bot",
    "text": "Based on the retrieved context, the 503 Service Unavailable error...",
    "timestamp": "2026-02-21T16:43:46.076063Z",
    "feedback": "none",
    "sources": [
      { "title": "API Gateway 503 Service Unavailable", "score": 0.573 },
      { "title": "Authentication Failure - Service Account Lockout", "score": 0.328 },
      { "title": "Incident Data Sync Delay", "score": 0.309 }
    ]
  }
}
```

**Validation Errors** `400 Bad Request`:
```json
{ "message": ["This field is required."] }
```

**Typical Response Times**: 30–60 seconds (dominated by Ollama LLM inference)

---

### 9.9 Update Message Feedback

```
PATCH /api/messages/<uuid:message_id>/feedback/
Content-Type: application/json

{
  "feedback": "up"   // "up", "down", or "none"
}
```

**Response** `200 OK`: Returns the updated message object.

---

### 9.10 Ingest Documents

```
POST /api/ingest/
```

Triggers ingestion of all 12 Guardian incident documents from `mock_data.py` into Qdrant.

**Response** `200 OK`:
```json
{
  "status": "success",
  "documents_ingested": 12
}
```

---

## 10. Knowledge Base — Ingested Documents

The system ships with 12 pre-authored Guardian incident documents spanning 12 categories:

| # | Error Code | Title | Category | Severity |
|---|---|---|---|---|
| 1 | `AUTH-001` | Authentication Failure — Service Account Lockout | Authentication | High |
| 2 | `DB-002` | Database Connection Timeout — Spanner Vector Search | Database | Critical |
| 3 | `API-503` | API Gateway 503 Service Unavailable | API | Critical |
| 4 | `SEC-010` | Certificate Expiration Warning | Security | High |
| 5 | `PERF-005` | Memory Leak in Guardian Processor Service | Performance | Medium |
| 6 | `DOC-001` | User Guide and Documentation Access | Documentation | Low |
| 7 | `LOG-003` | Log Aggregation Pipeline Failure | Logging | Medium |
| 8 | `RBAC-007` | Role-Based Access Control (RBAC) Permission Denied | Authorization | High |
| 9 | `SYNC-004` | Incident Data Sync Delay | Data Sync | Medium |
| 10 | `DEPLOY-002` | Deployment Rollback Procedure | Deployment | High |
| 11 | `NET-008` | SSL Handshake Failure with Upstream Services | Networking | High |
| 12 | `K8S-001` | Kubernetes Pod CrashLoopBackOff | Infrastructure | Critical |

Each document contains a detailed natural-language description (100–300 words) covering symptoms, root causes, diagnostic commands, and step-by-step resolution procedures.

---

## 11. Environment Configuration

### Backend — `/app/backend/.env`

| Variable | Default | Description |
|---|---|---|
| `PG_DB_NAME` | `guardian_db` | PostgreSQL database name |
| `PG_DB_USER` | `guardian_user` | PostgreSQL username |
| `PG_DB_PASSWORD` | `guardian_pass` | PostgreSQL password |
| `PG_DB_HOST` | `localhost` | PostgreSQL host |
| `PG_DB_PORT` | `5432` | PostgreSQL port |
| `OLLAMA_BASE_URL` | `http://31.220.21.156:11434` | Ollama API server URL (local or remote) |
| `OLLAMA_MODEL` | `llama3.1:8b` | Ollama model identifier |
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant HTTP API port |
| `QDRANT_COLLECTION` | `guardian_incidents` | Qdrant collection name for document vectors |
| `DJANGO_SECRET_KEY` | (auto-generated) | Django secret key for production |

### Frontend — `/app/frontend/.env`

| Variable | Description |
|---|---|
| `REACT_APP_BACKEND_URL` | External URL of the backend (set by infrastructure) |

---

## 12. Deployment & Infrastructure

### Process Management (Supervisor)

| Process | Command | Port |
|---|---|---|
| `backend` | `gunicorn guardian_project.wsgi:application --bind 0.0.0.0:8001 --workers 1 --timeout 300 --reload` | 8001 |
| `frontend` | `craco start` (React dev server) | 3000 |
| `nginx-proxy` | Reverse proxy routing | 80/443 |

### Service Dependencies (must be running)

| Service | Port | Start Command |
|---|---|---|
| PostgreSQL 15 | 5432 | `pg_ctlcluster 15 main start` |
| Qdrant 1.12.1 | 6333 | `qdrant --config-path /etc/qdrant/config.yaml` |
| Ollama (remote) | 11434 | Running at `http://31.220.21.156:11434` |

### First-Time Setup Sequence

```bash
# 1. Start PostgreSQL
pg_ctlcluster 15 main start

# 2. Create database
sudo -u postgres psql -c "CREATE USER guardian_user WITH PASSWORD 'guardian_pass';"
sudo -u postgres psql -c "CREATE DATABASE guardian_db OWNER guardian_user;"

# 3. Run Django migrations
cd /app/backend
python manage.py migrate

# 4. Start Qdrant
nohup qdrant --config-path /etc/qdrant/config.yaml &

# 5. Start backend (via supervisor)
sudo supervisorctl restart backend

# 6. Ingest knowledge base into Qdrant
curl -X POST http://localhost:8001/api/ingest/

# 7. Verify all services
curl http://localhost:8001/api/status/
```

---

## 13. Performance Characteristics

| Metric | Value | Notes |
|---|---|---|
| **Embedding Latency** | ~5 ms | Per query, CPU inference with all-MiniLM-L6-v2 |
| **Qdrant Search Latency** | ~2 ms | Cosine similarity over 12 documents (sub-linear at scale) |
| **Ollama LLM Latency** | 30–60 s | Cold start ~38s (model loading), warm ~10–15s per response |
| **Total Chat Response Time** | 10–65 s | Dominated by LLM inference time |
| **Fallback Response Time** | <100 ms | When Ollama is unavailable, deterministic response from RAG context |
| **Frontend Time-to-Interactive** | <2 s | React SPA with Tailwind CSS |
| **Session Load Time** | <200 ms | PostgreSQL query for session + messages |
| **Embedding Model Memory** | ~160 MB | Loaded once, reused across requests |
| **Gunicorn Workers** | 1 | Single worker to conserve memory in constrained environments |
| **Gunicorn Timeout** | 300 s | Set high to accommodate Ollama cold starts |

---

## 14. Error Handling & Resilience

### Backend Error Handling

| Scenario | Handling |
|---|---|
| Ollama server unreachable | `llm_service.py` catches the exception and invokes `_fallback_response()` — user receives a structured answer from RAG context alone |
| Qdrant search fails | `views.py` catches the exception, sets `context_docs = []`, LLM generates response without context |
| Invalid session ID | Returns `404 Not Found` with `{"error": "Session not found"}` |
| Invalid message format | DRF serializer validation returns `400 Bad Request` with field-level errors |
| Both Ollama and Qdrant down | Fallback returns a "no information found" message with support contact |

### Frontend Error Handling

| Scenario | Handling |
|---|---|
| Chat API fails | An error bot message is injected: "Sorry, I encountered an error processing your request." |
| Service status unreachable | Status polling continues every 30s; UI shows last known state |
| Feedback API fails | Error logged to console; UI state is not corrupted |
| Session load fails | Error logged to console; user stays on current view |

---

## 15. Project Structure

```
/app
├── backend/
│   ├── .env                           # Environment configuration
│   ├── manage.py                      # Django CLI
│   ├── requirements.txt               # Python dependencies (pip freeze)
│   ├── guardian_project/
│   │   ├── __init__.py
│   │   ├── settings.py                # Django settings (DB, Ollama, Qdrant config)
│   │   ├── urls.py                    # Root URL configuration
│   │   ├── wsgi.py                    # Gunicorn WSGI entry point
│   │   └── asgi.py                    # ASGI entry point
│   └── chat/
│       ├── __init__.py
│       ├── models.py                  # ChatSession, ChatMessage ORM models
│       ├── views.py                   # 8 DRF API view functions
│       ├── urls.py                    # 8 URL patterns
│       ├── serializers.py             # 5 DRF serializers
│       ├── rag_service.py             # Qdrant + SentenceTransformer service
│       ├── llm_service.py             # Ollama client + prompt + fallback
│       ├── mock_data.py               # 12 Guardian incident documents
│       ├── admin.py                   # Django admin (default)
│       ├── apps.py                    # App configuration
│       ├── tests.py                   # Test stubs
│       └── migrations/
│           └── 0001_initial.py        # Initial schema migration
├── frontend/
│   ├── .env                           # REACT_APP_BACKEND_URL
│   ├── package.json                   # Node dependencies
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   └── src/
│       ├── App.js                     # Root component, state management, API integration
│       ├── App.css                    # Global styles, scrollbar, FAB, responsive rules
│       ├── index.js                   # React DOM entry point
│       ├── index.css                  # Tailwind base + CSS variables (dark theme)
│       ├── data/
│       │   └── mockData.js            # Original mock data (retained for reference)
│       ├── components/
│       │   ├── ChatArea.jsx           # Messages, welcome state, input bar, typing indicator
│       │   ├── Sidebar.jsx            # Chat history, ADK status, new chat
│       │   ├── TopHeader.jsx          # Branding, settings, user, hamburger
│       │   ├── SubHeader.jsx          # Auth badge, support chat title, clear/connected
│       │   └── ui/                    # shadcn/ui component library (40+ components)
│       ├── hooks/
│       │   └── use-toast.js           # Toast notification hook
│       └── lib/
│           └── utils.js               # Tailwind class merge utility
├── contracts.md                       # API contract documentation
└── README.md                          # This file
```

---

*PSPD Guardian — Built with Django 5, React 19, Ollama Llama 3.1, Qdrant, and PostgreSQL.*
