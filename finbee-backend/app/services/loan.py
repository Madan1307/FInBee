"""
Loan business logic — full CRUD, always scoped to the requesting user.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.database import loans_collection


def _to_object_id(loan_id: str) -> ObjectId:
    try:
        return ObjectId(loan_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid loan id")


async def list_loans(user_id: str) -> list[dict]:
    cursor = loans_collection.find({"userId": user_id})
    return [doc async for doc in cursor]


async def create_loan(user_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    data["userId"] = user_id
    data["createdAt"] = now
    data["updatedAt"] = None

    result = await loans_collection.insert_one(data)
    return await loans_collection.find_one({"_id": result.inserted_id})


async def get_loan(user_id: str, loan_id: str) -> dict:
    oid = _to_object_id(loan_id)
    loan = await loans_collection.find_one({"_id": oid, "userId": user_id})
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


async def update_loan(user_id: str, loan_id: str, data: dict) -> dict:
    oid = _to_object_id(loan_id)
    existing = await loans_collection.find_one({"_id": oid, "userId": user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

    data["updatedAt"] = datetime.now(timezone.utc)
    await loans_collection.update_one({"_id": oid}, {"$set": data})
    return await loans_collection.find_one({"_id": oid})


async def delete_loan(user_id: str, loan_id: str) -> None:
    oid = _to_object_id(loan_id)
    result = await loans_collection.delete_one({"_id": oid, "userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")