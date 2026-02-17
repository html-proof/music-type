import logging
from typing import Optional
from app.services import saavn_service, firebase_service

logger = logging.getLogger(__name__)


async def get_recommendations(
    song_id: Optional[str] = None,
    uid: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """
    Get song recommendations using this priority:

    1. If song_id given → Saavn suggestions for that song
    2. If user has preferences → songs by preferred artist + language
    3. Fallback → trending / popular songs
    """
    results = []

    # ── Strategy 1: Song-based suggestions ──────────────────────────────
    if song_id:
        suggestions = await saavn_service.get_song_suggestions(song_id)
        if suggestions and suggestions.get("success"):
            data = suggestions.get("data", [])
            if isinstance(data, list):
                results.extend(data[:limit])
            elif isinstance(data, dict):
                results.extend(data.get("results", data.get("songs", []))[:limit])

        if len(results) >= limit:
            return {"success": True, "data": results[:limit], "source": "song_suggestions"}

    # ── Strategy 2: User preference-based ───────────────────────────────
    if uid:
        prefs = firebase_service.get_preferences(uid)
        if prefs:
            preferred_language = prefs.get("language")
            preferred_artists = prefs.get("artists", [])

            # Search by preferred artists
            for artist_name in preferred_artists[:3]:
                artist_songs = await saavn_service.search_songs(artist_name, limit=5)
                if artist_songs and artist_songs.get("success"):
                    for song in artist_songs.get("data", {}).get("results", []):
                        # Filter by language if set
                        if preferred_language:
                            song_lang = song.get("language", "").lower()
                            if song_lang and song_lang != preferred_language.lower():
                                continue
                        results.append(song)

            if len(results) >= limit:
                return {"success": True, "data": results[:limit], "source": "preferences"}

            # Search by language
            if preferred_language and len(results) < limit:
                lang_songs = await saavn_service.search_songs(
                    preferred_language, limit=limit - len(results)
                )
                if lang_songs and lang_songs.get("success"):
                    results.extend(lang_songs.get("data", {}).get("results", []))

            if results:
                return {"success": True, "data": results[:limit], "source": "preferences"}

    # ── Strategy 3: Trending fallback ───────────────────────────────────
    trending = await saavn_service.search_songs("trending", limit=limit)
    if trending and trending.get("success"):
        results = trending.get("data", {}).get("results", [])

    return {
        "success": bool(results),
        "data": results[:limit],
        "source": "trending" if results else "none",
    }
