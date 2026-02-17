from pydantic import BaseModel
from typing import Optional


class ImageQuality(BaseModel):
    quality: str
    url: str


class ArtistInfo(BaseModel):
    id: str
    name: str
    role: Optional[str] = None
    type: Optional[str] = None
    image: list[ImageQuality] = []
    url: Optional[str] = None


class AlbumInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None


class Song(BaseModel):
    id: str
    name: str
    type: Optional[str] = "song"
    year: Optional[str] = None
    release_date: Optional[str] = None
    duration: Optional[int] = None
    label: Optional[str] = None
    explicit_content: bool = False
    play_count: Optional[int] = None
    language: Optional[str] = None
    has_lyrics: bool = False
    lyrics_id: Optional[str] = None
    url: Optional[str] = None
    copyright: Optional[str] = None
    album: Optional[AlbumInfo] = None
    artists: Optional[dict] = None  # {primary: [], featured: [], all: []}
    image: list[ImageQuality] = []
    download_url: list[ImageQuality] = []

    class Config:
        populate_by_name = True


class SongSearchResult(BaseModel):
    total: int = 0
    start: int = 0
    results: list[Song] = []


class SearchResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
