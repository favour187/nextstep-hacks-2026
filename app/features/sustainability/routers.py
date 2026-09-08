from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.auth import User, get_current_user
from app.core.db import get_db
from app.core.errors import NotFoundError, ValidationFailedError
from app.features.sustainability import service

router = APIRouter(prefix="/sustainability", tags=["sustainability"])

class CreateGoalIn(BaseModel):
    goal_text: str = Field(min_length=4, max_length=400)
    weekly_effort_hours: float = Field(default=2.0, ge=0, le=40)
    weekly_budget_usd: float = Field(default=10.0, ge=0, le=500)
    horizon_days: int = Field(default=30, ge=7, le=90)

class CheckInIn(BaseModel):
    action_ids: list[str] = Field(min_length=1)
    notes: str = Field(default="", max_length=500)
    feeling_score: int = Field(default=3, ge=1, le=5)
    check_in_date: str | None = None

class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=800)
    goal_id: str | None = None

@router.post("/goals", status_code=201)
def create_goal(
    payload: CreateGoalIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return service.create_plan_for_user(db, str(user.id), payload.model_dump())
    except ValueError as exc:
        raise ValidationFailedError(str(exc)) from exc

@router.get("/goals")
def list_goals(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return {"goals": service.list_for_user(db, str(user.id))}

@router.get("/goals/{goal_id}")
def get_goal(
    goal_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    goal = service.get_goal_for_user(db, str(user.id), goal_id)
    if goal is None:
        raise NotFoundError("Plan not found.")
    return goal.to_dict()

@router.post("/goals/{goal_id}/check-ins", status_code=201)
def check_in(
    goal_id: str,
    payload: CheckInIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    goal = service.get_goal_for_user(db, str(user.id), goal_id)
    if goal is None:
        raise NotFoundError("Plan not found.")
    try:
        return service.record_check_in(
            db,
            goal,
            payload.action_ids,
            notes=payload.notes,
            feeling_score=payload.feeling_score,
            check_in_date=payload.check_in_date,
        )
    except ValueError as exc:
        raise ValidationFailedError(str(exc)) from exc

@router.post("/chat")
def chat(
    payload: ChatIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    goal = None
    if payload.goal_id:
        goal = service.get_goal_for_user(db, str(user.id), payload.goal_id)
        if goal is None:
            raise NotFoundError("Plan not found.")
    return service.chat(db, payload.message, goal)
