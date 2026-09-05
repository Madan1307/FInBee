"""
Intelligence endpoints — read-only, deterministic financial insights.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.services.intelligence import get_intelligence_overview

router = APIRouter()


@router.get("/overview")
async def get_overview(current_user: dict = Depends(get_current_user)):
    return await get_intelligence_overview(str(current_user["_id"]))

