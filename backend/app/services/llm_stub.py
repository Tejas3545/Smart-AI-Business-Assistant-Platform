from typing import List


def _summarize_snippet(text: str, max_chars: int = 240) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3] + "..."


def compose_answer(question: str, sources: List[dict]) -> str:
    if not sources:
        return (
            "I do not have enough document context to answer that yet. "
            "Please upload the relevant business documents or provide more details."
        )

    key_points = []
    for item in sources[:3]:
        key_points.append(_summarize_snippet(item["snippet"]))

    bullets = "\n".join(f"- {point}" for point in key_points)

    return (
        "Grounded response (based on your documents):\n\n"
        f"Question: {question}\n\n"
        "Key points:\n"
        f"{bullets}\n\n"
        "If you want a follow-up email or action plan, tell me the audience and tone."
    )
