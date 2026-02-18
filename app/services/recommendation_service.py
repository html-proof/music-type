import logging
from typing import Optional
from app.services import saavn_service, firebase_service

logger = logging.getLogger(__name__)


async def get_recommendations(
    song_id: Optional[str] = None,
    uid: Optional[str] = None,
    limit: int = 20,
) -> dict:
    results = []

    # ── Strategy 1: Recent History suggestions ──────────────────────────
    if uid:
        history = firebase_service.get_history(uid, limit=5)
        if history:
            # history is a dict of song_id: data. Sort by playedAt desc
            sorted_history = sorted(
                history.items(), 
                key=lambda x: x[1].get("playedAt", 0), 
                reverse=True
            )
            for song_id, data in sorted_history[:2]:
                suggestions = await saavn_service.get_song_suggestions(song_id)
                if suggestions and suggestions.get("success"):
                    data = suggestions.get("data", [])
                    if isinstance(data, list):
                        results.extend(data[:5])
                    elif isinstance(data, dict):
                        results.extend(data.get("results", data.get("songs", []))[:5])

    # ── Strategy 2: Song-based suggestions (if specific song_id given) ───
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

    # ── Strategy 3: User preference-based ───────────────────────────────
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

            if results and len(results) >= limit:
                return {"success": True, "data": results[:limit], "source": "preferences"}

            # Search by language if we still need more
            if preferred_language and len(results) < limit:
                lang_songs = await saavn_service.search_songs(
                    preferred_language, limit=limit - len(results)
                )
                if lang_songs and lang_songs.get("success"):
                    results.extend(lang_songs.get("data", {}).get("results", []))

            if results:
                return {"success": True, "data": results[:limit], "source": "preferences"}

    # ── Strategy 4: Trending fallback ───────────────────────────────────
    trending = await saavn_service.search_songs("trending", limit=limit)
    if trending and trending.get("success"):
        results = trending.get("data", {}).get("results", [])

    # ── Final Enrichment ────────────────────────────────────────────────
    enriched_data = await saavn_service.enrich_songs(results[:limit])

    return {
        "success": bool(enriched_data),
        "data": enriched_data,
        "source": "mixed" if uid else "trending",
    }
