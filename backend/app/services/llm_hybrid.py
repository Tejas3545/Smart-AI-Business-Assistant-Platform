from typing import List

import httpx

from app.core.config import settings
from app.services.llm_stub import compose_answer
from app.utils.retry import default_retry


def _build_prompt(question: str, sources: List[dict]) -> str:
    if not sources:
        return (
            "If the answer is not in the provided context, say you need more documents.\n\n"
            f"Question: {question}\n\nContext: (none)"
        )

    context = "\n".join(f"- {item['snippet']}" for item in sources[:4])
    return (
        "Answer using only the context. If it is missing, say you need more documents.\n\n"
        f"Question: {question}\n\nContext:\n{context}"
    )


@default_retry
def _call_ollama(prompt: str) -> str:
    url = f"{settings.ollama_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    return data.get("response", "").strip()


def generate_answer(question: str, sources: List[dict]) -> str:
    if not sources:
        return compose_answer(question, sources)

    prompt = _build_prompt(question, sources)

    try:
        local_reply = _call_ollama(prompt)
        if local_reply:
            return local_reply
    except Exception:
        local_reply = ""

    return compose_answer(question, sources)
