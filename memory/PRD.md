# PSPD Guardian RAG Chatbot - Product Requirements Document

## Original Problem Statement
Build a RAG (Retrieval-Augmented Generation) chatbot application with:
1. **Frontend**: Pixel-perfect, responsive clone of chatbot interface from Axure prototypes
2. **Backend**: Django-based RAG pipeline using remote Ollama instance
3. **Vector Database**: Qdrant for document embeddings and similarity search
4. **Analytics Dashboard**: Usage metrics and RAG performance visualization

## Core Requirements
- Use Django as the web framework
- Use `llama3.1` model for response generation via remote Ollama (http://31.220.21.156:11434)
- Use `nomic-embed-text` model for creating embeddings
- Use Qdrant as the vector database
- Full Docker setup for deployment
- Comprehensive README documentation

## Implementation Status

### Completed Features
- [x] React frontend matching Axure prototype designs (dark theme)
- [x] Django backend with REST API
- [x] RAG pipeline integration with remote Ollama
- [x] Chat session management (create, list, load, clear)
- [x] Message feedback system (thumbs up/down)
- [x] Service status monitoring (Ollama, Qdrant, DB)
- [x] Docker deployment configuration
- [x] Comprehensive README.md documentation
- [x] GitHub push to `miary/RAG-chatbot` repository
- [x] **Analytics Dashboard** (December 2025)
  - Usage Metrics tab with stat cards and time-series charts
  - RAG Performance tab with latency metrics and distributions
  - Tab navigation and back-to-chat functionality
  - Responsive dark theme matching main app

### Known Limitations
- Qdrant not available in preview environment (uses LLM fallback)
- Remote Ollama may have slow response times (30-120s cold starts)
- Database switched to SQLite for preview environment (Docker uses PostgreSQL)

## Architecture

### Frontend (React)
- `/app/frontend/src/App.js` - Main routing (/, /dashboard)
- `/app/frontend/src/components/Dashboard.jsx` - Analytics Dashboard
- `/app/frontend/src/components/ChatArea.jsx` - Chat interface
- `/app/frontend/src/components/Sidebar.jsx` - Navigation with dashboard link

### Backend (Django)
- `/app/backend/chat/views.py` - API endpoints including analytics
- `/app/backend/chat/models.py` - ChatSession, ChatMessage with performance metrics
- `/app/backend/chat/services/rag_service.py` - RAG pipeline
- `/app/backend/chat/services/llm_service.py` - Ollama integration

### API Endpoints
- `POST /api/chat/` - Send message, get RAG-augmented response
- `GET /api/sessions/` - List chat sessions
- `GET /api/sessions/{id}/` - Get session with messages
- `DELETE /api/sessions/{id}/clear/` - Clear session messages
- `PATCH /api/messages/{id}/feedback/` - Submit feedback
- `GET /api/analytics/usage/` - Usage metrics
- `GET /api/analytics/rag-performance/` - RAG performance metrics
- `GET /api/status/` - Service status check
- `POST /api/ingest/` - Ingest documents into Qdrant

## Future Enhancements (Backlog)
- [ ] Real-time analytics refresh
- [ ] Export analytics data (CSV/PDF)
- [ ] User authentication and multi-tenancy
- [ ] Document upload for RAG indexing
- [ ] Conversation summarization
- [ ] Custom embedding model support
