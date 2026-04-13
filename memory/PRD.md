# CBP Training Assistant — PRD

## Problem Statement
Adapt a full-stack RAG chatbot into a "CBP Training Assistant" using local-only infrastructure: Qdrant FastEmbed (BM25 + nomic-embed-text-v1.5), local Dockerized Ollama (gemma4:latest), PostgreSQL, and a 508-compliant React UI.

## Architecture
- **Frontend**: React 19 (508-compliant, responsive)
- **Backend**: Django 5.2, Django Channels, Daphne (ASGI)
- **Database**: PostgreSQL (metadata), Qdrant v1.17 (vectors)
- **RAG**: Qdrant FastEmbed (dense: nomic-embed-text-v1.5 @256d, sparse: BM25)
- **LLM**: Local Ollama Docker container (gemma4:latest)
- **DevOps**: Docker Compose (all services local)

## Completed Features
- [x] Qdrant FastEmbed integration (BM25 + nomic-embed-text-v1.5) — Feb 2026
- [x] Rebranded to "CBP Training Assistant" with mock CBP training data — Feb 2026
- [x] Cleaned requirements.txt (removed unused google-* deps) — Feb 2026
- [x] Fixed docker-compose.yml dependency issues for Qdrant v1.17 — Feb 2026
- [x] 508-compliant React UI (removed floating robot, external badges, added pill badge) — Feb 2026
- [x] Fixed FastEmbed dimension attribute error in entrypoint — Feb 2026
- [x] Local Ollama Docker service + download_ollama_model.py (gemma4:latest) — Feb 2026
- [x] Comprehensive README.md update — Feb 2026
- [x] Fixed .gitignore to allow .env.docker tracking (!.env.docker whitelist) — Feb 2026
- [x] Gemma 4 prompt engineering overhaul — Feb 2026
  - Applied official Gemma 4 sampling parameters (temp=1.0, top_p=0.95, top_k=64)
  - Fixed stale "FRDS" system prompt in WebSocket streaming path
  - Restructured prompts: system role defines identity/behaviour, user message carries context+question only
  - Added thinking mode support (opt-in via `think=True`)
  - Added adaptive-thought-efficiency hint per Gemma 4 docs
  - Centralized prompt constants in llm_service.py (single source of truth)

## Backlog
- P1: User Authentication setup
- P2: Knowledge Base management UI
- P2: Export features for chat/analytics data
