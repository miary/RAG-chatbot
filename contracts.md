# API Contracts - PSPD Guardian

## Backend APIs (Django 5 - port 8001)

### 1. GET /api/ — Health check
Response: `{ "message": "...", "status": "ok" }`

### 2. GET /api/status/ — Service status
Response: `{ "connected": bool, "services": { "ollama": bool, "qdrant": bool, "postgresql": bool } }`

### 3. GET /api/sessions/ — List chat sessions
Response: `[{ "id": uuid, "title": str, "created_at": dt, "updated_at": dt, "message_count": int, "last_message_preview": str|null }]`

### 4. POST /api/sessions/ — Create session
Body: `{ "title": str (optional) }`
Response: `{ "id": uuid, "title": str, "messages": [] }`

### 5. GET /api/sessions/<id>/ — Get session with messages
Response: `{ "id", "title", "messages": [{ "id", "session", "message_type", "text", "timestamp", "feedback", "sources" }] }`

### 6. DELETE /api/sessions/<id>/ — Delete session

### 7. DELETE /api/sessions/<id>/clear/ — Clear messages in session

### 8. POST /api/chat/ — Send message (RAG + LLM)
Body: `{ "message": str, "session_id": uuid|null }`
Response: `{ "session_id": uuid, "user_message": {...}, "bot_message": {...} }`

### 9. PATCH /api/messages/<id>/feedback/ — Update feedback
Body: `{ "feedback": "up"|"down"|"none" }`

### 10. POST /api/ingest/ — Ingest mock data into Qdrant

## Frontend Integration Plan
- Replace `mockChatMessages` with real API calls
- Replace `mockChatHistory` with GET /api/sessions/
- Replace simulated bot response with POST /api/chat/
- Replace `mockConnectionStatus` with GET /api/status/
- Add feedback PATCH calls on thumbs up/down
- Store active session_id in state
