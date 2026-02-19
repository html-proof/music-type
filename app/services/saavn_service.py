import httpx
import logging
import asyncio
import json
import base64
from typing import Optional, List, Dict, Any
from app.config import settings
from Crypto.Cipher import DES

logger = logging.getLogger(__name__)

BASE_URL = settings.saavn_api_base_url
DES_CIPHER_KEY = b"38346591"

# ── DES Decryption ────────────────────────────────────────────────────────────

def decrypt_url(encrypted_url: str) -> Optional[str]:
    """Decrypts the encrypted_media_url using DES."""
    try:
        enc_url = base64.b64decode(encrypted_url.strip())
        cipher = DES.new(DES_CIPHER_KEY, DES.MODE_ECB)
        dec_url = cipher.decrypt(enc_url).decode("utf-8")
        dec_url = dec_url.strip()  # Remove padding
        return dec_url.replace('\x00', '').replace('\x01', '').replace('\x02', '').replace('\x03', '').replace('\x04', '').replace('\x05', '').replace('\x06', '').replace('\x07', '').replace('\x08', '').replace('\t', '').replace('\n', '').replace('\r', '')
    except Exception as e:
        logger.error(f"Error decrypting URL: {e}")
        return None

# ── Helper: Transformation ────────────────────────────────────────────────────

def _format_song(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms official API song object to the app's expected format.
    """
    try:
        image_url = data.get("image", "").replace("150x150", "500x500")
        
        # Handle Artists
        artists = []
        if "more_info" in data:
             # Web API often puts artistMap in more_info
             artist_map = data["more_info"].get("artistMap", {})
             if artist_map:
                primary = artist_map.get("primary_artists", [])
                featured = artist_map.get("featured_artists", [])
                artists.extend([a.get("name") for a in primary])
                artists.extend([a.get("name") for a in featured])
        
        if not artists and "primary_artists" in data:
            # sometimes it's just a string in search results
             artists.append(data.get("primary_artists"))

        # Decrypt URL
        download_url = None
        encrypted_url = data.get("encrypted_media_url") or data.get("more_info", {}).get("encrypted_media_url")
        if encrypted_url:
            decrypted = decrypt_url(encrypted_url)
            if decrypted:
                download_url = [{"quality": "320kbps", "url": decrypted}]

        return {
            "id": data.get("id"),
            "name": data.get("song") or data.get("title"),
            "type": "song",
            "album": {
                "id": data.get("albumid") or data.get("more_info", {}).get("album_id"),
                "name": data.get("album") or data.get("more_info", {}).get("album"),
                "url": data.get("more_info", {}).get("album_url")
            },
            "year": data.get("year"),
            "releaseDate": data.get("release_date"),
            "duration": data.get("duration"),
            "label": data.get("label") or data.get("more_info", {}).get("label"),
            "artists": {"primary": artists, "all": []},
            "primary_artists": ", ".join(artists),
            "explicitContent": data.get("explicit_content") == "1",
            "playCount": data.get("play_count"),
            "language": data.get("language"),
            "hasLyrics": data.get("has_lyrics") == "true",
            "url": data.get("perma_url"),
            "image": [{"quality": "500x500", "url": image_url}],
            "downloadUrl": download_url
        }
    except Exception as e:
        logger.error(f"Error formatting song: {e}")
        return data

def _format_album(data: Dict[str, Any]) -> Dict[str, Any]:
    image_url = data.get("image", "").replace("150x150", "500x500")
    return {
        "id": data.get("id") or data.get("albumid"),
        "name": data.get("title") or data.get("album"),
        "type": "album",
        "image": [{"quality": "500x500", "url": image_url}],
        "language": data.get("language"),
        "year": data.get("year"),
        "playCount": data.get("play_count"),
        "explicitContent": data.get("explicit_content") == "1",
        "primary_artists": data.get("primary_artists") or data.get("music", ""),
        "url": data.get("perma_url"),
        "songs": [] 
    }

# ── API Calls ─────────────────────────────────────────────────────────────────

async def _get(params: Dict[str, Any]) -> Optional[Any]:
    params_clean = {
        "_format": "json",
        "_marker": "0",
        "api_version": "4",
        "ctx": "web6dot0",
        **params
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            response = await client.get(BASE_URL, params=params_clean)
            if response.status_code != 200:
                logger.error(f"Upstream error: {response.status_code}")
                return None
            
            try:
                # Sometimes API returns invalid JSON (text before/after json)
                text = response.text
                if not text.strip().startswith("{") and not text.strip().startswith("["):
                     # Try to find json start/end
                     start = text.find("{")
                     if start != -1:
                        text = text[start:]
                return json.loads(text)
            except json.JSONDecodeError:
                logger.error(f"JSON Decode Error. Text: {response.text[:200]}")
                return None
                
    except Exception as e:
        logger.error(f"Saavn API Connection error: {e}")
        return None

# ── Search ──────────────────────────────────────────────────────────────────

async def search_songs(query: str, page: int = 1, limit: int = 20) -> Optional[dict]:
    data = await _get({
        "__call": "search.getResults",
        "q": query,
        "n": limit,
        "p": page,
    })
    
    if data and "results" in data:
        results = [_format_song(s) for s in data["results"]]
        return {"success": True, "data": {"results": results}}
    
    return {"success": False, "data": {"results": []}}

async def search_albums(query: str, page: int = 1, limit: int = 20) -> Optional[dict]:
    data = await _get({
        "__call": "search.getAlbumResults",
        "q": query,
        "n": limit,
        "p": page
    })
    
    if data and "results" in data:
        results = [_format_album(s) for s in data["results"]]
        return {"success": True, "data": {"results": results}}

    return {"success": False, "data": {"results": []}}

async def search_artists(query: str, page: int = 1, limit: int = 20) -> Optional[dict]:
    data = await _get({
        "__call": "search.getArtistResults",
        "q": query,
        "n": limit,
        "p": page
    })
    
    if data and "results" in data:
        return {"success": True, "data": {"results": data["results"]}}
    return {"success": False, "data": {"results": []}}

async def global_search(query: str, language: Optional[str] = None, limit: int = 20) -> Optional[dict]:
    song_task = search_songs(query, limit=limit)
    album_task = search_albums(query, limit=limit)
    
    results = await asyncio.gather(song_task, album_task)
    
    return {
        "success": True,
        "data": {
            "songs": results[0]["data"] if results[0] else {"results": []},
            "albums": results[1]["data"] if results[1] else {"results": []},
            "topQuery": {"results": []} 
        }
    }

# ── Details ──────────────────────────────────────────────────────────────────

async def get_song_by_id(song_id: str) -> Optional[dict]:
    data = await _get({
        "__call": "song.getDetails",
        "pids": song_id
    })
    
    if data:
        # data might be { song_id: {...} } or { "songs": [...] } or just {...}
        raw_song = None
        if isinstance(data, dict):
            if "songs" in data and data["songs"]:
                raw_song = data["songs"][0]
            elif song_id in data:
                raw_song = data[song_id]
            elif "id" in data:
                raw_song = data
        
        if raw_song:
            formatted = _format_song(raw_song)
            return {"success": True, "data": [formatted]}
            
    return {"success": False, "message": "Song not found"}

async def get_album_by_id(album_id: str) -> Optional[dict]:
    data = await _get({
        "__call": "content.getAlbumDetails",
        "albumid": album_id
    })
    
    if data:
        formatted = _format_album(data)
        if "list" in data:
            formatted["songs"] = [_format_song(s) for s in data["list"]]
            
        return {"success": True, "data": formatted}
        
    return {"success": False, "message": "Album not found"}

async def get_playlist_by_id(playlist_id: str) -> Optional[dict]:
    data = await _get({
        "__call": "playlist.getDetails",
        "listid": playlist_id
    })

    if data:
         # Playlist data structure
         image_url = data.get("image", "").replace("150x150", "500x500")
         formatted = {
             "id": data.get("id") or data.get("listid"),
             "name": data.get("title") or data.get("listname"),
             "type": "playlist",
             "image": [{"quality": "500x500", "url": image_url}],
             "songs": []
         }
         if "list" in data:
             formatted["songs"] = [_format_song(s) for s in data["list"]]
         return {"success": True, "data": formatted}

    return {"success": False, "message": "Playlist not found"}

async def get_artist_by_id(artist_id: str) -> Optional[dict]:
    data = await _get({
        "__call": "artist.getArtistPageDetails",
        "artistId": artist_id
    })
    
    if data:
        # Standardize artist format
        return {"success": True, "data": data}
        
    return {"success": False, "message": "Artist not found"}

async def get_artist_songs(artist_id: str, page: int = 1) -> Optional[dict]:
    data = await _get({
        "__call": "artist.getArtistMoreSong",
        "artistId": artist_id,
        "p": page,
        "n": 20
    })
    if data and "songs" in data:
         results = [_format_song(s) for s in data["songs"]]
         return {"success": True, "data": results}
         
    return {"success": False, "data": []}

async def get_artist_albums(artist_id: str, page: int = 1) -> Optional[dict]:
    data = await _get({
        "__call": "artist.getArtistMoreAlbum",
        "artistId": artist_id,
        "p": page,
        "n": 20
    })
    if data and "albums" in data:
         results = [_format_album(s) for s in data["albums"]]
         return {"success": True, "data": results}

    return {"success": False, "data": []}

# ── Extra ─────────────────────────────────────────────────────────────────────

async def get_song_lyrics(song_id: str) -> Optional[dict]:
    data = await _get({
        "__call": "lyrics.getLyrics",
        "lyrics_id": song_id, 
        "ctx": "web6dot0"
    })
    
    if data and "lyrics" in data:
        return {"success": True, "data": {"lyrics": data["lyrics"]}}
        
    return {"success": False, "message": "Lyrics not found"}

async def get_song_suggestions(song_id: str) -> Optional[dict]:
    # reco.getreco usually requires pid
    data = await _get({
        "__call": "reco.getreco",
        "pid": song_id
    })
    
    if data:
        # returns list of songs directly? or dict?
        # usually list
        results = []
        if isinstance(data, list):
            results = [_format_song(s) for s in data]
        return {"success": True, "data": results}
        
    return {"success": False, "message": "No suggestions found"}

# ── Enrichment ─────────────────────────────────────────────────────────────

async def enrich_songs(songs: List[Dict]) -> List[Dict]:
    """
    Ensures that songs have playback data (downloadUrl).
    If missing, fetches full details in parallel.
    """
    if not songs:
        return []

    tasks = []
    indices_to_enrich = []

    for i, item in enumerate(songs):
        download_url = item.get("downloadUrl")
        # If downloadUrl is missing, or empty list, it needs enrichment
        if not download_url:
            song_id = item.get("id")
            if song_id:
                tasks.append(get_song_by_id(song_id))
                indices_to_enrich.append(i)

    if not tasks:
        return songs

    logger.info(f"Enriching {len(tasks)} songs...")
    enriched_results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(enriched_results):
        original_index = indices_to_enrich[i]
        
        if isinstance(result, Exception):
            logger.error(f"Enrichment error: {result}")
            continue

        if result and result.get("success"):
            data = result.get("data")
            full_song = None
            if isinstance(data, list) and len(data) > 0:
                full_song = data[0]
            
            if full_song:
                 # Update original with full details
                 songs[original_index].update(full_song)
    
    return songs
