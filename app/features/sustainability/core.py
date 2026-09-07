from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any


class ImpactCategory(StrEnum):
    WASTE = "waste"
    ENERGY = "energy"
    WATER = "water"
    TRANSPORT = "transport"
    FOOD = "food"
    CONSUMPTION = "consumption"


class FrictionKind(StrEnum):
    COST = "cost"
    TIME = "time"
    EFFORT = "effort"
    KNOWLEDGE = "knowledge"
    HABIT = "habit"
    ACCESS = "access"


UNIT_KEYS = ("kg", "co2e_kg", "kwh", "litres", "kg_food", "items")


@dataclass(frozen=True, slots=True)
class ImpactVector:
    kg: float = 0.0
    co2e_kg: float = 0.0
    kwh: float = 0.0
    litres: float = 0.0
    kg_food: float = 0.0
    items: float = 0.0

    def __add__(self, other: "ImpactVector") -> "ImpactVector":
        return ImpactVector(
            **{k: getattr(self, k) + getattr(other, k) for k in UNIT_KEYS}
        )

    def __mul__(self, factor: float) -> "ImpactVector":
        return ImpactVector(**{k: getattr(self, k) * factor for k in UNIT_KEYS})

    __rmul__ = __mul__

    def to_dict(self) -> dict[str, float]:
        return {k: round(getattr(self, k), 3) for k in UNIT_KEYS}

    @property
    def is_positive(self) -> bool:
        return any(getattr(self, k) > 0 for k in UNIT_KEYS)


def sum_impacts(vectors: list[ImpactVector]) -> ImpactVector:
    total = ImpactVector()
    for v in vectors:
        total = total + v
    return total


@dataclass(frozen=True, slots=True)
class ActionTemplate:
    action_id: str
    title: str
    category: ImpactCategory
    impact: ImpactVector
    execution_unit: str
    baseline_effort: int
    cost_usd: float
    duration_minutes: float
    needs_learning: bool
    setup_minutes: float = 0.0
    description: str = ""


@dataclass(frozen=True, slots=True)
class Weights:
    impact: float = 0.35
    effort: float = 0.25
    cost: float = 0.15
    time: float = 0.10
    habit: float = 0.10
    learning: float = 0.05

    def validate(self) -> None:
        total = (
            self.impact
            + self.effort
            + self.cost
            + self.time
            + self.habit
            + self.learning
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0 (got {total })")


@dataclass(slots=True)
class ActionInstance:
    template: ActionTemplate
    chosen_by: str = "line"
    score: float | None = None
    note: str | None = None

    @property
    def impact(self) -> ImpactVector:
        return self.template.impact

    @property
    def action_id(self) -> str:
        return self.template.action_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.template.action_id,
            "title": self.template.title,
            "category": self.template.category.value,
            "impact": self.template.impact.to_dict(),
            "execution_unit": self.template.execution_unit,
            "baseline_effort": self.template.baseline_effort,
            "cost_usd": self.template.cost_usd,
            "duration_minutes": self.template.duration_minutes,
            "needs_learning": self.template.needs_learning,
            "chosen_by": self.chosen_by,
            "score": self.score,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class Detriment:
    benefit: float
    effort: float
    cost: float
    time: float
    habit: float
    learning: float
    total: float

    def to_dict(self) -> dict[str, float]:
        return {
            "benefit": round(self.benefit, 4),
            "effort": round(self.effort, 4),
            "cost": round(self.cost, 4),
            "time": round(self.time, 4),
            "habit": round(self.habit, 4),
            "learning": round(self.learning, 4),
            "total": round(self.total, 4),
        }


def _log_scale(value: float, reference: float = 8.0) -> float:
    if value <= 0:
        return 0.0
    import math

    return min(1.0, math.log1p(value) / math.log1p(reference))


def quantify_detriment(action: ActionInstance, weights: Weights) -> Detriment:
    t = action.template
    magnitude = (
        t.impact.kg
        + t.impact.co2e_kg
        + t.impact.kwh
        + t.impact.litres
        + t.impact.kg_food
        + t.impact.items
    )
    benefit = _log_scale(magnitude)
    effort = min(1.0, t.baseline_effort / 10.0)
    cost = min(1.0, t.cost_usd / 50.0)
    time = min(1.0, t.duration_minutes / 60.0)
    habit = min(1.0, (t.baseline_effort + t.duration_minutes / 30.0) / 14.0)
    learning = 1.0 if t.needs_learning else 0.0
    total = (
        weights.effort * effort
        + weights.cost * cost
        + weights.time * time
        + weights.habit * habit
        + weights.learning * learning
    )
    return Detriment(
        benefit=benefit,
        effort=effort,
        cost=cost,
        time=time,
        habit=habit,
        learning=learning,
        total=total,
    )


def assign_action_scores(
    actions: list[ActionInstance],
    weights: Weights,
    *,
    category: ImpactCategory | None = None,
) -> list[ActionInstance]:
    weights.validate()
    for action in actions:
        detriment = quantify_detriment(action, weights)
        match = (
            1.0 if category is None or action.template.category == category else 0.72
        )
        action.score = round(
            match * (1.0 - detriment.total) * (0.7 + 0.3 * detriment.benefit), 4
        )
    return sorted(actions, key=lambda a: a.score or 0.0, reverse=True)


@dataclass(frozen=True, slots=True)
class FeasibleGroup:
    name: str
    actions: tuple[ActionInstance, ...]
    multiplier: float
    total_effort_score: float
    total_cost_usd: float
    total_schedule_minutes: float
    impact: ImpactVector

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "actions": [a.to_dict() for a in self.actions],
            "multiplier": self.multiplier,
            "total_effort_score": round(self.total_effort_score, 1),
            "total_cost_usd": round(self.total_cost_usd, 2),
            "total_schedule_minutes": round(self.total_schedule_minutes, 1),
            "impact": self.impact.to_dict(),
        }


def compute_feasibility(
    actions: list[ActionInstance],
    *,
    weekly_effort_hours: float,
    weekly_budget_usd: float,
    horizon_days: int = 30,
    category: ImpactCategory | None = None,
) -> list[FeasibleGroup]:
    minutes_per_week = max(0.0, weekly_effort_hours) * 60.0
    budget = max(0.0, weekly_budget_usd)
    weeks = max(1, horizon_days / 7.0)
    grouped: dict[str, list[ActionInstance]] = {}
    for action in actions:
        key = action.template.category.value
        grouped.setdefault(key, []).append(action)
    result: list[FeasibleGroup] = []
    for key, members in grouped.items():
        total_min = sum(a.template.duration_minutes for a in members)
        total_cost = sum(a.template.cost_usd for a in members)
        min_based = 0.0
        if total_min > 0:
            min_based = (minutes_per_week * weeks) / total_min
        cost_based = (budget * weeks) / total_cost if total_cost > 0 else float("inf")
        multiplier = max(1.0, min(min_based, cost_based))
        multiplier = min(multiplier, 90.0)
        multiplier = float(int(multiplier))
        impact = sum_impacts([m.impact * multiplier for m in members])
        effort = sum(m.template.baseline_effort for m in members) / max(1, len(members))
        result.append(
            FeasibleGroup(
                name=ImpactCategory(key).value,
                actions=tuple(members),
                multiplier=multiplier,
                total_effort_score=round(effort, 1),
                total_cost_usd=total_cost * multiplier,
                total_schedule_minutes=total_min * multiplier,
                impact=impact,
            )
        )
    return result


@dataclass(slots=True)
class Milestone:
    title: str
    due_offset_days: int
    done: bool = False
    note: str = ""


@dataclass(slots=True)
class PlanEntity:
    goal: str
    reframed_goal: str
    category: ImpactCategory
    scope: str
    horizon_days: int = 30
    weekly_effort_hours: float = 2.0
    weekly_budget_usd: float = 10.0
    actions: list[ActionInstance] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    created_at: date = field(default_factory=date.today)

    def pick_top(self, k: int, weights: Weights | None = None) -> list[ActionInstance]:
        scored = assign_action_scores(
            self.actions, weights or Weights(), category=self.category
        )
        return scored[:k]

    def overview(self, weights: Weights | None = None) -> dict[str, Any]:
        weight_obj = weights or Weights()
        full = assign_action_scores(self.actions, weight_obj, category=self.category)
        recommended = [a for a in full if a.score and a.score >= 0.6]
        next_action = recommended[0] if recommended else (full[0] if full else None)

        def _effort_level(score: float) -> str:
            if score >= 0.78:
                return "very-easy"
            if score >= 0.62:
                return "easy"
            if score >= 0.5:
                return "moderate"
            return "challenging"

        return {
            "goal": self.goal,
            "reframed_goal": self.reframed_goal,
            "category": self.category.value,
            "scope": self.scope,
            "horizon_days": self.horizon_days,
            "weekly_hours_committed": self.weekly_effort_hours,
            "weekly_budget_usd": self.weekly_budget_usd,
            "milestone_count": len(self.milestones),
            "milestones_done": sum(1 for m in self.milestones if m.done),
            "next_action": next_action.to_dict() if next_action else None,
            "recommended_count": len(recommended),
            "suggested_effort": _effort_level(next_action.score or 0.0),
        }

    def total_impact(self) -> ImpactVector:
        return sum_impacts([a.impact for a in self.actions if a.impact.is_positive])


@dataclass(slots=True)
class CheckInRecord:
    date: date
    action_ids: list[str]
    notes: str = ""
    feeling_score: int = 3


def compute_streak(dates: list[date] | list[CheckInRecord]) -> int:
    raw: list[date] = [d if isinstance(d, date) else d.date for d in dates]
    days = set(raw)
    streak = 0
    cursor = date.today()
    if cursor not in days:
        cursor -= timedelta(days=1)
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


@dataclass(frozen=True, slots=True)
class Reframe:
    statement: str
    focus: str
    lever: str
    category: ImpactCategory
    confidence: float = 0.8

    def to_dict(self) -> dict[str, str | float]:
        return {
            "statement": self.statement,
            "focus": self.focus,
            "lever": self.lever,
            "category": self.category.value,
            "confidence": self.confidence,
        }


def detect_category(text: str) -> ImpactCategory:
    t = text.lower()
    rules: list[tuple[ImpactCategory, tuple[str, ...]]] = [
        (
            ImpactCategory.WASTE,
            (
                "waste",
                "trash",
                "garbage",
                "recycl",
                "landfill",
                "plastic",
                "packaging",
                "compost",
                "single-use",
                "litter",
                "zero-waste",
            ),
        ),
        (
            ImpactCategory.ENERGY,
            (
                "energy",
                "electric",
                "electricity",
                "power",
                "kwh",
                "solar",
                "heating",
                "cooling",
                "utility bill",
                "led",
            ),
        ),
        (
            ImpactCategory.WATER,
            (
                "water",
                "shower",
                "tap",
                "drought",
                "bath",
                "leak",
                "garden watering",
                "lawn",
            ),
        ),
        (
            ImpactCategory.TRANSPORT,
            (
                "drive",
                "car",
                "commute",
                "transport",
                "flight",
                "train",
                "fuel",
                "gasoline",
                "petrol",
                "bike",
                "walk",
            ),
        ),
        (
            ImpactCategory.FOOD,
            (
                "food",
                "eat",
                "meal",
                "diet",
                "meat",
                "vegetarian",
                "vegan",
                "grocer",
                "leftover",
                "hunger",
            ),
        ),
        (
            ImpactCategory.CONSUMPTION,
            (
                "buy",
                "purchase",
                "shopping",
                "clothing",
                "fast fashion",
                "electronics",
                "stuff",
                "things",
                "possessions",
            ),
        ),
    ]
    scored: list[tuple[int, ImpactCategory]] = []
    for category, keywords in rules:
        score = sum(1 for kw in keywords if kw in t)
        if score:
            scored.append((score, category))
    if not scored:
        return ImpactCategory.WASTE
    scored.sort(reverse=True)
    return scored[0][1]


def reframe_goal(goal: str) -> Reframe:
    category = detect_category(goal)
    focus = {
        ImpactCategory.WASTE: "the items and packaging you choose day to day",
        ImpactCategory.ENERGY: "the energy you use at home day to day",
        ImpactCategory.WATER: "the water you use at home day to day",
        ImpactCategory.TRANSPORT: "how you move around week to week",
        ImpactCategory.FOOD: "what you buy and eat week to week",
        ImpactCategory.CONSUMPTION: "what you choose to buy, and how long you keep it",
    }[category]
    lever = {
        ImpactCategory.WASTE: "reducing what ends up in the bin",
        ImpactCategory.ENERGY: "cutting wasted kilowatt-hours",
        ImpactCategory.WATER: "cutting wasted litres",
        ImpactCategory.TRANSPORT: "shifting trips to lower-carbon modes",
        ImpactCategory.FOOD: "cutting waste and higher-impact foods",
        ImpactCategory.CONSUMPTION: "buying fewer, more durable things",
    }[category]
    return Reframe(
        statement=(
            f"Instead of worrying broadly about “{goal .strip ()[:80 ]}”, focus on one thing "
            f"you control: {focus }. Your lever is {lever } — measured as the totals on your "
            f"StepWise dashboard."
        ),
        focus=focus,
        lever=lever,
        category=category,
    )
