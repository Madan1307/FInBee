"""
Loan schema. Backed by the `loans` collection. One document per loan.
"""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel

LoanType = Literal["personal", "home", "vehicle", "education", "business", "creditCard", "other"]


class LoanBase(BaseModel):
    loanType: LoanType
    lender: str
    principalAmount: float
    outstandingAmount: float
    emiAmount: float
    interestRate: float
    tenure: int  # months
    startDate: date


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    loanType: Optional[LoanType] = None
    lender: Optional[str] = None
    principalAmount: Optional[float] = None
    outstandingAmount: Optional[float] = None
    emiAmount: Optional[float] = None
    interestRate: Optional[float] = None
    tenure: Optional[int] = None
    startDate: Optional[date] = None


class LoanOut(LoanBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None