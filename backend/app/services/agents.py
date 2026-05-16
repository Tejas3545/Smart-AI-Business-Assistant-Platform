from app.services.llm_hybrid import generate_answer


def plan_intent(message: str) -> str:
    lowered = message.lower()
    if lowered.strip() in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
        return "greeting"
    if "lead" in lowered or "demo" in lowered or "pricing" in lowered:
        return "lead_capture"
    if "email" in lowered or "crm" in lowered or "calendar" in lowered:
        return "automation"
    return "qa"


def execute_plan(intent: str, question: str, sources: list[dict]) -> dict:
    if intent == "lead_capture":
        return {
            "reply": "I can help with that. Could you share your name, email, and company?",
            "lead_hint": "Collect lead details",
        }
    if intent == "greeting":
        return {
            "reply": "Hello! Share a question or upload a document so I can help.",
            "lead_hint": None,
        }
    if intent == "automation":
        return {
            "reply": "I can trigger an automation. Tell me which workflow to run: email_summary, crm_sync, or calendar_booking.",
            "lead_hint": None,
        }
    return {
        "reply": generate_answer(question, sources),
        "lead_hint": None,
    }


def validate_response(reply: str, sources: list[dict]) -> str:
    if "Context used" in reply and not sources:
        return (
            "I am missing the supporting documents to answer that. "
            "Please upload relevant files so I can respond accurately."
        )
    return reply
