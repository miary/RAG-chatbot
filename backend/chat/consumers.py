import json
import logging
import time
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for streaming chat responses."""

    async def connect(self):
        """Handle WebSocket connection."""
        self.session_id = self.scope['url_route']['kwargs'].get('session_id')
        self.room_group_name = f'chat_{self.session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f'WebSocket connected: session={self.session_id}')

        # Send connection acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'session_id': self.session_id,
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f'WebSocket disconnected: session={self.session_id}, code={close_code}')

    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f'Error handling message: {e}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_chat_message(self, data):
        """Process a chat message and stream the response."""
        user_message = data.get('message', '').strip()
        if not user_message:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Empty message'
            }))
            return

        total_start = time.time()

        # Get or create session
        session = await self.get_or_create_session(user_message)

        # Save user message
        user_msg = await self.save_message(
            session_id=session.id,
            message_type='user',
            text=user_message
        )

        # Send user message confirmation
        await self.send(text_data=json.dumps({
            'type': 'user_message_saved',
            'message': {
                'id': str(user_msg.id),
                'text': user_message,
                'timestamp': user_msg.timestamp.isoformat(),
            }
        }))

        # Start RAG retrieval
        await self.send(text_data=json.dumps({
            'type': 'status',
            'status': 'retrieving',
            'message': 'Searching knowledge base...'
        }))

        rag_start = time.time()
        context_docs, top_score = await self.retrieve_context(user_message)
        rag_latency_ms = int((time.time() - rag_start) * 1000)

        # Prepare sources for frontend
        sources = [
            {'title': doc.get('title', 'N/A'), 'score': round(doc.get('score', 0), 3)}
            for doc in context_docs[:3]
        ]

        # Send RAG results
        await self.send(text_data=json.dumps({
            'type': 'rag_complete',
            'sources': sources,
            'rag_latency_ms': rag_latency_ms,
        }))

        # Start LLM generation
        await self.send(text_data=json.dumps({
            'type': 'status',
            'status': 'generating',
            'message': 'Generating response...'
        }))

        llm_start = time.time()

        # Create bot message placeholder
        bot_msg_id = str(uuid.uuid4())
        await self.send(text_data=json.dumps({
            'type': 'stream_start',
            'message_id': bot_msg_id,
        }))

        # Stream the response
        full_response = ""
        try:
            async for chunk in self.stream_llm_response(user_message, context_docs):
                full_response += chunk
                await self.send(text_data=json.dumps({
                    'type': 'stream_chunk',
                    'message_id': bot_msg_id,
                    'chunk': chunk,
                }))
        except Exception as e:
            logger.error(f'LLM streaming error: {e}')
            # Fallback to non-streaming response
            full_response = await self.get_fallback_response(user_message, context_docs)
            await self.send(text_data=json.dumps({
                'type': 'stream_chunk',
                'message_id': bot_msg_id,
                'chunk': full_response,
            }))

        llm_latency_ms = int((time.time() - llm_start) * 1000)
        total_latency_ms = int((time.time() - total_start) * 1000)

        # Save bot message to database
        bot_msg = await self.save_message(
            session_id=session.id,
            message_type='bot',
            text=full_response,
            sources=sources,
            rag_latency_ms=rag_latency_ms,
            llm_latency_ms=llm_latency_ms,
            total_latency_ms=total_latency_ms,
            top_rag_score=top_score,
        )

        # Send stream complete
        await self.send(text_data=json.dumps({
            'type': 'stream_complete',
            'message_id': str(bot_msg.id),
            'message': {
                'id': str(bot_msg.id),
                'text': full_response,
                'timestamp': bot_msg.timestamp.isoformat(),
                'sources': sources,
                'rag_latency_ms': rag_latency_ms,
                'llm_latency_ms': llm_latency_ms,
                'total_latency_ms': total_latency_ms,
            }
        }))

    @database_sync_to_async
    def get_or_create_session(self, title):
        """Get existing session or create a new one."""
        from .models import ChatSession

        if self.session_id and self.session_id != 'new':
            try:
                return ChatSession.objects.get(id=self.session_id)
            except ChatSession.DoesNotExist:
                pass

        # Create new session
        session = ChatSession.objects.create(
            title=title[:50] if len(title) > 50 else title
        )
        self.session_id = str(session.id)
        return session

    @database_sync_to_async
    def save_message(self, session_id, message_type, text, sources=None,
                     rag_latency_ms=0, llm_latency_ms=0, total_latency_ms=0,
                     top_rag_score=0.0):
        """Save a message to the database."""
        from .models import ChatSession, ChatMessage

        session = ChatSession.objects.get(id=session_id)
        return ChatMessage.objects.create(
            session=session,
            message_type=message_type,
            text=text,
            sources=sources or [],
            rag_latency_ms=rag_latency_ms,
            llm_latency_ms=llm_latency_ms,
            total_latency_ms=total_latency_ms,
            top_rag_score=top_rag_score,
        )

    @database_sync_to_async
    def retrieve_context(self, query):
        """Retrieve relevant documents from Qdrant."""
        from .rag_service import search_similar

        results = search_similar(query, top_k=3)
        top_score = results[0].get('score', 0) if results else 0.0
        return results, top_score

    async def stream_llm_response(self, query, context_docs):
        """Stream response from Ollama LLM."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        from .llm_service import build_rag_prompt, get_ollama_client

        prompt = build_rag_prompt(query, context_docs)

        def generate_chunks():
            """Run the blocking Ollama streaming in a thread."""
            try:
                client = get_ollama_client()
                stream = client.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {
                            'role': 'system',
                            'content': (
                                'You are PSPD Guardian, a helpful technical support chatbot for '
                                'the PSPD Guardian system. You help users troubleshoot incidents '
                                'and find solutions based on historical data. Keep responses '
                                'concise and actionable.'
                            ),
                        },
                        {
                            'role': 'user',
                            'content': prompt,
                        },
                    ],
                    stream=True,
                )
                
                chunks = []
                for chunk in stream:
                    if chunk and 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        if content:
                            chunks.append(content)
                return chunks
            except Exception as e:
                logger.error(f'Ollama streaming error: {e}')
                raise

        # Run blocking Ollama call in thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            chunks = await loop.run_in_executor(executor, generate_chunks)
        
        # Yield chunks
        for chunk in chunks:
            yield chunk

    @database_sync_to_async
    def get_fallback_response(self, query, context_docs):
        """Get fallback response when streaming fails."""
        from .llm_service import _fallback_response
        return _fallback_response(query, context_docs)
