"""
Financial profile business logic.
- get_profile(): fetch the current user's profile.
- upsert_profile(): create or update (one profile per user).
- normalize_income(): converts {primary, secondary, frequency} into a
  single monthly figure — used by Intelligence/Decisions later so they
  don't have to care whether the user entered monthly or yearly numbers.
"""

from datetime import datetime, timezone
from typing import Optional

from app.database import financial_profiles_collection


async def get_profile(user_id: str) -> Optional[dict]:
    return await financial_profiles_collection.find_one({"userId": user_id})


async def upsert_profile(user_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    existing = await financial_profiles_collection.find_one({"userId": user_id})

    if existing:
        data["updatedAt"] = now
        await financial_profiles_collection.update_one(
            {"userId": user_id},
            {"$set": data},
        )
    else:
        data["userId"] = user_id
        data["createdAt"] = now
        data["updatedAt"] = None
        await financial_profiles_collection.insert_one(data)

    return await financial_profiles_collection.find_one({"userId": user_id})


def normalize_income(income: dict) -> float:
    """
    Converts an income dict {primary, secondary, frequency} into a
    single monthly total, regardless of whether it was entered as
    monthly or yearly.
    """
    total = income.get("primary", 0) + income.get("secondary", 0)
    frequency = income.get("frequency", "monthly")

    if frequency == "yearly":
        return total / 12
    return total  # already monthly