"""StepWise application service: orchestrates engine + persistence for the API.

Kept free of request/response concerns so it can be tested directly.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ai import AIGateway, get_gateway
from app.core.db import iso_utc
from app.features.sustainability import ai_skills
from app.features.sustainability.core import ImpactVector, compute_streak, sum_impacts
from app.features.sustainability.engine import GeneratedPlan, plan_for_goal
from app.features.sustainability.repository import (
    CheckInEntity,
    GoalEntity,
    add_check_in,
    create_goal,
    get_goal,
    list_goals,
    update_goal_impact,
)


def _impact_to_dict(vec: ImpactVector) -> dict[str, float]:
    return vec.to_dict()


def create_plan_for_user(db: Session, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run the deterministic planner, persist it, and return the API shape."""
    goal_text = str(payload.get("goal_text", "")).strip()
    if len(goal_text) < 4:
        raise ValueError("goal_text must be at least 4 characters")

    plan: GeneratedPlan = plan_for_goal(
        goal_text,
        weekly_effort_hours=float(payload.get("weekly_effort_hours", 2.0)),
        weekly_budget_usd=float(payload.get("weekly_budget_usd", 10.0)),
        horizon_days=int(payload.get("horizon_days", 30)),
    )
    data = plan.to_dict()
    goal = create_goal(
        db,
        user_id,
        {
            "goal_text": goal_text,
            "reframed_goal": plan.reframe.statement,
            "category": plan.category.value,
            "scope": "personal",
            "horizon_days": int(payload.get("horizon_days", 30)),
            "weekly_effort_hours": float(payload.get("weekly_effort_hours", 2.0)),
            "weekly_budget_usd": float(payload.get("weekly_budget_usd", 10.0)),
            "plan": data,
            "impact": plan.total_impact.to_dict(),
        },
    )
    return goal.to_dict()


def get_goal_for_user(db: Session, user_id: str, goal_id: str) -> GoalEntity | None:
    return get_goal(db, goal_id, user_id)


def list_for_user(db: Session, user_id: str) -> list[dict[str, Any]]:
    return [g.to_dict() for g in list_goals(db, user_id)]


def record_check_in(
    db: Session,
    goal: GoalEntity,
    action_ids: list[str],
    *,
    notes: str = "",
    feeling_score: int = 3,
    check_in_date: str | None = None,
) -> dict[str, Any]:
    """Log a check-in and update the running impact totals."""
    day = date.fromisoformat(check_in_date) if check_in_date else date.today()
    plan = goal.plan()
    actions = plan.get("chosen", [])
    known_ids = {a["action_id"] for a in actions}
    valid = [aid for aid in action_ids if aid in known_ids]
    if not valid:
        raise ValueError("No valid action_ids provided for this goal")

    record = add_check_in(
        db, goal, valid, notes=notes, feeling_score=feeling_score, check_in_date=day
    )
    # Recompute impact fresh from the DB (the relationship cache is stale).
    fresh_check_ins = list(
        db.scalars(
            select(CheckInEntity)
            .where(CheckInEntity.goal_id == goal.id)
            .order_by(CheckInEntity.check_in_date)
        )
    )
    by_id = {a["action_id"]: a for a in actions}
    totals = ImpactVector()
    for check in fresh_check_ins:
        for aid in check.action_ids:
            if aid in by_id:
                entry = by_id[aid]
                totals = totals + ImpactVector(
                    **{
                        k: float(entry.get("impact", {}).get(k, 0.0))
                        for k in ("kg", "co2e_kg", "kwh", "litres", "kg_food", "items")
                    }
                )
    update_goal_impact(db, goal, totals.to_dict())

    # Streak uses the same fresh records.
    streak = compute_streak([c.check_in_date for c in fresh_check_ins])
    return {
        "check_in": record.to_dict(),
        "impact": totals.to_dict(),
        "streak": streak,
    }


def plan_streak(db: Session, goal: GoalEntity) -> int:
    return compute_streak(list(goal.check_ins))


def chat(db: Session, message: str, goal: GoalEntity | None, gateway: AIGateway | None = None) -> dict[str, Any]:
    """AI chat: deterministic local skills when no key; LLM when configured."""
    gateway = gateway or get_gateway()
    summary = goal.to_dict() if goal is not None else None
    result = gateway.chat(
        system=ai_skills.SYSTEM_PROMPT,
        user=message,
        max_tokens=420,
    )
    return {
        "reply": result.text,
        "provider": result.provider,
        "used_fallback": result.used_fallback,
        "cached": result.cached,
    }
