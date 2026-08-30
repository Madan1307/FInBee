"""
Financial profile schema — the user's reusable financial information.
Backed by the `financial_profiles` collection. One document per user.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Income(BaseModel):
    primary: float
    secondary: float = 0
    frequency: Literal["monthly", "yearly"]


class Dependent(BaseModel):
    relationship: str
    age: int


class FinancialProfileBase(BaseModel):
    income: Income
    expenses: float
    savings: float
    assets: float = 0
    riskProfile: Literal["low", "medium", "high"]
    maritalStatus: str
    dependents: list[Dependent] = []


class FinancialProfileCreate(FinancialProfileBase):
    pass


class FinancialProfileUpdate(BaseModel):
    """All optional — supports partial updates."""
    income: Optional[Income] = None
    expenses: Optional[float] = None
    savings: Optional[float] = None
    assets: Optional[float] = None
    riskProfile: Optional[Literal["low", "medium", "high"]] = None
    maritalStatus: Optional[str] = None
    dependents: Optional[list[Dependent]] = None


class FinancialProfileOut(FinancialProfileBase):
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None