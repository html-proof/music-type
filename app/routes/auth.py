from fastapi import APIRouter, Depends
from app.middleware.auth import verify_firebase_token
from app.services import firebase_service
from app.models.user import UserProfile

router = APIRouter()


@router.post("/verify-token")
async def verify_token(user: dict = Depends(verify_firebase_token)):
    """Verify Firebase ID token and return user claims."""
    uid = user.get("uid")

    # Auto-save profile on first login
    profile = firebase_service.get_profile(uid)
    if not profile:
        firebase_service.save_profile(uid, {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "photoUrl": user.get("picture", ""),
        })

    return {
        "success": True,
        "uid": uid,
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }
