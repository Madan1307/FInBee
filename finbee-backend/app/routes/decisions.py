"""
Decision endpoints — computed on demand, nothing persisted:
- POST /decisions/evaluate — assess a proposed financial decision
- POST /decisions/what-if — re-run the same assessment with adjusted inputs
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.decision import DecisionRequest, DecisionResult
from app.services.decisions import build_decision_result

router = APIRouter()


@router.post("/evaluate", response_model=DecisionResult)
async def evaluate_decision(
    payload: DecisionRequest,
    current_user: dict = Depends(get_current_user),
):
    decision = payload.model_dump()
    result = await build_decision_result(str(current_user["_id"]), decision)
    return result


@router.post("/what-if", response_model=DecisionResult)
async def what_if_decision(
    payload: DecisionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Same logic as /evaluate — the frontend calls this with adjusted
    values (e.g. higher down payment) to show the updated outcome."""
    decision = payload.model_dump()
    result = await build_decision_result(str(current_user["_id"]), decision)
    return result

