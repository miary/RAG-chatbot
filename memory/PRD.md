# FRDS - Product Requirements Document

## Original Problem Statement
Build a responsive, mobile-friendly chatbot interface implementing a full-stack RAG (Retrieval-Augmented Generation) backend for technical incident support.

## User Personas
- **Operations Teams**: Need rapid diagnosis and resolution of system incidents
- **Support Engineers**: Query the knowledge base for troubleshooting guidance
- **Administrators**: Monitor system health and analytics

## Core Requirements

### Phase 1-7: COMPLETED
- UI Clone with dark-themed responsive chat interface
- Full-Stack RAG Backend with Django 5.2, PostgreSQL, Qdrant
- Docker Compose orchestration and documentation
- Analytics Dashboard with Usage Metrics & RAG Performance tabs
- 5-Star Rating System
- WebSocket Streaming

### Phase 8: Local Embedding Models (COMPLETED - March 23, 2026)
- Switched from remote Ollama embeddings to local models
- Dense model: all-MiniLM-L6-v2 (sentence-transformers)
- Sparse model: SPLADE (naver/splade-cocondenser-ensembledistil)
- Hybrid search with Reciprocal Rank Fusion (RRF)
- Models pre-downloaded to `./models` directory

## Architecture

```
Frontend (React 19) → Nginx Proxy → Django 5.2 Backend
                                         ↓
                    ┌────────────────────┼────────────────────┐
                    ↓                    ↓                    ↓
              PostgreSQL            Qdrant               Remote Ollama
              (sessions)          (vectors)             (LLM only)
                    ↑
              Local Models (./models)
              - Dense: all-MiniLM-L6-v2
              - Sparse: SPLADE
```

## Key Technical Details
- **Dense Embedding**: all-MiniLM-L6-v2 with MRL (384→256 dimensions)
- **Sparse Embedding**: SPLADE for keyword matching
- **Hybrid Search**: RRF fusion of dense + sparse results
- **LLM Model**: llama3.1:8b (remote Ollama)
- **Vector DB**: Qdrant (containerized)
- **Knowledge Base**: 12 FRDS incident documents
- **Rating System**: 5-star scale (1-5)

## Local Models Setup
```bash
# Download models before Docker deployment
python download_models.py

# Models saved to:
# - models/dense/   (all-MiniLM-L6-v2, ~90MB)
# - models/sparse/  (SPLADE, ~400MB)
```

## Docker Deployment
```bash
# 1. Download models
python download_models.py

# 2. Start services
docker compose up -d

# 3. View logs
docker compose logs -f backend
```

## Status: COMPLETED
All phases implemented. Application ready for production deployment with local embedding models.

## Future Enhancements (Backlog)
1. User Authentication
2. Knowledge Base Management UI
3. Export Features
4. Multi-language Support
