"""
Goal endpoints — full CRUD, all scoped to the authenticated user.
"""

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import get_current_user
from app.models.goal import GoalCreate, GoalUpdate, GoalOut
from app.services.goals import (
    list_goals,
    create_goal,
    get_goal,
    update_goal,
    delete_goal,
)

router = APIRouter()


def _serialize(goal: dict) -> dict:
    """Mongo's _id -> string id, so it matches GoalOut."""
    goal["id"] = str(goal["_id"])
    return goal


@router.get("", response_model=list[GoalOut])
async def get_goals(
    goalType: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    goals = await list_goals(str(current_user["_id"]), goal_type=goalType)
    return [_serialize(g) for g in goals]


@router.post("", response_model=GoalOut)
async def add_goal(
    payload: GoalCreate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json")
    goal = await create_goal(str(current_user["_id"]), data)
    return _serialize(goal)


@router.get("/{goal_id}", response_model=GoalOut)
async def get_single_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    goal = await get_goal(str(current_user["_id"]), goal_id)
    return _serialize(goal)


@router.put("/{goal_id}", response_model=GoalOut)
async def edit_goal(
    goal_id: str,
    payload: GoalUpdate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(mode="json", exclude_none=True)
    goal = await update_goal(str(current_user["_id"]), goal_id, data)
    return _serialize(goal)


@router.delete("/{goal_id}", status_code=204)
async def remove_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    await delete_goal(str(current_user["_id"]), goal_id)