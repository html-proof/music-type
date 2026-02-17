from fastapi import APIRouter, Depends
from app.middleware.auth import verify_firebase_token
from app.services import firebase_service
from app.models.user import UserPreferences

router = APIRouter()


@router.get("/preferences")
async def get_preferences(
    user: dict = Depends(verify_firebase_token),
):
    """Get user preferences (language, artists)."""
    uid = user["uid"]
    prefs = firebase_service.get_preferences(uid)
    return {"success": True, "data": prefs or {"language": None, "artists": []}}


@router.post("/preferences")
async def save_preferences(
    data: UserPreferences,
    user: dict = Depends(verify_firebase_token),
):
    """Save user preferences (language, artists)."""
    uid = user["uid"]
    success = firebase_service.save_preferences(uid, data.model_dump())
    return {"success": success}


@router.get("/profile")
async def get_profile(
    user: dict = Depends(verify_firebase_token),
):
    """Get user profile."""
    uid = user["uid"]
    profile = firebase_service.get_profile(uid)
    return {"success": True, "data": profile}


@router.put("/profile")
async def update_profile(
    data: dict,
    user: dict = Depends(verify_firebase_token),
):
    """Update user profile."""
    uid = user["uid"]
    success = firebase_service.save_profile(uid, data)
    return {"success": success}
