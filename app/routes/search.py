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
    limit: int = Query(10, description="Results per page"),
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
        result = await saavn_service.global_search(q, language=language)
        # Global search results are more complex, but we can filter the 'songs' inside them if language provided
        if result and result.get("success"):
            data = result.get("data", {})
            if "topQuery" in data and "results" in data["topQuery"]:
                # Filter
                top_results = data["topQuery"]["results"]
                if language:
                    top_results = [
                        s for s in top_results
                        if s.get("type") != "song" or s.get("language", "").lower() == language.lower()
                    ]
                # Enrich only songs
                data["topQuery"]["results"] = await saavn_service.enrich_songs(top_results)
                
            if "songs" in data and "results" in data["songs"]:
                song_results = data["songs"]["results"]
                if language:
                    song_results = [
                        s for s in song_results
                        if s.get("language", "").lower() == language.lower()
                    ]
                # Enrich
                data["songs"]["results"] = await saavn_service.enrich_songs(song_results)

    if result:
        return result

    return {"success": False, "message": "No results found"}
