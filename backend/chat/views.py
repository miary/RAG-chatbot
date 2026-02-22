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
def analytics_usage(request):
    """Return usage metrics for the analytics dashboard."""
    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)
    seven_days_ago = now - timezone.timedelta(days=7)

    # Total counts
    total_sessions = ChatSession.objects.count()
    total_messages = ChatMessage.objects.count()
    total_user_messages = ChatMessage.objects.filter(message_type='user').count()
    total_bot_messages = ChatMessage.objects.filter(message_type='bot').count()

    # Feedback stats
    feedback_up = ChatMessage.objects.filter(feedback='up').count()
    feedback_down = ChatMessage.objects.filter(feedback='down').count()
    feedback_none = ChatMessage.objects.filter(feedback='none', message_type='bot').count()

    # Messages per day (last 30 days)
    messages_per_day = (
        ChatMessage.objects
        .filter(timestamp__gte=thirty_days_ago)
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Sessions per day (last 30 days)
    sessions_per_day = (
        ChatSession.objects
        .filter(created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Messages per hour (last 7 days) - for hourly distribution
    messages_per_hour = (
        ChatMessage.objects
        .filter(timestamp__gte=seven_days_ago)
        .annotate(hour=TruncHour('timestamp'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    # Average messages per session
    avg_msgs_per_session = 0
    if total_sessions > 0:
        avg_msgs_per_session = round(total_messages / total_sessions, 2)

    return Response({
        'summary': {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_user_messages': total_user_messages,
            'total_bot_messages': total_bot_messages,
            'avg_messages_per_session': avg_msgs_per_session,
        },
        'feedback': {
            'helpful': feedback_up,
            'not_helpful': feedback_down,
            'no_feedback': feedback_none,
        },
        'messages_per_day': [
            {'date': item['date'].isoformat(), 'count': item['count']}
            for item in messages_per_day
        ],
        'sessions_per_day': [
            {'date': item['date'].isoformat(), 'count': item['count']}
            for item in sessions_per_day
        ],
        'messages_per_hour': [
            {'hour': item['hour'].isoformat(), 'count': item['count']}
            for item in messages_per_hour
        ],
    })


@api_view(['GET'])
def analytics_rag_performance(request):
    """Return RAG performance metrics for the analytics dashboard."""
    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)
    seven_days_ago = now - timezone.timedelta(days=7)

    # Only bot messages have performance metrics
    bot_msgs = ChatMessage.objects.filter(message_type='bot')
    recent_bot_msgs = bot_msgs.filter(timestamp__gte=thirty_days_ago)

    # Overall averages
    overall_stats = bot_msgs.aggregate(
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
    )

    # Performance over time (daily averages, last 30 days)
    performance_per_day = (
        recent_bot_msgs
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(
            avg_rag_latency=Avg('rag_latency_ms'),
            avg_llm_latency=Avg('llm_latency_ms'),
            avg_total_latency=Avg('total_latency_ms'),
            avg_rag_score=Avg('top_rag_score'),
            count=Count('id'),
        )
        .order_by('date')
    )

    # RAG score distribution
    score_ranges = [
        {'label': '0.0 - 0.2', 'min': 0.0, 'max': 0.2},
        {'label': '0.2 - 0.4', 'min': 0.2, 'max': 0.4},
        {'label': '0.4 - 0.6', 'min': 0.4, 'max': 0.6},
        {'label': '0.6 - 0.8', 'min': 0.6, 'max': 0.8},
        {'label': '0.8 - 1.0', 'min': 0.8, 'max': 1.0},
    ]
    score_distribution = []
    for sr in score_ranges:
        count = bot_msgs.filter(
            top_rag_score__gte=sr['min'],
            top_rag_score__lt=sr['max'] if sr['max'] < 1.0 else 1.01
        ).count()
        score_distribution.append({'range': sr['label'], 'count': count})

    # Response time distribution
    latency_ranges = [
        {'label': '0-1s', 'min': 0, 'max': 1000},
        {'label': '1-3s', 'min': 1000, 'max': 3000},
        {'label': '3-5s', 'min': 3000, 'max': 5000},
        {'label': '5-10s', 'min': 5000, 'max': 10000},
        {'label': '10s+', 'min': 10000, 'max': 999999},
    ]
    latency_distribution = []
    for lr in latency_ranges:
        count = bot_msgs.filter(
            total_latency_ms__gte=lr['min'],
            total_latency_ms__lt=lr['max']
        ).count()
        latency_distribution.append({'range': lr['label'], 'count': count})

    # Recent responses (last 10) for detailed view
    recent_responses = (
        bot_msgs
        .order_by('-timestamp')[:10]
        .values(
            'id', 'timestamp', 'rag_latency_ms', 'llm_latency_ms',
            'total_latency_ms', 'top_rag_score'
        )
    )

    return Response({
        'summary': {
            'avg_rag_latency_ms': round(overall_stats['avg_rag_latency'] or 0, 2),
            'avg_llm_latency_ms': round(overall_stats['avg_llm_latency'] or 0, 2),
            'avg_total_latency_ms': round(overall_stats['avg_total_latency'] or 0, 2),
            'avg_rag_score': round(overall_stats['avg_rag_score'] or 0, 4),
            'max_rag_latency_ms': overall_stats['max_rag_latency'] or 0,
            'max_llm_latency_ms': overall_stats['max_llm_latency'] or 0,
            'max_total_latency_ms': overall_stats['max_total_latency'] or 0,
            'min_rag_latency_ms': overall_stats['min_rag_latency'] or 0,
            'min_llm_latency_ms': overall_stats['min_llm_latency'] or 0,
            'min_total_latency_ms': overall_stats['min_total_latency'] or 0,
        },
        'performance_per_day': [
            {
                'date': item['date'].isoformat(),
                'avg_rag_latency': round(item['avg_rag_latency'] or 0, 2),
                'avg_llm_latency': round(item['avg_llm_latency'] or 0, 2),
                'avg_total_latency': round(item['avg_total_latency'] or 0, 2),
                'avg_rag_score': round(item['avg_rag_score'] or 0, 4),
                'count': item['count'],
            }
            for item in performance_per_day
        ],
        'score_distribution': score_distribution,
        'latency_distribution': latency_distribution,
        'recent_responses': [
            {
                'id': str(item['id']),
                'timestamp': item['timestamp'].isoformat(),
                'rag_latency_ms': item['rag_latency_ms'],
                'llm_latency_ms': item['llm_latency_ms'],
                'total_latency_ms': item['total_latency_ms'],
                'top_rag_score': round(item['top_rag_score'], 4),
            }
            for item in recent_responses
        ],
    })
