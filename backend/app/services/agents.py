from app.services.llm_hybrid import generate_answer
from app.services.llm_stub import compose_answer
import logging
from typing import List

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def process(self, *args, **kwargs):
        raise NotImplementedError

class PlannerAgent(Agent):
    def __init__(self):
        super().__init__("Planner", "Determines the intent of the user message")

    def process(self, message: str) -> str:
        try:
            # First try some simple keyword matching to avoid LLM call for simple stuff
            lowered = message.lower()
            if lowered.strip() in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
                return "greeting"
            if "lead" in lowered or "demo" in lowered or "pricing" in lowered:
                return "lead_capture"
            if "email" in lowered or "crm" in lowered or "calendar" in lowered:
                return "automation"

            # Simulate a quick intent classification LLM call.
            # Real LLM integration could be placed here if Ollama supported it reliably.
            # We will default to QA.
            return "qa"

        except Exception as e:
            logger.error(f"PlannerAgent error: {e}")
            return "qa"

class ExecutorAgent(Agent):
    def __init__(self):
        super().__init__("Executor", "Generates the response or action based on intent")

    def process(self, intent: str, question: str, sources: List[dict]) -> dict:
        try:
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

            # Use generate_answer which already falls back to compose_answer if LLM fails
            reply = generate_answer(question, sources)
            return {
                "reply": reply,
                "lead_hint": None,
            }
        except Exception as e:
            logger.error(f"ExecutorAgent error: {e}")
            return {
                "reply": compose_answer(question, sources), # Absolute fallback
                "lead_hint": None,
            }

class CriticAgent(Agent):
    def __init__(self):
        super().__init__("Critic", "Validates the executor's response against guidelines")

    def process(self, reply: str, sources: List[dict]) -> str:
        try:
            # 1. Hallucination check
            if "Context used" in reply and not sources:
                return (
                    "I am missing the supporting documents to answer that. "
                    "Please upload relevant files so I can respond accurately."
                )

            # 2. Add validation to ensure response isn't empty
            if not reply or not reply.strip():
                return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."

            return reply
        except Exception as e:
            logger.error(f"CriticAgent error: {e}")
            return reply


# Instantiate global agents
planner = PlannerAgent()
executor = ExecutorAgent()
critic = CriticAgent()

def plan_intent(message: str) -> str:
    return planner.process(message)

def execute_plan(intent: str, question: str, sources: List[dict]) -> dict:
    return executor.process(intent, question, sources)

def validate_response(reply: str, sources: List[dict]) -> str:
    return critic.process(reply, sources)
