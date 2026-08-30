"""
Financial profile endpoints:
- GET /financial-profile — get the current user's profile
- PUT /financial-profile — create or update the current user's profile
"""

from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user
from app.models.financial_profile import FinancialProfileCreate, FinancialProfileOut
from app.services.financial_profile import get_profile, upsert_profile

router = APIRouter()


@router.get("", response_model=FinancialProfileOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    profile = await get_profile(str(current_user["_id"]))
    if not profile:
        raise HTTPException(status_code=404, detail="No financial profile found for this user")
    return profile


@router.put("", response_model=FinancialProfileOut)
async def update_my_profile(
    payload: FinancialProfileCreate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump()
    updated = await upsert_profile(str(current_user["_id"]), data)
    return updated