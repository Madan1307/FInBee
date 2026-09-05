"""
Insurance business logic — full CRUD, always scoped to the requesting user.
"""

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.database import insurance_collection


def _to_object_id(insurance_id: str) -> ObjectId:
    try:
        return ObjectId(insurance_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid insurance id")


async def list_insurance(user_id: str) -> list[dict]:
    cursor = insurance_collection.find({"userId": user_id})
    return [doc async for doc in cursor]


async def create_insurance(user_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    data["userId"] = user_id
    data["createdAt"] = now
    data["updatedAt"] = None

    result = await insurance_collection.insert_one(data)
    return await insurance_collection.find_one({"_id": result.inserted_id})


async def get_insurance(user_id: str, insurance_id: str) -> dict:
    oid = _to_object_id(insurance_id)
    policy = await insurance_collection.find_one({"_id": oid, "userId": user_id})
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
    return policy


async def update_insurance(user_id: str, insurance_id: str, data: dict) -> dict:
    oid = _to_object_id(insurance_id)
    existing = await insurance_collection.find_one({"_id": oid, "userId": user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")

    data["updatedAt"] = datetime.now(timezone.utc)
    await insurance_collection.update_one({"_id": oid}, {"$set": data})
    return await insurance_collection.find_one({"_id": oid})


async def delete_insurance(user_id: str, insurance_id: str) -> None:
    oid = _to_object_id(insurance_id)
    result = await insurance_collection.delete_one({"_id": oid, "userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")