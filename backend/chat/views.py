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


# ---------- Analytics ----------

@api_view(['GET'])
def usage_analytics(request):
    """Return usage analytics for the dashboard.
    
    Provides:
    - Total messages (user + bot)
    - Total sessions
    - Average messages per session
    - Message counts over time (daily)
    - Feedback distribution
    """
    from datetime import timedelta
    
    # Time range: last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Total counts
    total_sessions = ChatSession.objects.count()
    total_messages = ChatMessage.objects.count()
    total_user_messages = ChatMessage.objects.filter(message_type='user').count()
    total_bot_messages = ChatMessage.objects.filter(message_type='bot').count()
    
    # Average messages per session
    avg_messages_per_session = round(total_messages / total_sessions, 2) if total_sessions > 0 else 0
    
    # Messages over time (daily for last 30 days)
    messages_by_day = (
        ChatMessage.objects
        .filter(timestamp__gte=start_date)
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(
            user_count=Count('id', filter=Q(message_type='user')),
            bot_count=Count('id', filter=Q(message_type='bot')),
            total=Count('id'),
        )
        .order_by('date')
    )
    
    # Feedback distribution (only for bot messages)
    feedback_dist = (
        ChatMessage.objects
        .filter(message_type='bot')
        .values('feedback')
        .annotate(count=Count('id'))
    )
    feedback_summary = {item['feedback']: item['count'] for item in feedback_dist}
    
    # Sessions created over time (daily for last 30 days)
    sessions_by_day = (
        ChatSession.objects
        .filter(created_at__gte=start_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    return Response({
        'summary': {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_user_messages': total_user_messages,
            'total_bot_messages': total_bot_messages,
            'avg_messages_per_session': avg_messages_per_session,
        },
        'messages_over_time': [
            {
                'date': item['date'].isoformat() if item['date'] else None,
                'user_count': item['user_count'],
                'bot_count': item['bot_count'],
                'total': item['total'],
            }
            for item in messages_by_day
        ],
        'sessions_over_time': [
            {
                'date': item['date'].isoformat() if item['date'] else None,
                'count': item['count'],
            }
            for item in sessions_by_day
        ],
        'feedback_distribution': {
            'thumbs_up': feedback_summary.get('up', 0),
            'thumbs_down': feedback_summary.get('down', 0),
            'no_feedback': feedback_summary.get('none', 0),
        },
    })


@api_view(['GET'])
def rag_performance_analytics(request):
    """Return RAG performance analytics for the dashboard.
    
    Provides:
    - Average RAG latency
    - Average LLM latency
    - Average total latency
    - Average RAG similarity score
    - Latency distribution over time
    - Score distribution
    """
    from datetime import timedelta
    
    # Only analyze bot messages (they have the performance metrics)
    bot_messages = ChatMessage.objects.filter(message_type='bot')
    
    # Overall statistics
    stats = bot_messages.aggregate(
        avg_rag_latency=Avg('rag_latency_ms'),
        avg_llm_latency=Avg('llm_latency_ms'),
        avg_total_latency=Avg('total_latency_ms'),
        avg_rag_score=Avg('top_rag_score'),
        max_rag_latency=Max('rag_latency_ms'),
        max_llm_latency=Max('llm_latency_ms'),
        max_total_latency=Max('total_latency_ms'),
        min_rag_latency=Min('rag_latency_ms'),
        min_llm_latency=Min('llm_latency_ms'),
        min_total_latency=Min('total_latency_ms'),
        max_rag_score=Max('top_rag_score'),
        min_rag_score=Min('top_rag_score'),
        total_responses=Count('id'),
    )
    
    # Time range: last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Latency over time (daily averages)
    latency_by_day = (
        bot_messages
        .filter(timestamp__gte=start_date)
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(
            avg_rag=Avg('rag_latency_ms'),
            avg_llm=Avg('llm_latency_ms'),
            avg_total=Avg('total_latency_ms'),
            avg_score=Avg('top_rag_score'),
            count=Count('id'),
        )
        .order_by('date')
    )
    
    # Score distribution (buckets)
    score_buckets = {
        'excellent': bot_messages.filter(top_rag_score__gte=0.7).count(),
        'good': bot_messages.filter(top_rag_score__gte=0.5, top_rag_score__lt=0.7).count(),
        'fair': bot_messages.filter(top_rag_score__gte=0.3, top_rag_score__lt=0.5).count(),
        'poor': bot_messages.filter(top_rag_score__lt=0.3).count(),
    }
    
    # Latency distribution (buckets in ms)
    latency_buckets = {
        'fast': bot_messages.filter(total_latency_ms__lt=5000).count(),       # < 5s
        'normal': bot_messages.filter(total_latency_ms__gte=5000, total_latency_ms__lt=30000).count(),  # 5-30s
        'slow': bot_messages.filter(total_latency_ms__gte=30000, total_latency_ms__lt=60000).count(),   # 30-60s
        'very_slow': bot_messages.filter(total_latency_ms__gte=60000).count(),  # > 60s
    }
    
    return Response({
        'summary': {
            'total_responses': stats['total_responses'] or 0,
            'avg_rag_latency_ms': round(stats['avg_rag_latency'] or 0, 2),
            'avg_llm_latency_ms': round(stats['avg_llm_latency'] or 0, 2),
            'avg_total_latency_ms': round(stats['avg_total_latency'] or 0, 2),
            'avg_rag_score': round(stats['avg_rag_score'] or 0, 4),
            'max_rag_latency_ms': stats['max_rag_latency'] or 0,
            'max_llm_latency_ms': stats['max_llm_latency'] or 0,
            'min_rag_latency_ms': stats['min_rag_latency'] or 0,
            'min_llm_latency_ms': stats['min_llm_latency'] or 0,
            'max_rag_score': round(stats['max_rag_score'] or 0, 4),
            'min_rag_score': round(stats['min_rag_score'] or 0, 4),
        },
        'latency_over_time': [
            {
                'date': item['date'].isoformat() if item['date'] else None,
                'avg_rag_ms': round(item['avg_rag'] or 0, 2),
                'avg_llm_ms': round(item['avg_llm'] or 0, 2),
                'avg_total_ms': round(item['avg_total'] or 0, 2),
                'avg_score': round(item['avg_score'] or 0, 4),
                'count': item['count'],
            }
            for item in latency_by_day
        ],
        'score_distribution': score_buckets,
        'latency_distribution': latency_buckets,
    })
