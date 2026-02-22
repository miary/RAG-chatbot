import logging
import time

from django.utils import timezone
from django.db.models import Avg, Count, Sum, Max, Min, Q, F
from django.db.models.functions import TruncDate, TruncHour
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    ChatMessageSerializer,
    SendMessageSerializer,
    FeedbackSerializer,
)
from .rag_service import search_similar
from .llm_service import generate_response

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health_check(request):
    """Health / root endpoint."""
    return Response({'message': 'PSPD Guardian API is running', 'status': 'ok'})


@api_view(['GET'])
def service_status(request):
    """Return status of connected services (Ollama, Qdrant, PostgreSQL)."""
    statuses = {
        'ollama': False,
        'qdrant': False,
        'postgresql': True,  # If we got here, Django DB is working
    }

    # Check Ollama
    try:
        from .llm_service import get_ollama_client
        client = get_ollama_client()
        client.list()
        statuses['ollama'] = True
    except Exception as e:
        logger.warning('Ollama not reachable: %s', e)

    # Check Qdrant
    try:
        from .rag_service import get_qdrant
        client = get_qdrant()
        client.get_collections()
        statuses['qdrant'] = True
    except Exception as e:
        logger.warning('Qdrant not reachable: %s', e)

    all_connected = all(statuses.values())
    return Response({
        'connected': all_connected,
        'services': statuses,
    })


# ---------- Chat Session CRUD ----------

@api_view(['GET', 'POST'])
def session_list(request):
    """List all sessions or create a new one."""
    if request.method == 'GET':
        sessions = ChatSession.objects.all()
        serializer = ChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        session = ChatSession.objects.create(title=request.data.get('title', ''))
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
def session_detail(request, session_id):
    """Get or delete a single session."""
    try:
        session = ChatSession.objects.get(id=session_id)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def clear_session(request, session_id):
    """Delete all messages in a session (keep the session)."""
    try:
        session = ChatSession.objects.get(id=session_id)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    session.messages.all().delete()
    return Response({'status': 'cleared'})


# ---------- Send Message (RAG + LLM) ----------

@api_view(['POST'])
def send_message(request):
    """Accept a user message, perform RAG search, generate LLM response."""
    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_text = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id')

    # Get or create session
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Create a new session, title from first message
        title = user_text[:60] if len(user_text) > 60 else user_text
        session = ChatSession.objects.create(title=title)

    # Save user message
    user_msg = ChatMessage.objects.create(
        session=session,
        message_type='user',
        text=user_text,
    )

    # RAG: retrieve similar documents (with timing)
    t_start = time.time()
    try:
        context_docs = search_similar(user_text, top_k=3)
    except Exception as e:
        logger.error('RAG search failed: %s', e)
        context_docs = []
    rag_ms = int((time.time() - t_start) * 1000)

    # LLM: generate response (with timing)
    t_llm = time.time()
    bot_text = generate_response(user_text, context_docs)
    llm_ms = int((time.time() - t_llm) * 1000)
    total_ms = rag_ms + llm_ms

    top_score = max((d.get('score', 0) for d in context_docs), default=0.0)

    # Save bot message with sources and timing
    sources = [
        {'title': d.get('title', ''), 'score': round(d.get('score', 0), 3)}
        for d in context_docs
    ]
    bot_msg = ChatMessage.objects.create(
        session=session,
        message_type='bot',
        text=bot_text,
        sources=sources,
        rag_latency_ms=rag_ms,
        llm_latency_ms=llm_ms,
        total_latency_ms=total_ms,
        top_rag_score=round(top_score, 4),
    )

    # Update session title if it was auto-generated
    if not session.title:
        session.title = user_text[:60]
        session.save(update_fields=['title'])

    return Response({
        'session_id': str(session.id),
        'user_message': ChatMessageSerializer(user_msg).data,
        'bot_message': ChatMessageSerializer(bot_msg).data,
    })


# ---------- Feedback ----------

@api_view(['PATCH'])
def message_feedback(request, message_id):
    """Update feedback on a bot message."""
    try:
        message = ChatMessage.objects.get(id=message_id)
    except ChatMessage.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = FeedbackSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    message.feedback = serializer.validated_data['feedback']
    message.save(update_fields=['feedback'])
    return Response(ChatMessageSerializer(message).data)


# ---------- Ingest (admin) ----------

@api_view(['POST'])
def ingest_data(request):
    """Trigger ingestion of mock Guardian data into Qdrant."""
    from .rag_service import ensure_collection, ingest_documents
    from .mock_data import GUARDIAN_INCIDENTS

    try:
        ensure_collection()
        ingest_documents(GUARDIAN_INCIDENTS)
        return Response({
            'status': 'success',
            'documents_ingested': len(GUARDIAN_INCIDENTS),
        })
    except Exception as e:
        logger.error('Ingestion failed: %s', e)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
