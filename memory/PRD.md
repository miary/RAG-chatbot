# CBP Training Assistant - Product Requirements Document

## Original Problem Statement
Build a responsive, mobile-friendly chatbot interface to serve as a training tool for U.S. Customs and Border Protection (CBP) personnel. The assistant helps trainees learn about CBP policies, procedures, regulations, and best practices through an AI-powered conversational interface.

## User Personas
- **CBP Trainees**: New officers learning policies, procedures, and regulations
- **Field Training Officers**: Using the tool to supplement hands-on training
- **Training Supervisors**: Monitoring training engagement and knowledge gaps via analytics

## Core Requirements

### Phase 1-7: COMPLETED
- UI Clone with dark-themed responsive chat interface
- Full-Stack RAG Backend with Django 5.2, PostgreSQL, Qdrant
- Docker Compose orchestration and documentation
- Analytics Dashboard with Usage Metrics & Knowledge Base Performance tabs
- 5-Star Rating System for training quality feedback
- WebSocket Streaming for real-time responses

### Phase 8: Local Embedding Models via FastEmbed (COMPLETED)
- Switched to Qdrant FastEmbed for local embedding generation
- Dense model: nomic-ai/nomic-embed-text-v1.5-Q (quantized, 768d -> 256d MRL)
- Sparse model: Qdrant/bm25 (BM25-based sparse embeddings)
- Hybrid search with Reciprocal Rank Fusion (RRF)

### Phase 9: CBP Training Rebranding (COMPLETED - April 10, 2026)
- Rebranded from "FRDS" to "CBP Training Assistant"
- Created 12 realistic CBP training modules covering:
  - Primary & Secondary Inspection Procedures
  - Immigration Document Verification
  - Customs Declaration & Duty Assessment
  - Agricultural Inspection Requirements
  - Currency Reporting Requirements
  - Visa Waiver Program (VWP) and ESTA
  - Trusted Traveler Programs
  - Human Trafficking Indicators
  - Use of Force Policy & De-escalation
  - TECS & Law Enforcement Database Queries
  - CBP Ethics & Professional Conduct
- Updated all UI text, welcome messages, and placeholders
- Updated LLM system prompts for training context

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
- **Knowledge Base**: 12 CBP training modules
- **Rating System**: 5-star scale (1-5)

## Training Content Categories
1. **Inspection Procedures**: Primary inspection, secondary inspection, referral criteria
2. **Document Verification**: Passport verification, visa authentication, fraud detection
3. **Customs**: Declarations, duty assessment, prohibited items
4. **Agriculture**: Agricultural inspection, quarantine requirements
5. **Trade & Currency**: Currency reporting, monetary instruments
6. **Immigration**: Visa Waiver Program, ESTA, admissibility
7. **Trusted Traveler**: Global Entry, NEXUS, SENTRI, FAST
8. **Law Enforcement**: Human trafficking, officer safety, use of force
9. **Systems**: TECS, NCIC, database queries
10. **Professional Standards**: Ethics, conduct, reporting

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
All phases implemented. CBP Training Assistant ready for deployment.

## Future Enhancements (Backlog)
1. **P1**: User Authentication for personalized training tracking
2. **P2**: Knowledge Base Management UI for content updates
3. **P2**: Export features for training progress reports
4. **P3**: Multi-language support for diverse workforce
5. **P3**: Integration with official CBP Learning Portal

## Changelog

### April 10, 2026 - CBP Training Rebranding
- Rebranded entire application from "FRDS" to "CBP Training Assistant"
- Created 12 realistic CBP training modules
- Updated all frontend components (TopHeader, SubHeader, ChatArea, Sidebar, Dashboard)
- Updated backend mock_data.py with CBP training content
- Updated LLM system prompts for educational context
- Changed Qdrant collection from "frds_incidents" to "cbp_training"
- Updated all documentation (README.md, docker-compose.yml, .env files)

### April 10, 2026 - FastEmbed Integration
- Switched from sentence-transformers/SPLADE to Qdrant FastEmbed
- Dense model: nomic-ai/nomic-embed-text-v1.5-Q
- Sparse model: Qdrant/bm25

### Previous Updates
- WebSocket streaming for real-time chat responses
- 5-star rating system for feedback
- Analytics dashboard with usage and RAG performance metrics
