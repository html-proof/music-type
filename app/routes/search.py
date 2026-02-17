from fastapi import APIRouter, Query
from typing import Optional
from app.services import saavn_service

router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Type: songs, albums, artists, playlists"),
    page: int = Query(0, description="Page number"),
    limit: int = Query(10, description="Results per page"),
):
    """
    Search for music content.

    - No type → global search (all types)
    - type=songs → song-specific search
    - type=albums → album-specific search
    - type=artists → artist-specific search
    """
    if type == "songs":
        result = await saavn_service.search_songs(q, page=page, limit=limit)
    elif type == "albums":
        result = await saavn_service.search_albums(q, page=page, limit=limit)
    elif type == "artists":
        result = await saavn_service.search_artists(q, page=page, limit=limit)
    else:
        result = await saavn_service.global_search(q)

    if result:
        return result

    return {"success": False, "message": "No results found"}
