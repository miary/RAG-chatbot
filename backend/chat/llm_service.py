import logging

import ollama
from django.conf import settings

logger = logging.getLogger(__name__)


def build_rag_prompt(query: str, context_docs: list[dict]) -> str:
    """Build a prompt that includes retrieved context documents."""
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        context_parts.append(
            f"""--- Document {i} ---
"""
            f"Title: {doc.get('title', 'N/A')}\n"
            f"Category: {doc.get('category', 'N/A')}\n"
            f"Severity: {doc.get('severity', 'N/A')}\n"
            f"Content: {doc.get('content', '')}\n"
            f"Resolution: {doc.get('resolution', 'N/A')}\n"
        )

    context_text = '\n'.join(context_parts)

    prompt = f"""You are PSPD Guardian, a technical support assistant that helps users resolve Guardian system incidents. You provide clear, concise solutions based on historical incident data.

Use the following retrieved context documents to answer the user's question. If the context is relevant, reference specific details. If none of the context is relevant, say so honestly and offer general guidance.

=== Retrieved Context ===
{context_text}
=== End Context ===

User Question: {query}

Provide a helpful, accurate response. Be concise but thorough. If referencing a specific error code or resolution, mention it explicitly."""
    return prompt


def generate_response(query: str, context_docs: list[dict]) -> str:
    """Generate a response using Ollama with RAG context."""
    prompt = build_rag_prompt(query, context_docs)

    try:
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are PSPD Guardian, a helpful technical support chatbot for the PSPD Guardian system. You help users troubleshoot incidents and find solutions based on historical data. Keep responses concise and actionable.',
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
        )
        return response['message']['content']
    except Exception as e:
        logger.error('Ollama generation error: %s', e)
        return f'I apologize, but I encountered an error generating a response. Please try again. Error: {str(e)}'
