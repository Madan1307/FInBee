"""
Decision request/response schemas. Decisions are computed on demand —
nothing here is persisted to MongoDB.
"""

from typing import Optional, Literal
from pydantic import BaseModel

DecisionType = Literal["purchase", "loan", "investment"]
BurdenLevel = Literal["low", "moderate", "high", "veryHigh", "unavailable"]


class DecisionRequest(BaseModel):
    decisionType: DecisionType
    description: Optional[str] = None
    amount: float                       # total cost of the purchase/investment
    downPayment: float = 0
    newLoanAmount: float = 0            # 0 if no financing involved
    newEmiAmount: float = 0             # monthly EMI this decision would add
    interestRate: Optional[float] = None
    tenure: Optional[int] = None        # months


class DecisionResult(BaseModel):
    assessment: BurdenLevel
    financialImpact: dict
    reasons: list[str]
    recommendations: list[str]