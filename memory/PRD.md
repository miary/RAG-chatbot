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
- [x] Fixed .gitignore to allow .env.docker tracking — Feb 2026
- [x] Gemma 4 prompt engineering (sampling params, thinking mode, centralized prompts) — Feb 2026
- [x] UI Fix: Chat area scrolling (min-h-0 flex fix) — Feb 2026
- [x] UI Fix: Chat history popup dialog (Shadcn Dialog with Q&A preview) — Feb 2026
- [x] UI Fix: Dynamic chat history updates (sidebar refreshes after each response) — Feb 2026

## Backlog
- P1: User Authentication setup
- P2: Knowledge Base management UI
- P2: Export features for chat/analytics data
