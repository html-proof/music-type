import logging
import time
from typing import Optional
from app.firebase.firebase_init import get_db_ref

logger = logging.getLogger(__name__)


# ── User Profile ────────────────────────────────────────────────────────────

def save_profile(uid: str, data: dict) -> bool:
    """Save or update user profile."""
    try:
        ref = get_db_ref(f"users/{uid}/profile")
        ref.set(data)
        return True
    except Exception as e:
        logger.error(f"Error saving profile for {uid}: {e}")
        return False


def get_profile(uid: str) -> Optional[dict]:
    """Get user profile."""
    try:
        ref = get_db_ref(f"users/{uid}/profile")
        return ref.get()
    except Exception as e:
        logger.error(f"Error getting profile for {uid}: {e}")
        return None


# ── User Preferences ───────────────────────────────────────────────────────

def save_preferences(uid: str, data: dict) -> bool:
    """Save user preferences (language, artists)."""
    try:
        ref = get_db_ref(f"users/{uid}/preferences")
        ref.set(data)
        return True
    except Exception as e:
        logger.error(f"Error saving preferences for {uid}: {e}")
        return False


def get_preferences(uid: str) -> Optional[dict]:
    """Get user preferences."""
    try:
        ref = get_db_ref(f"users/{uid}/preferences")
        return ref.get()
    except Exception as e:
        logger.error(f"Error getting preferences for {uid}: {e}")
        return None


# ── Activity: History ───────────────────────────────────────────────────────

def save_history(uid: str, song_id: str, data: dict) -> bool:
    """Save a song to play history."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/history/{song_id}")
        data["playedAt"] = data.get("playedAt", int(time.time() * 1000))
        ref.set(data)
        return True
    except Exception as e:
        logger.error(f"Error saving history: {e}")
        return False


def get_history(uid: str, limit: int = 50) -> Optional[dict]:
    """Get play history."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/history")
        return ref.order_by_child("playedAt").limit_to_last(limit).get()
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return None


# ── Activity: Skipped ───────────────────────────────────────────────────────

def save_skipped(uid: str, song_id: str, data: dict) -> bool:
    """Save a skipped song."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/skipped/{song_id}")
        data["skippedAt"] = data.get("skippedAt", int(time.time() * 1000))
        ref.set(data)
        return True
    except Exception as e:
        logger.error(f"Error saving skipped: {e}")
        return False


# ── Activity: Search History ────────────────────────────────────────────────

def save_search(uid: str, data: dict) -> bool:
    """Save a search query."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/searches")
        data["timestamp"] = data.get("timestamp", int(time.time() * 1000))
        ref.push(data)
        return True
    except Exception as e:
        logger.error(f"Error saving search: {e}")
        return False


def get_searches(uid: str, limit: int = 20) -> Optional[dict]:
    """Get search history."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/searches")
        return ref.order_by_child("timestamp").limit_to_last(limit).get()
    except Exception as e:
        logger.error(f"Error getting searches: {e}")
        return None


# ── Activity: Current Playing ───────────────────────────────────────────────

def save_current_playing(uid: str, data: dict) -> bool:
    """Save currently playing song."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/currentPlaying")
        ref.set(data)
        return True
    except Exception as e:
        logger.error(f"Error saving current playing: {e}")
        return False


def get_current_playing(uid: str) -> Optional[dict]:
    """Get currently playing song."""
    try:
        ref = get_db_ref(f"users/{uid}/activity/currentPlaying")
        return ref.get()
    except Exception as e:
        logger.error(f"Error getting current playing: {e}")
        return None
