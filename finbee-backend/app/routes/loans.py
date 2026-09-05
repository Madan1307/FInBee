"""
Loan endpoints — full CRUD, all scoped to the authenticated user.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.loan import LoanCreate, LoanUpdate, LoanOut
from app.services.loan import (
    list_loans,
    create_loan,
    get_loan,
    update_loan,
    delete_loan,
)

router = APIRouter()


def _serialize(loan: dict) -> dict:
    loan["id"] = str(loan["_id"])
    return loan


@router.get("", response_model=list[LoanOut])
async def get_loans(current_user: dict = Depends(get_current_user)):
    loans = await list_loans(str(current_user["_id"]))
    return [_serialize(l) for l in loans]


@router.post("", response_model=LoanOut)
async def add_loan(
    payload: LoanCreate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json")
    loan = await create_loan(str(current_user["_id"]), data)
    return _serialize(loan)


@router.get("/{loan_id}", response_model=LoanOut)
async def get_single_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
):
    loan = await get_loan(str(current_user["_id"]), loan_id)
    return _serialize(loan)


@router.put("/{loan_id}", response_model=LoanOut)
async def edit_loan(
    loan_id: str,
    payload: LoanUpdate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json", exclude_none=True)
    loan = await update_loan(str(current_user["_id"]), loan_id, data)
    return _serialize(loan)


@router.delete("/{loan_id}", status_code=204)
async def remove_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
):
    await delete_loan(str(current_user["_id"]), loan_id)