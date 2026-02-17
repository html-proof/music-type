from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

# ── Languages ───────────────────────────────────────────────────────────────

@router.get("/languages", response_model=List[Dict[str, str]])
async def get_languages():
    """Get list of available languages."""
    return [
        {"name": "Hindi", "icon": "🇮🇳"},
        {"name": "English", "icon": "🇬🇧"},
        {"name": "Punjabi", "icon": "🎵"},
        {"name": "Tamil", "icon": "🎶"},
        {"name": "Telugu", "icon": "🎼"},
        {"name": "Bengali", "icon": "🎹"},
        {"name": "Marathi", "icon": "🎸"},
        {"name": "Kannada", "icon": "🎺"},
        {"name": "Malayalam", "icon": "🎻"},
        {"name": "Gujarati", "icon": "🪕"},
        {"name": "Bhojpuri", "icon": "🥁"},
        {"name": "Korean", "icon": "🇰🇷"},
        {"name": "Japanese", "icon": "🇯🇵"},
        {"name": "Spanish", "icon": "🇪🇸"},
    ]


# ── Artists ─────────────────────────────────────────────────────────────────

@router.get("/artists", response_model=List[str])
async def get_featured_artists():
    """Get list of featured/popular artists."""
    return [
        "Arijit Singh",
        "Shreya Ghoshal",
        "Atif Aslam",
        "Neha Kakkar",
        "Jubin Nautiyal",
        "AR Rahman",
        "Honey Singh",
        "Badshah",
        "Armaan Malik",
        "Darshan Raval",
        "Sid Sriram",
        "Diljit Dosanjh",
        "Guru Randhawa",
        "Imagine Dragons",
        "Ed Sheeran",
        "Taylor Swift",
        "The Weeknd",
        "BTS",
        "Drake",
        "Billie Eilish",
        "Dua Lipa",
        "Coldplay",
        "Eminem",
        "Justin Bieber",
    ]
