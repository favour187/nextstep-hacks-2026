from __future__ import annotations
import json
import uuid
from datetime import date, datetime
from sqlalchemy import Uuid
from typing import Any
from sqlalchemy import DateTime, ForeignKey, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from app.core.db import Base, TimestampsMixin, UUIDMixin, iso_utc, utcnow


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)


def _json_loads(raw: str | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


class GoalEntity(UUIDMixin, TimestampsMixin, Base):
    __tablename__ = "sustainability_goals"
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    goal_text: Mapped[str] = mapped_column(Text)
    reframed_goal: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(32), default="waste")
    scope: Mapped[str] = mapped_column(String(32), default="personal")
    horizon_days: Mapped[int] = mapped_column(default=30)
    weekly_effort_hours: Mapped[float] = mapped_column(default=2.0)
    weekly_budget_usd: Mapped[float] = mapped_column(default=10.0)
    plan_json: Mapped[str] = mapped_column(Text, default="{}")
    impact_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(16), default="active")
    check_ins: Mapped[list["CheckInEntity"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )

    def plan(self) -> dict[str, Any]:
        return _json_loads(self.plan_json) or {}

    def impact(self) -> dict[str, float]:
        return _json_loads(self.impact_json) or {}

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan()
        return {
            "id": str(self.id),
            "goal_text": self.goal_text,
            "reframed_goal": self.reframed_goal,
            "category": self.category,
            "scope": self.scope,
            "horizon_days": self.horizon_days,
            "weekly_effort_hours": self.weekly_effort_hours,
            "weekly_budget_usd": self.weekly_budget_usd,
            "status": self.status,
            "plan": plan,
            "impact": self.impact(),
            "check_ins": [c.to_dict() for c in self.check_ins],
            "created_at": iso_utc(self.created_at),
        }


class CheckInEntity(UUIDMixin, Base):
    __tablename__ = "sustainability_check_ins"
    goal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("sustainability_goals.id"), index=True
    )
    check_in_date: Mapped[date] = mapped_column(default=date.today)
    action_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[str] = mapped_column(Text, default="")
    feeling_score: Mapped[int] = mapped_column(default=3)
    recorded_at: Mapped[datetime] = mapped_column(default=utcnow)
    goal: Mapped[GoalEntity] = relationship(back_populates="check_ins")

    @property
    def action_ids(self) -> list[str]:
        return _json_loads(self.action_ids_json) or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "date": self.check_in_date.isoformat(),
            "action_ids": self.action_ids,
            "notes": self.notes,
            "feeling_score": self.feeling_score,
        }


def create_goal(db: Session, user_id: str, data: dict[str, Any]) -> GoalEntity:
    goal = GoalEntity(
        user_id=user_id,
        goal_text=data["goal_text"],
        reframed_goal=data["reframed_goal"],
        category=data.get("category", "waste"),
        scope=data.get("scope", "personal"),
        horizon_days=int(data.get("horizon_days", 30)),
        weekly_effort_hours=float(data.get("weekly_effort_hours", 2.0)),
        weekly_budget_usd=float(data.get("weekly_budget_usd", 10.0)),
        plan_json=_json_dumps(data.get("plan", {})),
        impact_json=_json_dumps(data.get("impact", {})),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goal(db: Session, goal_id: str, user_id: str) -> GoalEntity | None:
    return db.scalar(
        select(GoalEntity).where(
            GoalEntity.id == uuid.UUID(goal_id), GoalEntity.user_id == user_id
        )
    )


def list_goals(db: Session, user_id: str) -> list[GoalEntity]:
    stmt = (
        select(GoalEntity)
        .where(GoalEntity.user_id == user_id)
        .order_by(GoalEntity.created_at.desc())
    )
    return list(db.scalars(stmt))


def update_goal_impact(db: Session, goal: GoalEntity, impact: dict[str, float]) -> None:
    goal.impact_json = _json_dumps(impact)
    db.commit()


def add_check_in(
    db: Session,
    goal: GoalEntity,
    action_ids: list[str],
    *,
    notes: str = "",
    feeling_score: int = 3,
    check_in_date: date | None = None,
) -> CheckInEntity:
    record = CheckInEntity(
        goal_id=goal.id,
        check_in_date=check_in_date or date.today(),
        action_ids_json=_json_dumps(action_ids),
        notes=notes,
        feeling_score=feeling_score,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
