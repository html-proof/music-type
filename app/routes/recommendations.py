from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.middleware.auth import optional_firebase_token
from app.services import recommendation_service

router = APIRouter()


@router.get("/recommendations")
async def get_recommendations(
    song_id: Optional[str] = Query(None, description="Base song ID for suggestions"),
    limit: int = Query(20, description="Number of recommendations"),
    user: Optional[dict] = Depends(optional_firebase_token),
):
    """
    Get song recommendations.

    Priority:
    1. song_id → similar songs from Saavn
    2. User preferences → artist + language based
    3. Trending fallback
    """
    uid = user.get("uid") if user else None
    result = await recommendation_service.get_recommendations(
        song_id=song_id, uid=uid, limit=limit
    )
    return result


@router.get("/recommendations/{song_id}")
async def get_recommendations_for_song(
    song_id: str,
    limit: int = Query(20),
    user: Optional[dict] = Depends(optional_firebase_token),
):
    """Get recommendations based on a specific song."""
    uid = user.get("uid") if user else None
    result = await recommendation_service.get_recommendations(
        song_id=song_id, uid=uid, limit=limit
    )
    return result
