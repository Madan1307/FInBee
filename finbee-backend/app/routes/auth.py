"""
Auth endpoints:
- POST /auth/google  — exchange a Google ID token for a FinBee JWT (login or signup)
- GET  /auth/me       — return the currently authenticated user
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.middleware.auth import create_access_token, get_current_user
from app.services.auth import verify_google_token, login_or_create_user

router = APIRouter()


class GoogleLoginRequest(BaseModel):
    id_token: str


@router.post("/google")
async def google_login(payload: GoogleLoginRequest):
    google_profile = verify_google_token(payload.id_token)
    user = await login_or_create_user(google_profile)

    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
        },
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "name": current_user["name"],
    }