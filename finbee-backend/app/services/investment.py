"""
Investment business logic — full CRUD, always scoped to the requesting user.
"""

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.database import investments_collection


def _to_object_id(investment_id: str) -> ObjectId:
    try:
        return ObjectId(investment_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid investment id")


async def list_investments(user_id: str) -> list[dict]:
    cursor = investments_collection.find({"userId": user_id})
    return [doc async for doc in cursor]


async def create_investment(user_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    data["userId"] = user_id
    data["createdAt"] = now
    data["updatedAt"] = None

    result = await investments_collection.insert_one(data)
    return await investments_collection.find_one({"_id": result.inserted_id})


async def get_investment(user_id: str, investment_id: str) -> dict:
    oid = _to_object_id(investment_id)
    investment = await investments_collection.find_one({"_id": oid, "userId": user_id})
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")
    return investment


async def update_investment(user_id: str, investment_id: str, data: dict) -> dict:
    oid = _to_object_id(investment_id)
    existing = await investments_collection.find_one({"_id": oid, "userId": user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    data["updatedAt"] = datetime.now(timezone.utc)
    await investments_collection.update_one({"_id": oid}, {"$set": data})
    return await investments_collection.find_one({"_id": oid})


async def delete_investment(user_id: str, investment_id: str) -> None:
    oid = _to_object_id(investment_id)
    result = await investments_collection.delete_one({"_id": oid, "userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")