"""StepWise AI layer: deterministic skills that make the decision engine
conversational, plus optional LLM enrichment.

Skills are registered with the shared LocalDemoProvider so:
 - with no API key: the product is fully functional (deterministic answers),
 - with a key: the same prompts go to the remote LLM (richer, natural
   language) — but every returned payload also carries the deterministic
   numbers the engine computed, so the UI can always show real data.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.core.ai import AIMessage, AIProvider, LocalDemoProvider
from app.features.sustainability.core import ImpactVector


# ---------------------------------------------------------------------------
# Deterministic local skills
# ---------------------------------------------------------------------------
class AIExplainSkill:
    """Local explanation of a StepWise notion (no network needed)."""

    id = "explain"

    def can_handle(self, user_text: str, system: str) -> bool:
        return "explain" in user_text.lower() or "why" in user_text.lower()

    def respond(self, user_text: str, system: str, context: dict[str, Any] | None) -> str:
        topic = user_text.lower().split("explain")[-1].strip() or "a plan"
        return (
            f"Here's the idea behind “{topic[:60]}”: StepWise scores every candidate "
            f"action with a weighted decision model (impact vs. effort, cost, time, habit "
            f"and learning). It then shows you the LOWEST-friction step first, because "
            f"behaviour science shows that small consistent actions beat big intentions. "
            f"Do you want me to lay out your top 3 candidate actions?"
        )


class AIPlanSkill:
    """Local: turn a plain-English goal into a structured action list."""

    id = "plan"

    def can_handle(self, user_text: str, system: str) -> bool:
        lowered = user_text.lower()
        return any(k in lowered for k in ("plan", "goal", "reduce", "less", "want to"))

    def respond(self, user_text: str, system: str, context: dict[str, Any] | None) -> str:
        return json.dumps(
            {
                "kind": "plan",
                "goal": user_text,
                "actions": [
                    {"title": "Line your bin with a bag; rinse out recyclables", "impact_kg": 0.15},
                    {"title": "Start a kitchen compost collection", "impact_kg": 0.35},
                    {"title": "Plan meals and shop with a list", "impact_kg": 0.2},
                ],
                "nudge": "The first step is the one that removes the most friction.",
            },
            indent=None,
        )


class AITipSkill:
    """Local: short, useful coaching tip."""

    id = "tip"

    def can_handle(self, user_text: str, system: str) -> bool:
        return "tip" in user_text.lower() or "stuck" in user_text.lower()

    def respond(self, user_text: str, system: str, context: dict[str, Any] | None) -> str:
        return (
            "StepWise tip: don't try to change everything at once. Commit to ONE "
            "two-minute action per day (e.g. turning the tap off while brushing) — "
            "consistency compounds, and the dashboard will show it within a week."
        )


class AIReviewSkill:
    """Local: reflect on a check-in with a short supportive note."""

    id = "review"

    def can_handle(self, user_text: str, system: str) -> bool:
        return "review" in user_text.lower() or "check in" in user_text.lower()

    def respond(self, user_text: str, system: str, context: dict[str, Any] | None) -> str:
        return (
            "Nice work — logging a check-in is how the plan turns into a habit. "
            "The curve on your dashboard will start bending this week; the step "
            "that matters most is the one you can repeat tomorrow."
        )


def local_provider() -> AIProvider:
    return LocalDemoProvider([AIExplainSkill(), AIPlanSkill(), AITipSkill(), AIReviewSkill()])


# ---------------------------------------------------------------------------
# LLM prompt builders (used when a remote key IS configured)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are StepWise, a kind, concise sustainability coach for a hackathon demo. "
    "You help people turn vague environmental concerns into specific, easy, "
    "measurable next steps. Use plain language. Never invent numbers; if you quote "
    "an impact, call it an estimate. If the user asks for an explanation, explain "
    "the decision model (impact vs effort, cost, time, habit, learning). Keep "
    "answers under 120 words unless asked for more."
)


def build_messages(user_text: str, plan_summary: dict[str, Any] | None = None) -> list[AIMessage]:
    context = ""
    if plan_summary:
        context = (
            "\n\nCurrent plan for this user (JSON):\n"
            + json.dumps(plan_summary, default=str)[:2000]
        )
    return [
        AIMessage(role="system", content=SYSTEM_PROMPT),
        AIMessage(role="user", content=user_text + context),
    ]


def parse_payload(text: str) -> dict[str, Any]:
    """Try to wrap raw LLM output into the envelope the API always returns.

    Falls back to a plain {'reply': ...} shape so the UI can always render.
    """
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {"reply": data.get("reply", text), "raw": data, "parsed": True}
    except json.JSONDecodeError:
        pass
    return {"reply": text, "raw": None, "parsed": False}
