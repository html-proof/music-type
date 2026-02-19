from fastapi import APIRouter, Query
from typing import Optional
from app.services import saavn_service

router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Type: songs, albums, artists, playlists"),
    language: Optional[str] = Query(None, description="Filter by language"),
    page: int = Query(0, description="Page number"),
    limit: int = Query(20, description="Results per page"),
):
    """
    Search for music content.
    """
    if type == "songs":
        result = await saavn_service.search_songs(q, page=page, limit=limit)
        # Apply language filter if provided and search results exist
        if result and result.get("success"):
            data = result.get("data", {})
            results = data.get("results", [])
            
            if language:
                results = [
                    s for s in results 
                    if s.get("language", "").lower() == language.lower()
                ]
            
            # Enrich results with download URLs
            data["results"] = await saavn_service.enrich_songs(results)
            
    elif type == "albums":
        result = await saavn_service.search_albums(q, page=page, limit=limit)
    elif type == "artists":
        result = await saavn_service.search_artists(q, page=page, limit=limit)
    else:
        result = await saavn_service.global_search(q, language=language, limit=limit)

    if result:
        return result

    return {"success": False, "message": "No results found"}


