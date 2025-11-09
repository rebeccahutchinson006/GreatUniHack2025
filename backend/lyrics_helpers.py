"""
Lyrics Helper Functions
Provides functions for fetching lyrics from various sources
"""
import httpx
import lyricsgenius
from typing import Optional, List
from pydantic import BaseModel


class LyricsLine(BaseModel):
    text: str
    timestamp_ms: int  # Timestamp in milliseconds


def parse_lrc_content(lrc_content: str) -> Optional[dict]:
    """
    Parse LRC file content and extract timestamped lines.
    
    Args:
        lrc_content: LRC format string content
    
    Returns:
        Dictionary with "lines" (list of LyricsLine) and "text" (full text), or None
    """
    try:
        lines = []
        full_text = []
        import re
        
        for line in lrc_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Parse timestamp format: [mm:ss.xx] or [mm:ss.xxx]
            timestamp_match = re.match(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)', line)
            if timestamp_match:
                minutes = int(timestamp_match.group(1))
                seconds = int(timestamp_match.group(2))
                centiseconds = int(timestamp_match.group(3))
                
                # Convert to milliseconds
                timestamp_ms = (minutes * 60 + seconds) * 1000 + (centiseconds * 10 if len(timestamp_match.group(3)) == 2 else centiseconds)
                
                text = timestamp_match.group(4).strip()
                if text:  # Only add non-empty lines
                    lines.append(LyricsLine(text=text, timestamp_ms=timestamp_ms))
                    full_text.append(text)
        
        if lines:
            return {
                "lines": lines,
                "text": "\n".join(full_text)
            }
        
        return None
    except Exception as e:
        print(f"Error parsing LRC: {e}")
        return None


async def get_lrc_lyrics(track_name: str, artist_name: str) -> Optional[dict]:
    """
    Try to fetch LRC file from various sources (async).
    
    Args:
        track_name: Name of the track
        artist_name: Name of the artist
    
    Returns:
        Dictionary with "lines" and "text" if found, None otherwise
    """
    # Clean up names for URL encoding
    artist = artist_name.split(",")[0].strip()
    
    async with httpx.AsyncClient() as client:
        # Try LRCLib API first (free, open source)
        try:
            from urllib.parse import quote
            encoded_artist = quote(artist)
            encoded_track = quote(track_name)
            url = f"https://lrclib.net/api/get?artist_name={encoded_artist}&track_name={encoded_track}"
            
            response = await client.get(url, timeout=5.0, follow_redirects=True)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("syncedLyrics"):
                    # LRCLib returns synced lyrics in LRC format
                    lrc_content = data.get("syncedLyrics", "")
                    parsed = parse_lrc_content(lrc_content)
                    if parsed:
                        print(f"[DEBUG] Found LRC lyrics from LRCLib for {track_name} by {artist}")
                        return parsed
        except Exception as e:
            print(f"LRCLib API error: {e}")
    
    return None


async def get_lyrics_ovh(track_name: str, artist_name: str) -> Optional[str]:
    """
    Get lyrics from Lyrics.ovh (free API) (async).
    
    Args:
        track_name: Name of the track
        artist_name: Name of the artist
    
    Returns:
        Lyrics text if found, None otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            # Clean up artist name (take first artist if multiple)
            artist = artist_name.split(",")[0].strip()
            
            url = f"https://api.lyrics.ovh/v1/{artist}/{track_name}"
            response = await client.get(url, timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("lyrics", "")
            
            return None
    except Exception:
        return None


def get_genius_lyrics_sync(track_name: str, artist_name: str, genius_token: str) -> Optional[str]:
    """
    Synchronous function to get lyrics from Genius API using lyricsgenius.
    
    Args:
        track_name: Name of the track
        artist_name: Name of the artist
        genius_token: Genius API access token
    
    Returns:
        Lyrics text if found, None otherwise
    """
    try:
        if not genius_token:
            return None
        
        genius_client = lyricsgenius.Genius(genius_token)
        # Remove section headers and other metadata from lyrics
        genius_client.remove_section_headers = True
        genius_client.skip_non_songs = True
        
        # Clean up artist name (take first artist if multiple)
        artist = artist_name.split(",")[0].strip()
        
        # Search for the song
        song = genius_client.search_song(track_name, artist)
        
        if song and song.lyrics:
            # Clean up the lyrics - remove metadata at the end
            lyrics = song.lyrics
            # Remove common Genius metadata patterns
            if "You might also like" in lyrics:
                lyrics = lyrics.split("You might also like")[0]
            if "Embed" in lyrics and lyrics.count("Embed") > 1:
                # Remove embed information
                parts = lyrics.split("Embed")
                if len(parts) > 1:
                    lyrics = parts[0].strip()
            
            return lyrics.strip()
        
        return None
    except Exception as e:
        print(f"Error fetching Genius lyrics: {e}")
        return None

