"""
Investment schema. Backed by the `investments` collection. One document per investment.
"""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel

InvestmentType = Literal[
    "stocks", "mutualFund", "fixedDeposit", "recurringDeposit",
    "bonds", "etf", "gold", "realEstate", "ppf", "nps", "other"
]


class InvestmentBase(BaseModel):
    investmentType: InvestmentType
    amountInvested: float
    currentValue: float
    startDate: date
    goalId: Optional[str] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentUpdate(BaseModel):
    investmentType: Optional[InvestmentType] = None
    amountInvested: Optional[float] = None
    currentValue: Optional[float] = None
    startDate: Optional[date] = None
    goalId: Optional[str] = None


class InvestmentOut(InvestmentBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None