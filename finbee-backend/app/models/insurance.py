"""
Insurance schema. Backed by the `insurance` collection. One document per policy.
"""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel

InsuranceType = Literal["health", "life", "termLife", "vehicle", "home", "travel", "other"]
PremiumFrequency = Literal["monthly", "quarterly", "halfYearly", "yearly"]


class InsuranceBase(BaseModel):
    insuranceType: InsuranceType
    provider: str
    coverageAmount: float
    premiumAmount: float
    premiumFrequency: PremiumFrequency
    policyStartDate: date
    policyEndDate: date


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceUpdate(BaseModel):
    insuranceType: Optional[InsuranceType] = None
    provider: Optional[str] = None
    coverageAmount: Optional[float] = None
    premiumAmount: Optional[float] = None
    premiumFrequency: Optional[PremiumFrequency] = None
    policyStartDate: Optional[date] = None
    policyEndDate: Optional[date] = None


class InsuranceOut(InsuranceBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None