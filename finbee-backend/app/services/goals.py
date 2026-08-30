"""
Goals business logic — full CRUD, always scoped to the requesting user.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.database import goals_collection


def _to_object_id(goal_id: str) -> ObjectId:
    try:
        return ObjectId(goal_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid goal id")


async def list_goals(user_id: str, goal_type: Optional[str] = None) -> list[dict]:
    query = {"userId": user_id}
    if goal_type:
        query["goalType"] = goal_type

    cursor = goals_collection.find(query)
    return [doc async for doc in cursor]


async def create_goal(user_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    data["userId"] = user_id
    data["createdAt"] = now
    data["updatedAt"] = None

    result = await goals_collection.insert_one(data)
    return await goals_collection.find_one({"_id": result.inserted_id})


async def get_goal(user_id: str, goal_id: str) -> dict:
    oid = _to_object_id(goal_id)
    goal = await goals_collection.find_one({"_id": oid, "userId": user_id})
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


async def update_goal(user_id: str, goal_id: str, data: dict) -> dict:
    oid = _to_object_id(goal_id)
    existing = await goals_collection.find_one({"_id": oid, "userId": user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    data["updatedAt"] = datetime.now(timezone.utc)
    await goals_collection.update_one({"_id": oid}, {"$set": data})
    return await goals_collection.find_one({"_id": oid})


async def delete_goal(user_id: str, goal_id: str) -> None:
    oid = _to_object_id(goal_id)
    result = await goals_collection.delete_one({"_id": oid, "userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")