"""
Planning endpoints:
- GET /planning/planner-types — static list of available planners and their fields
- GET /planning/goals/{goal_id}/roadmap — computed roadmap for a specific goal (not stored)
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.services.planning import list_planner_types, get_roadmap
from app.services.goals import get_goal

router = APIRouter()


@router.get("/planner-types")
async def get_planner_types():
    return list_planner_types()


@router.get("/goals/{goal_id}/roadmap")
async def get_goal_roadmap(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = str(current_user["_id"])
    goal = await get_goal(user_id, goal_id)
    return await get_roadmap(goal, user_id)