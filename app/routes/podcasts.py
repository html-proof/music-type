from fastapi import APIRouter, Query
from typing import Optional
from app.services import saavn_service

router = APIRouter()


@router.get("/podcasts")
async def get_podcasts(
    q: str = Query("latest", description="Search query for podcasts"),
    page: int = Query(0),
    limit: int = Query(10),
):
    """
    Get podcast episodes.
    """
    result = await saavn_service.search_podcasts(q, page=page, limit=limit)
    
    if result and result.get("success"):
        data = result.get("data", {})
        results = data.get("results", [])
        
        # Enrich results with download URLs for playback
        data["results"] = await saavn_service.enrich_songs(results)
        return result

    return {"success": False, "message": "No podcasts found"}
