"""
Spotify API Helper Functions
Provides async helper functions for interacting with Spotify API
"""
import httpx
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# Spotify API credentials - should be set as environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")


async def get_access_token(client_id: Optional[str] = None, client_secret: Optional[str] = None) -> str:
    """
    Get Spotify access token using client credentials flow (async).
    
    Args:
        client_id: Spotify client ID (defaults to env var)
        client_secret: Spotify client secret (defaults to env var)
    
    Returns:
        Access token string
    
    Raises:
        Exception: If token request fails
    """
    client_id = client_id or SPOTIFY_CLIENT_ID
    client_secret = client_secret or SPOTIFY_CLIENT_SECRET
    
    if not client_id or not client_secret:
        raise Exception("Spotify Client ID and Secret must be provided")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Token request failed: {response.status_code} {response.text}")


async def get_top_artists_by_genre(
    token: str, 
    genre: str, 
    limit: int = 10
) -> List[Dict]:
    """
    Fetch top artists for a genre/region, sorted by popularity (async).
    
    Args:
        token: Spotify access token
        genre: Search query (e.g., "french", "k-pop", artist names)
        limit: Maximum number of artists to return
    
    Returns:
        List of artist dictionaries with id, name, image, popularity
    
    Raises:
        Exception: If API request fails
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/search"
    
    params = {
        "q": genre,
        "type": "artist",
        "limit": 50  # Get more, then filter by popularity
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params, timeout=10.0)
        if response.status_code != 200:
            raise Exception(f"Spotify API error: {response.status_code} {response.text}")
        
        artists = response.json()["artists"]["items"]
        
        # Filter out artists with very low popularity
        artists = [a for a in artists if a.get("popularity", 0) > 0]
        
        # Sort descending by popularity
        artists.sort(key=lambda a: a.get("popularity", 0), reverse=True)
        
        top_artists = []
        for artist in artists[:limit]:
            # Get best quality image (images are sorted by size, largest first)
            image_url = artist["images"][0]["url"] if artist["images"] else None
            
            top_artists.append({
                "id": artist["id"],
                "name": artist["name"],
                "image": image_url,
                "popularity": artist.get("popularity", 0)
            })
        
        return top_artists


async def get_top_tracks_by_artist_id(
    token: str, 
    artist_id: str, 
    market: str = "US", 
    limit: int = 10
) -> List[Dict]:
    """
    Get an artist's top tracks using Spotify's dedicated endpoint (async).
    
    Args:
        token: Spotify access token
        artist_id: Spotify artist ID
        market: Market code (default: "US")
        limit: Maximum number of tracks to return
    
    Returns:
        List of track dictionaries with name, popularity, preview_url
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    params = {"market": market}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            if response.status_code != 200:
                print(f"Warning: Failed to fetch tracks for artist {artist_id}: {response.status_code}")
                return []
            
            tracks = response.json()["tracks"]
            
            # Top tracks endpoint already returns sorted by popularity
            top_tracks = []
            for track in tracks[:limit]:
                top_tracks.append({
                    "name": track["name"],
                    "id": track["id"],
                    "uri": track["uri"],
                    "popularity": track["popularity"],
                    "preview_url": track.get("preview_url")
                })
            
            return top_tracks
    except Exception as e:
        print(f"Error fetching tracks for artist {artist_id}: {e}")
        return []


async def get_all_artists_top_tracks(
    token: str, 
    artists: List[Dict], 
    limit: int = 10, 
    market: str = "US"
) -> Dict[str, Dict]:
    """
    Fetch top tracks for multiple artists concurrently (async).
    This dramatically speeds up the process compared to sequential requests.
    
    Args:
        token: Spotify access token
        artists: List of artist dictionaries (must have "id" key)
        limit: Maximum number of tracks per artist
        market: Market code (default: "US")
    
    Returns:
        Dictionary mapping artist names to their data and tracks
    """
    import asyncio
    
    results = {}
    
    # Create tasks for all artists
    tasks = [
        get_top_tracks_by_artist_id(token, artist["id"], market, limit)
        for artist in artists
    ]
    
    # Execute all requests concurrently
    track_lists = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for artist, tracks in zip(artists, track_lists):
        if isinstance(tracks, Exception):
            print(f"Error processing {artist['name']}: {tracks}")
            results[artist["name"]] = {
                "artist": artist,
                "tracks": []
            }
        else:
            results[artist["name"]] = {
                "artist": artist,
                "tracks": tracks
            }
    
    return results


def encode_client_credentials(client_id: str, client_secret: str) -> str:
    """
    Encode client credentials for Basic Auth.
    
    Args:
        client_id: Spotify client ID
        client_secret: Spotify client secret
    
    Returns:
        Base64 encoded credentials string
    """
    import base64
    credentials = f"{client_id}:{client_secret}"
    return base64.b64encode(credentials.encode()).decode()

