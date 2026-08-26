"""
Auth business logic:
- verify_google_token(): validates a Google ID token and extracts the user's profile.
- login_or_create_user(): finds an existing user by googleId, or creates a new one.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.database import users_collection


def verify_google_token(google_id_token: str) -> dict:
    """
    Verifies the ID token sent by the frontend after Google Sign-In.
    Returns the decoded profile: email, name, google 'sub' (unique user id).
    """
    try:
        payload = id_token.verify_oauth2_token(
            google_id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    return {
        "email": payload["email"],
        "name": payload.get("name", payload["email"]),
        "googleId": payload["sub"],
    }


async def login_or_create_user(google_profile: dict) -> dict:
    """
    Looks up the user by googleId. Creates a new user document on first login.
    Returns the full user document (including _id) either way.
    """
    existing = await users_collection.find_one({"googleId": google_profile["googleId"]})
    if existing:
        return existing

    new_user = {
        "email": google_profile["email"],
        "name": google_profile["name"],
        "googleId": google_profile["googleId"],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": None,
    }
    result = await users_collection.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    return new_user