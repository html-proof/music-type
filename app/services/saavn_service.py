import httpx
import logging
import asyncio
from typing import Optional, List, Dict
from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.saavn_api_base_url


async def _get(endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
    """Make an async GET request to the Saavn API."""
    url = f"{BASE_URL}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Upstream error from Saavn API: {response.status_code} for {url}. Result: {response.text[:200]}")
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout calling Saavn API: {url}")
        return None
    except httpx.HTTPStatusError as e:
        # Already logged status code above
        return None
    except Exception as e:
        logger.error(f"Saavn API error: {e}")
        return None


# ── Search ──────────────────────────────────────────────────────────────────

async def global_search(query: str, language: Optional[str] = None, limit: int = 20) -> Optional[dict]:
    """Global search: songs, albums, artists, playlists."""
    params = {"query": query, "limit": limit}
    if language:
        params["language"] = language
    
    # Launch Global Search and dedicated Song Search in parallel
    global_task = _get("/api/search", params=params)
    songs_task = search_songs(query, page=0, limit=limit)
    
    results = await asyncio.gather(global_task, songs_task, return_exceptions=True)
    
    global_result = results[0]
    songs_result = results[1]
    
    # Determine the base result from global search
    final_result = None
    if not isinstance(global_result, Exception) and global_result:
        final_result = global_result
    
    # If global search failed essentially, we might still want to construct a response from song search,
    # but strictly speaking global_search returns a specific structure with 'topQuery', 'albums', etc.
    # If global failed, we might checking songs_result.
    if not final_result and not isinstance(songs_result, Exception) and songs_result and songs_result.get("success"):
        # Construct a partial global result from song result
        final_result = {
            "success": True,
            "data": {
                "songs": songs_result.get("data", {}),
                "topQuery": {"results": []},
                "albums": {"results": []},
                "artists": {"results": []},
                "playlists": {"results": []}
            }
        }

    if final_result and final_result.get("success"):
        data = final_result.get("data", {})
        
        # 1. Enrich Top Query
        if "topQuery" in data and "results" in data["topQuery"]:
            top_results = data["topQuery"]["results"]
            if language:
                top_results = [
                    s for s in top_results
                    if s.get("type") != "song" or s.get("language", "").lower() == language.lower()
                ]
            data["topQuery"]["results"] = await enrich_songs(top_results)

        # 2. Merge/Use Dedicated Songs
        # Extract dedicated songs
        dedicated_songs = []
        if not isinstance(songs_result, Exception) and songs_result and songs_result.get("success"):
            d_data = songs_result.get("data", {})
            if "results" in d_data:
                dedicated_songs = d_data["results"]

        # If we have dedicated songs, use them as the primary source for the 'songs' section
        # because global search truncates this list severely.
        if dedicated_songs:
            if language:
                dedicated_songs = [
                    s for s in dedicated_songs
                    if s.get("language", "").lower() == language.lower()
                ]
            # Verify enrichment for these songs
            data["songs"] = {"results": await enrich_songs(dedicated_songs)}
        
        # Fallback: if dedicated search failed or returned nothing, use global songs (enriched)
        elif "songs" in data and "results" in data["songs"]:
            start_songs = data["songs"]["results"]
            if language:
                start_songs = [
                    s for s in start_songs
                    if s.get("language", "").lower() == language.lower()
                ]
            data["songs"]["results"] = await enrich_songs(start_songs)

    return final_result


async def search_songs(query: str, page: int = 0, limit: int = 20) -> Optional[dict]:
    """Search specifically for songs."""
    return await _get("/api/search/songs", params={
        "query": query, "page": page, "limit": limit
    })


async def search_albums(query: str, page: int = 0, limit: int = 20) -> Optional[dict]:
    """Search specifically for albums."""
    return await _get("/api/search/albums", params={
        "query": query, "page": page, "limit": limit
    })


async def search_artists(query: str, page: int = 0, limit: int = 20) -> Optional[dict]:
    """Search specifically for artists."""
    return await _get("/api/search/artists", params={
        "query": query, "page": page, "limit": limit
    })


async def search_podcasts(query: str, page: int = 0, limit: int = 20) -> Optional[dict]:
    """Search for podcasts."""
    # The unofficial API might not have a dedicated podcast endpoint, 
    # so we use song search with "podcast" as query or filter if global search has them.
    # However, for now we search specifically for "podcast" and enrich them.
    return await _get("/api/search/songs", params={
        "query": f"{query} podcast", "page": page, "limit": limit
    })


# ── Song Details ────────────────────────────────────────────────────────────

async def get_song_by_id(song_id: str) -> Optional[dict]:
    """Get full song details by ID. Supports comma separated IDs."""
    data = await _get("/api/songs", params={"ids": song_id})
    return data


async def get_song_lyrics(song_id: str) -> Optional[dict]:
    """Get lyrics for a song."""
    return await _get("/api/songs/lyrics", params={"ids": song_id})


# ── Suggestions / Recommendations ──────────────────────────────────────────

async def get_song_suggestions(song_id: str) -> Optional[dict]:
    """Get suggested songs based on a song."""
    return await _get("/api/songs/suggestions", params={"ids": song_id})


# ── Artist ──────────────────────────────────────────────────────────────────

async def get_artist_by_id(artist_id: str) -> Optional[dict]:
    """Get artist details and top songs."""
    return await _get(f"/api/artists/{artist_id}")


async def get_artist_songs(artist_id: str, page: int = 0) -> Optional[dict]:
    """Get songs by a specific artist."""
    return await _get(f"/api/artists/{artist_id}/songs", params={"page": page})


async def get_artist_albums(artist_id: str, page: int = 0) -> Optional[dict]:
    """Get albums by a specific artist."""
    return await _get(f"/api/artists/{artist_id}/albums", params={"page": page})


# ── Album ───────────────────────────────────────────────────────────────────

async def get_album_by_id(album_id: str) -> Optional[dict]:
    """Get album details and songs."""
    return await _get(f"/api/albums", params={"id": album_id})


# ── Playlist ────────────────────────────────────────────────────────────────

async def get_playlist_by_id(playlist_id: str) -> Optional[dict]:
    """Get playlist details and songs."""
    return await _get(f"/api/playlists", params={"id": playlist_id})

# ── Enrichment ─────────────────────────────────────────────────────────────

async def enrich_songs(songs: List[Dict]) -> List[Dict]:
    """
    Ensures that songs have essential playback data (downloadUrl).
    If missing, fetches full details in parallel.
    """
    if not songs:
        return []

    # Identify songs that need enrichment
    tasks = []
    indices_to_enrich = []

    for i, item in enumerate(songs):
        # Only enrich items that look like songs or are confirmed as songs
        item_type = item.get("type", "song")
        if item_type != "song":
            continue

        download_url = item.get("downloadUrl")
        # If downloadUrl is missing, or empty list, it needs enrichment
        # BUT if it already has a raw 'url' that looks like a stream, we might skip
        if not download_url or not isinstance(download_url, list) or len(download_url) == 0:
            song_id = item.get("id")
            if song_id:
                tasks.append(get_song_by_id(song_id))
                indices_to_enrich.append(i)

    if not tasks:
        return songs

    logger.info(f"Enriching {len(tasks)} songs... (Total items: {len(songs)})")
    
    # Fetch all details in parallel, return_exceptions=True to keep moving on individual failures
    enriched_results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(enriched_results):
        original_index = indices_to_enrich[i]
        item = songs[original_index]
        item_id = item.get("id", "Unknown")
        item_name = item.get("name", item.get("title", "Unknown"))

        if isinstance(result, Exception):
            logger.warning(f"Enrichment task for {item_name} ({item_id}) raised exception: {result}")
            continue

        if result and result.get("success"):
            data = result.get("data")
            full_song = None
            if isinstance(data, list) and len(data) > 0:
                full_song = data[0]
            elif isinstance(data, dict):
                full_song = data

            if full_song:
                # Update original song with ALL fields from full_song
                songs[original_index].update(full_song)
            else:
                logger.warning(f"Enrichment result data empty for {item_name} ({item_id})")
        else:
            msg = result.get("message") if result else "No response"
            logger.warning(f"Enrichment failed for {item_name} ({item_id}). Status: {msg}")

    return songs
