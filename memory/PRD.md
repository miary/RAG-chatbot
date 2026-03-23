# PSPD Guardian - Product Requirements Document

## Original Problem Statement
Build a responsive, mobile-friendly chatbot interface based on Axure prototypes, implementing a full-stack RAG (Retrieval-Augmented Generation) backend for technical incident support.

## User Personas
- **Operations Teams**: Need rapid diagnosis and resolution of system incidents
- **Support Engineers**: Query the knowledge base for troubleshooting guidance
- **Administrators**: Monitor system health and analytics

## Core Requirements

### Phase 1: UI Clone (COMPLETED)
- Pixel-perfect frontend clone of Axure prototypes
- Dark-themed responsive chat interface
- Sidebar with chat history
- Service status indicators

### Phase 2: Full-Stack RAG Backend (COMPLETED)
- Django 5.2 backend with REST API
- PostgreSQL for session/message storage
- Qdrant for vector similarity search
- Remote Ollama for LLM and embeddings
- 12 pre-authored incident documents

### Phase 3: DevOps & Documentation (COMPLETED)
- Docker Compose orchestration
- Comprehensive README.md
- Makefile for common commands
- .gitignore configuration

### Phase 4: Tech Stack Upgrade (COMPLETED)
- Django 5.2
- nomic-embed-text embeddings via Ollama
- Qdrant latest version

### Phase 5: Analytics Dashboard (COMPLETED - March 23, 2026)
- Two-tab dashboard: Usage Metrics & RAG Performance
- Summary statistics cards
- Time-series charts (messages, latencies)
- Distribution visualizations (feedback, scores, latency buckets)

### Phase 6: Remote Qdrant Configuration (COMPLETED - March 23, 2026)
- Changed from local Qdrant to remote instance at 148.230.92.74:6333
- Updated docker-compose.yml (removed local qdrant service)
- Updated environment variables and documentation

## Architecture

```
Frontend (React 19) → Nginx Proxy → Django 5.2 Backend
                                         ↓
                           ┌─────────────┼─────────────┐
                           ↓             ↓             ↓
                     PostgreSQL    Remote Qdrant   Remote Ollama
                     (sessions)   (148.230.92.74)  (31.220.21.156)
```

## API Endpoints
- `GET /api/` - Health check
- `GET /api/status/` - Service connectivity status
- `GET/POST /api/sessions/` - List/create sessions
- `GET/DELETE /api/sessions/<id>/` - Session detail/delete
- `DELETE /api/sessions/<id>/clear/` - Clear messages
- `POST /api/chat/` - Send message (RAG + LLM)
- `PATCH /api/messages/<id>/feedback/` - Update feedback
- `POST /api/ingest/` - Ingest documents
- `GET /api/analytics/usage/` - Usage analytics
- `GET /api/analytics/rag/` - RAG performance analytics

## Key Technical Details
- **Embedding Model**: nomic-embed-text (768 dimensions)
- **LLM Model**: llama3.1:8b
- **Vector DB**: Qdrant (remote at 148.230.92.74:6333)
- **Knowledge Base**: 12 Guardian incident documents

## Status: COMPLETED
All phases implemented and tested. Application is production-ready.

## Future Enhancements (Backlog)
1. **User Authentication**: Add login/registration for personalized sessions
2. **Knowledge Base Management**: Admin UI for adding/editing documents
3. **Export Features**: Export chat history, analytics reports
4. **Real-time Updates**: WebSocket for live message streaming
5. **Multi-language Support**: i18n for different locales
