"""
Goal schema — a single shared collection for all planner types.
Backed by the `goals` collection. Every planner submission is a new document.
"""

from datetime import datetime, date
from typing import Optional, Literal, Any
from pydantic import BaseModel


class GoalBase(BaseModel):
    goalType: Literal["vehicle", "house", "retirement", "education"]
    goalName: str
    targetAmount: float
    currentAmount: float = 0
    targetDate: date
    priority: Literal["low", "medium", "high"]
    goalSpecificData: dict[str, Any] = {}


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    """All optional — supports partial updates."""
    goalName: Optional[str] = None
    targetAmount: Optional[float] = None
    currentAmount: Optional[float] = None
    targetDate: Optional[date] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    goalSpecificData: Optional[dict[str, Any]] = None


class GoalOut(GoalBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None