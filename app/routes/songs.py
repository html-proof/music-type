from fastapi import APIRouter
from app.services import saavn_service

router = APIRouter()


@router.get("/song/{song_id}")
async def get_song(song_id: str):
    """Get full song details by ID."""
    result = await saavn_service.get_song_by_id(song_id)
    if result:
        return result
    return {"success": False, "message": "Song not found"}


@router.get("/song/{song_id}/lyrics")
async def get_lyrics(song_id: str):
    """Get lyrics for a song."""
    result = await saavn_service.get_song_lyrics(song_id)
    if result:
        return result
    return {"success": False, "message": "Lyrics not found"}


@router.get("/song/{song_id}/suggestions")
async def get_suggestions(song_id: str):
    """Get similar songs / suggestions."""
    result = await saavn_service.get_song_suggestions(song_id)
    if result:
        return result
    return {"success": False, "message": "No suggestions found"}


@router.get("/album/{album_id}")
async def get_album(album_id: str):
    """Get album details and songs."""
    result = await saavn_service.get_album_by_id(album_id)
    if result and result.get("success"):
        data = result.get("data", {})
        if "songs" in data:
            data["songs"] = await saavn_service.enrich_songs(data["songs"])
        return result
    return {"success": False, "message": "Album not found"}


@router.get("/artist/{artist_id}")
async def get_artist(artist_id: str):
    """Get artist details."""
    result = await saavn_service.get_artist_by_id(artist_id)
    if result and result.get("success"):
        # Some detail responses might include top songs
        return result
    return {"success": False, "message": "Artist not found"}


@router.get("/artist/{artist_id}/songs")
async def get_artist_songs(artist_id: str, page: int = 0):
    """Get songs by a specific artist."""
    result = await saavn_service.get_artist_songs(artist_id, page=page)
    if result and result.get("success"):
        data = result.get("data", [])
        if isinstance(data, list):
            enriched = await saavn_service.enrich_songs(data)
            result["data"] = enriched
        return result
    return {"success": False, "message": "No songs found"}


@router.get("/playlist/{playlist_id}")
async def get_playlist(playlist_id: str):
    """Get playlist details and songs."""
    result = await saavn_service.get_playlist_by_id(playlist_id)
    if result and result.get("success"):
        data = result.get("data", {})
        if "songs" in data:
            data["songs"] = await saavn_service.enrich_songs(data["songs"])
        return result
    return {"success": False, "message": "Playlist not found"}
