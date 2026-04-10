import logging

from ollama import Client
from django.conf import settings

logger = logging.getLogger(__name__)

# Create Ollama client pointing to the configured (possibly remote) server
_ollama_client = None


def get_ollama_client():
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = Client(host=settings.OLLAMA_BASE_URL)
        logger.info('Ollama client configured for %s', settings.OLLAMA_BASE_URL)
    return _ollama_client


def build_rag_prompt(query: str, context_docs: list[dict]) -> str:
    """Build a prompt that includes retrieved training content."""
    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        context_parts.append(
            f"--- Training Module {i} ---\n"
            f"Title: {doc.get('title', 'N/A')}\n"
            f"Category: {doc.get('category', 'N/A')}\n"
            f"Module: {doc.get('module', 'N/A')}\n"
            f"Content: {doc.get('content', '')}\n"
        )

    context_text = '\n'.join(context_parts)

    prompt = f"""You are the CBP Training Assistant, an AI-powered learning companion designed to help U.S. Customs and Border Protection personnel understand policies, procedures, and best practices.

Use the following training materials to answer the trainee's question. Provide clear, accurate information based on official CBP procedures. If the training content is relevant, reference specific details and procedures. If the question is outside the available training materials, acknowledge this and suggest consulting official CBP resources or supervisors.

=== Training Materials ===
{context_text}
=== End Training Materials ===

Trainee Question: {query}

Provide a helpful, educational response. Be clear and thorough, emphasizing proper procedures and compliance. When referencing specific regulations or procedures, cite them explicitly. Encourage the trainee to practice these skills and seek hands-on guidance from experienced officers."""
    return prompt


def _fallback_response(query: str, context_docs: list[dict]) -> str:
    """Generate a structured response from training content when Ollama is unavailable.

    This is a deterministic fallback that formats the best-matching
    training document(s) into a readable answer.
    """
    if not context_docs:
        return (
            "I wasn't able to find specific training materials related to your question "
            "in our knowledge base. Please try rephrasing your question, or "
            "consult the CBP Learning Portal or your Field Training Officer for "
            "additional guidance."
        )

    top = context_docs[0]
    score = top.get('score', 0)

    # If best match has very low relevance, say so
    if score < 0.05:
        return (
            "I found some training materials, but they may not directly address "
            "your question. Here's the closest match:\n\n"
            f"**{top.get('title', '')}**\n"
            f"{top.get('content', '')}\n\n"
            f"*Module:* {top.get('module', 'N/A')}\n\n"
            "If this doesn't answer your question, please consult your supervisor "
            "or the CBP Learning Portal for more specific guidance."
        )

    # Good match – format a proper answer
    parts = []
    parts.append(f"Based on our CBP training materials, here's the relevant information:\n")
    parts.append(f"**{top.get('title', '')}** (Category: {top.get('category', 'N/A')})\n")
    parts.append(f"{top.get('content', '')}\n")

    if top.get('module'):
        parts.append(f"\n*Training Module:* {top['module']}\n")

    # Include additional relevant docs if available
    additional = [d for d in context_docs[1:] if d.get('score', 0) > 0.1]
    if additional:
        parts.append("\n**Related Training Topics:**")
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
        client = get_ollama_client()
        response = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You are the CBP Training Assistant, an AI-powered learning companion '
                        'for U.S. Customs and Border Protection personnel. You help trainees '
                        'understand CBP policies, procedures, regulations, and best practices. '
                        'Provide accurate, professional responses that emphasize proper procedures '
                        'and compliance. Be educational and supportive in your tone.'
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
