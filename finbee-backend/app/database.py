"""
MongoDB Atlas connection (async, via Motor).
Exposes a single `db` object the rest of the app imports.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]

# Finalized collections — do not add new ones without a real persistence need.
users_collection = db["users"]
financial_profiles_collection = db["financial_profiles"]
goals_collection = db["goals"]
loans_collection = db["loans"]
insurance_collection = db["insurance"]
investments_collection = db["investments"]

async def ping_database() -> bool:
    """Used by the health-check endpoint to confirm Atlas connectivity."""
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False