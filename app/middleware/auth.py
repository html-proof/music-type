from fastapi import Header, HTTPException, Depends
from firebase_admin import auth as firebase_auth
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def verify_firebase_token(
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    FastAPI dependency that verifies a Firebase ID token.

    Expects header: Authorization: Bearer <id_token>
    Returns the decoded token claims (uid, email, name, picture, etc.)
    Raises HTTP 401 if invalid or missing.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use 'Bearer <token>'")

    token = parts[1]

    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def optional_firebase_token(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """
    Optional auth — returns decoded token if present, None otherwise.
    Use for endpoints that work for both anonymous and authenticated users.
    """
    if not authorization:
        return None

    try:
        return await verify_firebase_token(authorization)
    except HTTPException:
        return None
