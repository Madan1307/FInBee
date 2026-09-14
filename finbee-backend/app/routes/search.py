"""
Search endpoints — feature/service discovery via simple keyword matching.
"""

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import get_current_user
from app.services.search import match_query_to_features

router = APIRouter()


@router.get("")
async def search(
    q: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    results = match_query_to_features(q)
    return {"query": q, "results": results}