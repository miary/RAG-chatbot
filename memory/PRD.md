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

### Phase 8: Local Embedding Models via FastEmbed (COMPLETED - April 10, 2026)
- Switched to Qdrant FastEmbed for local embedding generation
- Dense model: nomic-ai/nomic-embed-text-v1.5-Q (quantized, 768d -> 256d MRL)
- Sparse model: Qdrant/bm25 (BM25-based sparse embeddings)
- Hybrid search with Reciprocal Rank Fusion (RRF)
- Models pre-downloaded to `./models` directory (~150MB total)

## Architecture

```
Frontend (React 19) → Nginx Proxy → Django 5.2 Backend (Daphne ASGI)
                                         ↓
                    ┌────────────────────┼────────────────────┐
                    ↓                    ↓                    ↓
              PostgreSQL          Qdrant (Remote)       Remote Ollama
              (sessions)         (148.230.92.74)        (LLM only)
                    ↑
              Local Models (./models via FastEmbed)
              - Dense: nomic-embed-text-v1.5-Q
              - Sparse: Qdrant/bm25
```

## Key Technical Details
- **Dense Embedding**: nomic-embed-text-v1.5-Q with MRL (768→256 dimensions) via FastEmbed
- **Sparse Embedding**: Qdrant/bm25 for keyword matching via FastEmbed
- **Hybrid Search**: RRF fusion of dense + sparse results
- **LLM Model**: llama3.1:8b (remote Ollama)
- **Vector DB**: Qdrant (remote at 148.230.92.74:6333)
- **Knowledge Base**: 12 FRDS incident documents
- **Rating System**: 5-star scale (1-5)

## Local Models Setup
```bash
# Download models before Docker deployment
pip install fastembed
python download_models.py

# Models saved to:
# - models/  (FastEmbed cache structure)
#   - nomic-ai/nomic-embed-text-v1.5-Q (~130MB)
#   - Qdrant/bm25 (~20MB)
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
All phases implemented. Application ready for production deployment with local FastEmbed-based embedding models.

## Future Enhancements (Backlog)
1. **P1**: User Authentication
2. **P2**: Knowledge Base Management UI
3. **P2**: Export Features
4. **P3**: Multi-language Support

## Changelog

### April 10, 2026
- Switched from sentence-transformers/SPLADE to Qdrant FastEmbed
- Dense model: nomic-ai/nomic-embed-text-v1.5-Q (quantized version, ~130MB vs ~550MB)
- Sparse model: Qdrant/bm25 (replaces SPLADE)
- Updated download_models.py to use FastEmbed API
- Updated rag_service.py for FastEmbed integration
- Updated documentation (README.md, docker-compose.yml, .env.docker)

### Previous Updates
- WebSocket streaming for real-time chat responses
- 5-star rating system for feedback
- Analytics dashboard with usage and RAG performance metrics
- Rebranding from "Guardian" to "FRDS"
