import logging

import ollama
from django.conf import settings

logger = logging.getLogger(__name__)


def build_rag_prompt(query: str, context_docs: list[dict]) -> str:
    """Build a prompt that includes retrieved context documents."""
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        context_parts.append(
            f"--- Document {i} ---\n"
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


def _fallback_response(query: str, context_docs: list[dict]) -> str:
    """Generate a structured response from RAG context when Ollama is unavailable.

    This is a deterministic fallback that formats the best-matching
    context document(s) into a readable answer.
    """
    if not context_docs:
        return (
            "I wasn't able to find specific information related to your query in our "
            "Guardian incident database. Please try rephrasing your question, or "
            "contact the Guardian support team at guardian-support@cbp.dhs.gov for "
            "further assistance."
        )

    top = context_docs[0]
    score = top.get('score', 0)

    # If best match has very low relevance, say so
    if score < 0.05:
        return (
            "I found some information in our database, but it may not directly address "
            "your question. Here's the closest match:\n\n"
            f"**{top.get('title', '')}**\n"
            f"{top.get('content', '')}\n\n"
            f"*Resolution:* {top.get('resolution', 'N/A')}\n\n"
            "If this doesn't help, please rephrase your question or contact "
            "guardian-support@cbp.dhs.gov."
        )

    # Good match – format a proper answer
    parts = []
    parts.append(f"Based on our Guardian incident database, here's what I found:\n")
    parts.append(f"**{top.get('title', '')}** (Category: {top.get('category', 'N/A')}, Severity: {top.get('severity', 'N/A')})\n")
    parts.append(f"{top.get('content', '')}\n")

    if top.get('resolution'):
        parts.append(f"\n**Recommended Resolution:** {top['resolution']}\n")

    # Include additional relevant docs if available
    additional = [d for d in context_docs[1:] if d.get('score', 0) > 0.1]
    if additional:
        parts.append("\n**Related incidents:**")
        for doc in additional:
            parts.append(f"- {doc.get('title', '')} ({doc.get('category', 'N/A')})")

    return '\n'.join(parts)


def generate_response(query: str, context_docs: list[dict]) -> str:
    """Generate a response using Ollama with RAG context.

    Falls back to a deterministic context-based response if Ollama
    is unavailable (e.g. insufficient memory in the container).
    """
    prompt = build_rag_prompt(query, context_docs)

    try:
        response = ollama.chat(
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
        )
        return response['message']['content']
    except Exception as e:
        logger.warning('Ollama unavailable (%s), using RAG-context fallback.', e)
        return _fallback_response(query, context_docs)
