"""
Insurance endpoints — full CRUD, all scoped to the authenticated user.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.insurance import InsuranceCreate, InsuranceUpdate, InsuranceOut
from app.services.insurance import (
    list_insurance,
    create_insurance,
    get_insurance,
    update_insurance,
    delete_insurance,
)

router = APIRouter()


def _serialize(policy: dict) -> dict:
    policy["id"] = str(policy["_id"])
    return policy


@router.get("", response_model=list[InsuranceOut])
async def get_all_insurance(current_user: dict = Depends(get_current_user)):
    policies = await list_insurance(str(current_user["_id"]))
    return [_serialize(p) for p in policies]


@router.post("", response_model=InsuranceOut)
async def add_insurance(
    payload: InsuranceCreate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json")
    policy = await create_insurance(str(current_user["_id"]), data)
    return _serialize(policy)


@router.get("/{insurance_id}", response_model=InsuranceOut)
async def get_single_insurance(
    insurance_id: str,
    current_user: dict = Depends(get_current_user),
):
    policy = await get_insurance(str(current_user["_id"]), insurance_id)
    return _serialize(policy)


@router.put("/{insurance_id}", response_model=InsuranceOut)
async def edit_insurance(
    insurance_id: str,
    payload: InsuranceUpdate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json", exclude_none=True)
    policy = await update_insurance(str(current_user["_id"]), insurance_id, data)
    return _serialize(policy)


@router.delete("/{insurance_id}", status_code=204)
async def remove_insurance(
    insurance_id: str,
    current_user: dict = Depends(get_current_user),
):
    await delete_insurance(str(current_user["_id"]), insurance_id)