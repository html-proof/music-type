import firebase_admin
from firebase_admin import credentials, db as rtdb
import logging

logger = logging.getLogger(__name__)

_firebase_app = None


def initialize_firebase() -> bool:
    """Initialize Firebase Admin SDK. Returns True on success."""
    global _firebase_app

    if _firebase_app:
        return True

    from app.config import settings

    creds = settings.firebase_credentials
    if not creds:
        logger.warning("No Firebase credentials available")
        return False

    try:
        cred = credentials.Certificate(creds)
        _firebase_app = firebase_admin.initialize_app(cred, {
            "databaseURL": settings.firebase_database_url,
        })
        logger.info("✅ Firebase Admin SDK initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase init failed: {e}")
        return False


def get_db_ref(path: str):
    """Get a Firebase Realtime Database reference."""
    return rtdb.reference(path)
