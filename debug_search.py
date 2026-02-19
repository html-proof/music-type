import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import saavn_service

async def debug_search():
    print("Debugging search_songs...")
    
    # Test 1: Search Songs
    print("\n--- search_songs('believer') ---")
    res = await saavn_service.search_songs("believer", limit=5)
    print(f"Result keys: {res.keys()}")
    if res.get("success"):
        data = res.get("data", {})
        results = data.get("results", [])
        print(f"Found {len(results)} songs")
        if results:
            first = results[0]
            print(f"First song keys: {first.keys()}")
            print(f"First song name: {first.get('name')}")
            print(f"First song image: {first.get('image')}")
            print(f"First song downloadUrl: {first.get('downloadUrl')}")
    else:
        print("Search failed")

    # Test 2: Global Search
    print("\n--- global_search('believer') ---")
    g_res = await saavn_service.global_search("believer", limit=5)
    if g_res.get("success"):
        g_data = g_res.get("data", {})
        songs_res = g_data.get("songs", {}).get("results", [])
        print(f"Global Search Found {len(songs_res)} songs")
    else:
        print("Global Search failed")

if __name__ == "__main__":
    asyncio.run(debug_search())
