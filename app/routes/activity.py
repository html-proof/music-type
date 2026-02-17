from fastapi import APIRouter, Depends
from app.middleware.auth import verify_firebase_token
from app.services import firebase_service
from app.models.user import ActivityHistory, ActivitySkipped, ActivitySearch, CurrentPlaying

router = APIRouter()


@router.post("/activity/history")
async def save_history(
    data: ActivityHistory,
    user: dict = Depends(verify_firebase_token),
):
    """Save a song to play history."""
    uid = user["uid"]
    success = firebase_service.save_history(uid, data.song_id, data.model_dump())
    return {"success": success}


@router.get("/activity/history")
async def get_history(
    user: dict = Depends(verify_firebase_token),
    limit: int = 50,
):
    """Get user's play history."""
    uid = user["uid"]
    history = firebase_service.get_history(uid, limit=limit)
    return {"success": True, "data": history or {}}


@router.post("/activity/skipped")
async def save_skipped(
    data: ActivitySkipped,
    user: dict = Depends(verify_firebase_token),
):
    """Save a skipped song."""
    uid = user["uid"]
    success = firebase_service.save_skipped(uid, data.song_id, data.model_dump())
    return {"success": success}


@router.post("/activity/search")
async def save_search(
    data: ActivitySearch,
    user: dict = Depends(verify_firebase_token),
):
    """Save a search query."""
    uid = user["uid"]
    success = firebase_service.save_search(uid, data.model_dump())
    return {"success": success}


@router.get("/activity/search")
async def get_searches(
    user: dict = Depends(verify_firebase_token),
    limit: int = 20,
):
    """Get user's search history."""
    uid = user["uid"]
    searches = firebase_service.get_searches(uid, limit=limit)
    return {"success": True, "data": searches or {}}


@router.post("/activity/current")
async def save_current(
    data: CurrentPlaying,
    user: dict = Depends(verify_firebase_token),
):
    """Save currently playing song."""
    uid = user["uid"]
    success = firebase_service.save_current_playing(uid, data.model_dump())
    return {"success": success}


@router.get("/activity/current")
async def get_current(
    user: dict = Depends(verify_firebase_token),
):
    """Get currently playing song."""
    uid = user["uid"]
    current = firebase_service.get_current_playing(uid)
    return {"success": True, "data": current}
