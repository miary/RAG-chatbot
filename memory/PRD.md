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

## DB Schema — ChatMessage
- id, session, message_type, text, timestamp, rating, sources
- rag_latency_ms, llm_latency_ms, total_latency_ms, top_rag_score
- rag_num_sources, llm_model, llm_prompt_tokens, llm_response_tokens, llm_tokens_per_second

## Completed Features
- [x] Qdrant FastEmbed integration (BM25 + nomic-embed-text-v1.5)
- [x] Rebranded to "CBP Training Assistant" with mock CBP training data
- [x] Cleaned requirements.txt (removed unused google-* deps)
- [x] Fixed docker-compose.yml dependency issues for Qdrant v1.17
- [x] 508-compliant React UI (removed floating robot, external badges, added pill badge)
- [x] Fixed FastEmbed dimension attribute error in entrypoint
- [x] Local Ollama Docker service + download_ollama_model.py (gemma4:latest)
- [x] Comprehensive README.md update
- [x] Fixed .gitignore to allow .env.docker tracking
- [x] Gemma 4 prompt engineering (sampling params, thinking mode, centralized prompts)
- [x] UI Fix: Chat area scrolling, dashboard scrolling
- [x] UI Fix: Chat history popup dialog (Shadcn Dialog with Q&A preview + markdown formatting)
- [x] Dynamic chat history updates (sidebar refreshes after each response)
- [x] Global conversations model (not session-based, configurable display limit)
- [x] LLM & RAG metrics tracking — Apr 2026
  - New DB fields: rag_num_sources, llm_model, llm_prompt_tokens, llm_response_tokens, llm_tokens_per_second
  - generate_response() now returns dict with text + llm_meta (token counts from Ollama)
  - Conversations API includes metrics per Q&A pair
  - Popup dialog shows Performance Metrics section
  - Dashboard RAG tab shows 2 rows of stat cards: latency row + LLM token metrics row
  - Analytics API aggregates avg/total prompt tokens, response tokens, throughput, sources/query

## Backlog
- P1: User Authentication setup
- P2: Knowledge Base management UI
- P2: Export features for chat/analytics data
