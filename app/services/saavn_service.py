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
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout calling Saavn API: {url}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Saavn API: {e.response.status_code} {url}")
        return None
    except Exception as e:
        logger.error(f"Saavn API error: {e}")
        return None


# ── Search ──────────────────────────────────────────────────────────────────

async def global_search(query: str) -> Optional[dict]:
    """Global search: songs, albums, artists, playlists."""
    return await _get("/api/search", params={"query": query})


async def search_songs(query: str, page: int = 0, limit: int = 10) -> Optional[dict]:
    """Search specifically for songs."""
    return await _get("/api/search/songs", params={
        "query": query, "page": page, "limit": limit
    })


async def search_albums(query: str, page: int = 0, limit: int = 10) -> Optional[dict]:
    """Search specifically for albums."""
    return await _get("/api/search/albums", params={
        "query": query, "page": page, "limit": limit
    })


async def search_artists(query: str, page: int = 0, limit: int = 10) -> Optional[dict]:
    """Search specifically for artists."""
    return await _get("/api/search/artists", params={
        "query": query, "page": page, "limit": limit
    })


# ── Song Details ────────────────────────────────────────────────────────────

async def get_song_by_id(song_id: str) -> Optional[dict]:
    """Get full song details by ID."""
    return await _get(f"/api/songs/{song_id}")


async def get_song_lyrics(song_id: str) -> Optional[dict]:
    """Get lyrics for a song."""
    return await _get(f"/api/songs/{song_id}/lyrics")


# ── Suggestions / Recommendations ──────────────────────────────────────────

async def get_song_suggestions(song_id: str) -> Optional[dict]:
    """Get suggested songs based on a song."""
    return await _get(f"/api/songs/{song_id}/suggestions")


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

    for i, song in enumerate(songs):
        download_url = song.get("downloadUrl")
        # If downloadUrl is missing, empty, or not a list, it needs enrichment
        if not download_url or not isinstance(download_url, list) or len(download_url) == 0:
            song_id = song.get("id")
            if song_id:
                tasks.append(get_song_by_id(song_id))
                indices_to_enrich.append(i)

    if not tasks:
        return songs

    logger.info(f"Enriching {len(tasks)} songs missing playback data...")
    
    # Fetch all details in parallel
    enriched_results = await asyncio.gather(*tasks)

    for i, result in enumerate(enriched_results):
        if result and result.get("success"):
            # Result data can be a list or a dict containing song data
            data = result.get("data")
            full_song = None
            if isinstance(data, list) and len(data) > 0:
                full_song = data[0]
            elif isinstance(data, dict):
                full_song = data

            if full_song:
                original_index = indices_to_enrich[i]
                # Update original song with missing fields
                songs[original_index].update({
                    "downloadUrl": full_song.get("downloadUrl", []),
                    "image": full_song.get("image", []),
                    "duration": full_song.get("duration"),
                    "hasLyrics": full_song.get("hasLyrics"),
                    # Add any other critical playing fields here
                })

    return songs
