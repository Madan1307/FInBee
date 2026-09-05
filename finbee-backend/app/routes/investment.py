"""
Investment endpoints — full CRUD, all scoped to the authenticated user.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.investment import InvestmentCreate, InvestmentUpdate, InvestmentOut
from app.services.investment import (
    list_investments,
    create_investment,
    get_investment,
    update_investment,
    delete_investment,
)

router = APIRouter()


def _serialize(investment: dict) -> dict:
    investment["id"] = str(investment["_id"])
    return investment


@router.get("", response_model=list[InvestmentOut])
async def get_investments(current_user: dict = Depends(get_current_user)):
    investments = await list_investments(str(current_user["_id"]))
    return [_serialize(i) for i in investments]


@router.post("", response_model=InvestmentOut)
async def add_investment(
    payload: InvestmentCreate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json")
    investment = await create_investment(str(current_user["_id"]), data)
    return _serialize(investment)


@router.get("/{investment_id}", response_model=InvestmentOut)
async def get_single_investment(
    investment_id: str,
    current_user: dict = Depends(get_current_user),
):
    investment = await get_investment(str(current_user["_id"]), investment_id)
    return _serialize(investment)


@router.put("/{investment_id}", response_model=InvestmentOut)
async def edit_investment(
    investment_id: str,
    payload: InvestmentUpdate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json", exclude_none=True)
    investment = await update_investment(str(current_user["_id"]), investment_id, data)
    return _serialize(investment)


@router.delete("/{investment_id}", status_code=204)
async def remove_investment(
    investment_id: str,
    current_user: dict = Depends(get_current_user),
):
    await delete_investment(str(current_user["_id"]), investment_id)