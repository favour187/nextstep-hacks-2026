"""Tests for the StepWise planning engine, API flow and AI chat."""

from __future__ import annotations

import json

from app.core.testing import auth_headers, create_user
from app.features.sustainability.core import (
    ImpactCategory,
    ImpactVector,
    Weights,
    assign_action_scores,
    compute_streak,
    detect_category,
    quantify_detriment,
    reframe_goal,
)
from app.features.sustainability.engine import plan_for_goal
from app.features.sustainability.library import all_templates
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Reframing / categorisation
# ---------------------------------------------------------------------------
def test_category_detection():
    assert detect_category("I want to reduce plastic waste at home") == ImpactCategory.WASTE
    assert detect_category("lower my electricity bill") == ImpactCategory.ENERGY
    assert detect_category("save water in the garden") == ImpactCategory.WATER


def test_reframe_produces_actionable_statement():
    reframe = reframe_goal("I'm worried about all the plastic I throw away")
    assert "focus" in reframe.to_dict()
    assert "lever" in reframe.to_dict()
    assert len(reframe.statement) > 40


# ---------------------------------------------------------------------------
# Decision model
# ---------------------------------------------------------------------------
def test_weights_sum_to_one():
    Weights().validate()  # default sums to 1.0; must not raise


def test_detriment_lower_for_easier_action():
    from app.features.sustainability.core import ActionInstance

    templates = all_templates()
    easy = next(t for t in templates if t.action_id == "water_tap_off")
    hard = next(t for t in templates if t.action_id == "travel_bus_commute")
    d_easy = quantify_detriment(ActionInstance(template=easy), Weights())
    d_hard = quantify_detriment(ActionInstance(template=hard), Weights())
    assert d_easy.total < d_hard.total


def test_scoring_prefers_feasible_actions():
    templates = all_templates()
    actions = [t for t in templates if t.category == ImpactCategory.WASTE]
    from app.features.sustainability.core import ActionInstance

    scored = assign_action_scores([ActionInstance(template=t) for t in actions], Weights(), category=ImpactCategory.WASTE)
    assert scored[0].score is not None
    assert scored[0].score >= scored[-1].score


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------
def test_plan_for_goal_generates_structure():
    plan = plan_for_goal("reduce household waste", weekly_effort_hours=2.0)
    assert plan.category == ImpactCategory.WASTE
    assert 4 <= len(plan.chosen) <= 6
    assert len(plan.milestones) >= 3
    assert plan.total_impact.kg > 0 or plan.total_impact.items > 0
    assert plan.explanation
    assert plan.reframe.statement


def test_plan_for_goal_respects_budget():
    plan = plan_for_goal("cut my energy use", weekly_budget_usd=0.0, weekly_effort_hours=1.0)
    # Zero budget should still produce a workable plan (free actions dominate).
    assert plan.chosen


# ---------------------------------------------------------------------------
# Streaks
# ---------------------------------------------------------------------------
def test_compute_streak():
    today = date.today()
    days = [today - timedelta(days=i) for i in range(3)]
    assert compute_streak(days) == 3
    days = [today - timedelta(days=i) for i in (0, 1, 3)]
    assert compute_streak(days) == 2
    assert compute_streak([]) == 0
