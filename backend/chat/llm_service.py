import logging

from ollama import Client
from django.conf import settings

logger = logging.getLogger(__name__)

# Create Ollama client pointing to the configured (possibly remote) server
_ollama_client = None

# ---------------------------------------------------------------------------
# Gemma 4 Prompt Engineering
# ---------------------------------------------------------------------------
# References:
#   - https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4
#   - https://ai.google.dev/gemma/docs/core/model_card_4#best_practices
#
# Key principles applied:
#   1. Native system-role support  – Gemma 4 honours the `system` role natively.
#   2. Sampling parameters         – Model card recommends temp=1.0, top_p=0.95, top_k=64.
#   3. Thinking mode               – Activated via system instruction for reasoning tasks.
#   4. Clear separation            – System prompt defines *role & behaviour*;
#                                    user message carries *context + question* only.
#   5. Structured instructions     – Gemma 4 has exceptionally strong instruction-
#                                    following; explicit formatting directives yield
#                                    better results.
# ---------------------------------------------------------------------------

# Gemma 4 recommended sampling parameters (from model card)
GEMMA4_OPTIONS = {
    'temperature': 1.0,
    'top_p': 0.95,
    'top_k': 64,
}

# System prompt – the single source of truth for the model's identity and behaviour.
# The <|think|> token is NOT embedded here; it is toggled per-request so that
# callers can opt into thinking mode without always paying the latency cost.
SYSTEM_PROMPT = (
    "You are the CBP Training Assistant, an AI-powered learning companion for "
    "U.S. Customs and Border Protection personnel.\n"
    "\n"
    "Role and Scope:\n"
    "- Help trainees understand CBP policies, procedures, regulations, and best practices.\n"
    "- Provide accurate, professional responses grounded in the training materials provided.\n"
    "- When training materials are relevant, cite the specific module title and category.\n"
    "- If the question falls outside the provided materials, state that clearly and "
    "recommend consulting the CBP Learning Portal or a Field Training Officer.\n"
    "\n"
    "Response Guidelines:\n"
    "- Be educational, clear, and thorough.\n"
    "- Emphasize proper procedures, safety, and compliance.\n"
    "- Structure longer answers with headings or numbered steps when appropriate.\n"
    "- Keep language professional but approachable.\n"
    "- Do not fabricate regulations or procedures that are not in the provided training materials.\n"
)

# Lightweight system prompt variant used for thinking mode.
# Appending the adaptive-thought-efficiency hint reduces thinking tokens by ~20%
# while preserving quality (see Gemma 4 prompt-formatting docs).
SYSTEM_PROMPT_THINKING = (
    SYSTEM_PROMPT
    + "\n"
    "Think step-by-step before answering. Be efficient in your reasoning — "
    "focus on the most relevant training material and reach a conclusion quickly."
)


def get_ollama_client():
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = Client(host=settings.OLLAMA_BASE_URL)
        logger.info('Ollama client configured for %s', settings.OLLAMA_BASE_URL)
    return _ollama_client


def _format_context(context_docs: list[dict]) -> str:
    """Format retrieved training documents into a clean context block."""
    if not context_docs:
        return "(No relevant training materials found.)"

    parts = []
    for i, doc in enumerate(context_docs, 1):
        title = doc.get('title', 'Untitled')
        category = doc.get('category', '')
        module = doc.get('module', '')
        content = doc.get('content', '')
        score = doc.get('score', 0)

        header = f"[Source {i}] {title}"
        if category:
            header += f" | Category: {category}"
        if module:
            header += f" | Module: {module}"
        header += f" (relevance: {score:.2f})"

        parts.append(f"{header}\n{content}")

    return "\n\n".join(parts)


def build_rag_prompt(query: str, context_docs: list[dict]) -> str:
    """Build the *user-turn* message containing context and the trainee's question.

    This intentionally does NOT repeat the assistant's role (that belongs in the
    system message).  Gemma 4 performs best when the user turn contains only the
    task-specific content.
    """
    context_text = _format_context(context_docs)

    prompt = (
        "Training materials retrieved from the CBP knowledge base:\n"
        "---\n"
        f"{context_text}\n"
        "---\n"
        "\n"
        f"Trainee question: {query}"
    )
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
    parts.append("Based on our CBP training materials, here's the relevant information:\n")
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


def generate_response(query: str, context_docs: list[dict], *, think: bool = False) -> str:
    """Generate a response using Ollama with RAG context.

    Args:
        query: The trainee's question.
        context_docs: Retrieved training documents from Qdrant.
        think: If True, enable Gemma 4 thinking mode for step-by-step reasoning.

    Falls back to a deterministic context-based response if Ollama
    is unavailable (e.g. insufficient memory in the container).
    """
    prompt = build_rag_prompt(query, context_docs)
    system = SYSTEM_PROMPT_THINKING if think else SYSTEM_PROMPT

    try:
        client = get_ollama_client()
        response = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt},
            ],
            options=GEMMA4_OPTIONS,
            think=think,
        )
        return response['message']['content']
    except Exception as e:
        logger.warning('Ollama unavailable (%s), using RAG-context fallback.', e)
        return _fallback_response(query, context_docs)
