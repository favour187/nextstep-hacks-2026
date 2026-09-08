from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Any
from app.features.sustainability.core import (
    ActionInstance,
    ImpactCategory,
    ImpactVector,
    Milestone,
    Reframe,
    Weights,
    assign_action_scores,
    compute_feasibility,
    reframe_goal,
    sum_impacts,
)
from app.features.sustainability.library import templates_for_category

@dataclass(slots=True)
class GeneratedPlan:
    reframe: Reframe
    category: ImpactCategory
    chosen: list[ActionInstance]
    feasibility: list[Any]
    milestones: list[Milestone]
    total_impact: ImpactVector
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reframe": self.reframe.to_dict(),
            "category": self.category.value,
            "chosen": [a.to_dict() for a in self.chosen],
            "feasibility": [f.to_dict() for f in self.feasibility],
            "milestones": [asdict(m) for m in self.milestones],
            "total_impact": self.total_impact.to_dict(),
            "explanation": self.explanation,
        }

_MAX_ACTIONS = 6
_MIN_ACTIONS = 4

def plan_for_goal(
    goal: str,
    *,
    weekly_effort_hours: float = 2.0,
    weekly_budget_usd: float = 10.0,
    horizon_days: int = 30,
    weights: Weights | None = None,
) -> GeneratedPlan:
    weight_obj = weights or Weights()
    reframe = reframe_goal(goal)
    category = reframe.category
    candidates = [ActionInstance(template=t) for t in templates_for_category(category)]
    scored = assign_action_scores(candidates, weight_obj, category=category)
    shortlist = scored[:_MAX_ACTIONS]
    if len(shortlist) < _MIN_ACTIONS:
        fallback = [
            ActionInstance(template=t)
            for t in templates_for_category(_neighbour(category))
        ]
        fallback = assign_action_scores(fallback, weight_obj)
        shortlist += fallback[: _MIN_ACTIONS - len(shortlist)]
    feasible = compute_feasibility(
        shortlist,
        weekly_effort_hours=weekly_effort_hours,
        weekly_budget_usd=weekly_budget_usd,
        horizon_days=horizon_days,
        category=category,
    )
    milestones = _build_milestones(shortlist, horizon_days)
    total = sum_impacts([a.impact for a in shortlist])
    explanation = (
        f"Your {category .value } goal got reframed into {len (shortlist )} concrete actions "
        f"(from the {len (candidates )} candidates in the {category .value } library). "
        f"We prioritised actions whose impact-per-effort is high, so your first move "
        f"is a low-friction step you can do this week: “{shortlist [0 ].template .title }”."
    )
    return GeneratedPlan(
        reframe=reframe,
        category=category,
        chosen=shortlist,
        feasibility=list(feasible),
        milestones=milestones,
        total_impact=total,
        explanation=explanation,
    )

def _neighbour(category: ImpactCategory) -> ImpactCategory:
    return {
        ImpactCategory.WASTE: ImpactCategory.CONSUMPTION,
        ImpactCategory.ENERGY: ImpactCategory.WATER,
        ImpactCategory.WATER: ImpactCategory.ENERGY,
        ImpactCategory.TRANSPORT: ImpactCategory.CONSUMPTION,
        ImpactCategory.FOOD: ImpactCategory.WASTE,
        ImpactCategory.CONSUMPTION: ImpactCategory.WASTE,
    }[category]

def _build_milestones(
    actions: list[ActionInstance], horizon_days: int
) -> list[Milestone]:
    if not actions:
        return []
    top = actions[0]
    steps = [
        Milestone(
            title=f"Learn one fact about {top .template .title .lower ()}",
            due_offset_days=2,
        ),
        Milestone(
            title=f"Do “{top .template .title }” once",
            due_offset_days=5,
        ),
    ]
    if len(actions) > 1:
        steps.append(
            Milestone(
                title=f"Add “{actions [1 ].template .title }” to your routine",
                due_offset_days=max(8, horizon_days // 3),
            )
        )
    if len(actions) > 2:
        steps.append(
            Milestone(
                title=f"Take stock: what changed after {max (10 ,horizon_days //2 )} days?",
                due_offset_days=max(10, horizon_days // 2),
            )
        )
    steps.append(
        Milestone(
            title=f"Review the full plan at day {horizon_days }",
            due_offset_days=horizon_days,
        )
    )
    return steps

def plan_manifest(plan: GeneratedPlan) -> dict[str, Any]:
    return {
        "reframe": plan.reframe.to_dict(),
        "category": plan.category.value,
        "chosen": [a.to_dict() for a in plan.chosen],
        "feasibility": [f.to_dict() for f in plan.feasibility],
        "milestones": [m.__dict__ for m in plan.milestones],
        "total_impact": plan.total_impact.to_dict(),
        "explanation": plan.explanation,
    }

def apply_checkin(
    plan: PlanEntity,
    action_ids: list[str],
    *,
    check_in_date: date | None = None,
) -> ImpactVector:
    day = check_in_date or date.today()
    matched = [a for a in plan.actions if a.action_id in action_ids]
    added = sum_impacts([a.impact for a in matched])
    pending = [m for m in plan.milestones if not m.done]
    if pending and pending[0].due_offset_days <= (day - plan.created_at).days:
        pending[0].done = True
    return added
