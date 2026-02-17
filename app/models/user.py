from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    photo_url: Optional[str] = None


class UserPreferences(BaseModel):
    language: Optional[str] = None
    artists: list[str] = []


class ActivityHistory(BaseModel):
    song_id: str
    song_name: Optional[str] = None
    artist: Optional[str] = None
    played_at: Optional[str] = None
    duration: Optional[int] = None


class ActivitySkipped(BaseModel):
    song_id: str
    song_name: Optional[str] = None
    skipped_at: Optional[str] = None


class ActivitySearch(BaseModel):
    query: str
    timestamp: Optional[str] = None


class CurrentPlaying(BaseModel):
    song_id: str
    song_name: Optional[str] = None
    artist: Optional[str] = None
    position: Optional[int] = 0
