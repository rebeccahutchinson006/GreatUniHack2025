from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List
import secrets
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from translation_library import DeepLTranslator, LyricFormatter
from translation_library.exceptions import TranslationError, RateLimitError, InvalidLanguageError

# Import helper modules
from spotify_helpers import (
    encode_client_credentials,
    get_access_token,
    get_top_artists_by_genre,
    get_all_artists_top_tracks
)
from lyrics_helpers import get_lrc_lyrics, get_lyrics_ovh, get_genius_lyrics_sync, LyricsLine
from translation_helpers import translate_lyrics_sync, translate_batch_sync
from summary import analyze_lyrics

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Spotify Lyrics API")

# CORS middleware to allow React frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify API credentials - should be set as environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

# Genius API access token for lyrics
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN", "")

# DeepL API key for translation
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")

# Thread pool executor for running synchronous operations
executor = ThreadPoolExecutor(max_workers=2)

# In-memory storage for access tokens (use Redis or database in production)
user_tokens = {}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


class CurrentlyPlaying(BaseModel):
    track_name: str
    artist_name: str
    album_name: Optional[str] = None
    album_art: Optional[str] = None
    is_playing: bool
    progress_ms: int
    duration_ms: int


# LyricsLine is now imported from lyrics_helpers


class LyricsResponse(BaseModel):
    lyrics: str
    track_name: str
    artist_name: str
    synced: bool = False  # Whether lyrics have timestamps
    lines: Optional[List[LyricsLine]] = None  # Timestamped lines if synced


class TranslationRequest(BaseModel):
    lyrics: str
    target_lang: str = 'FR'
    source_lang: Optional[str] = 'EN'


class TranslationResponse(BaseModel):
    translated_lyrics: str
    original_lyrics: str
    target_language: str
    detected_language: Optional[str] = None
    translated_lines: Optional[List[LyricsLine]] = None  # For synced lyrics


class OverlayLine(BaseModel):
    original: str
    translated: str
    timestamp_ms: Optional[int] = None  # For synced lyrics


class OverlayTranslationRequest(BaseModel):
    lyrics: str
    target_lang: str = 'FR'
    source_lang: Optional[str] = 'EN'
    lines: Optional[List[LyricsLine]] = None  # For synced lyrics


class OverlayTranslationResponse(BaseModel):
    lines: List[OverlayLine]
    target_language: str
    detected_language: Optional[str] = None


class WordTranslationRequest(BaseModel):
    word: str
    target_lang: str = 'FR'
    source_lang: Optional[str] = 'EN'


class WordTranslationResponse(BaseModel):
    original_word: str
    translated_word: str
    target_language: str
    detected_language: Optional[str] = None


class LyricsAnalysisRequest(BaseModel):
    lyrics: str


class LyricsAnalysisResponse(BaseModel):
    summary: str
    insights: List[str]


@app.get("/")
async def root():
    return {"message": "Spotify Lyrics API"}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration (without exposing secrets)"""
    return {
        "client_id_set": bool(SPOTIFY_CLIENT_ID),
        "client_secret_set": bool(SPOTIFY_CLIENT_SECRET),
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "genius_token_set": bool(GENIUS_ACCESS_TOKEN),
    }


@app.get("/login")
async def login():
    """Initiate Spotify OAuth flow"""
    if not SPOTIFY_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Spotify Client ID not configured")
    
    if not SPOTIFY_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Spotify Client Secret not configured")
    
    state = secrets.token_urlsafe(32)
    scope = "user-read-currently-playing user-read-playback-state"
    
    # URL encode the redirect URI
    from urllib.parse import quote
    encoded_redirect_uri = quote(SPOTIFY_REDIRECT_URI, safe='')
    
    auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"response_type=code&"
        f"client_id={SPOTIFY_CLIENT_ID}&"
        f"scope={scope}&"
        f"redirect_uri={encoded_redirect_uri}&"
        f"state={state}"
    )
    
    print(f"[DEBUG] Redirect URI: {SPOTIFY_REDIRECT_URI}")
    print(f"[DEBUG] Auth URL: {auth_url}")
    
    return RedirectResponse(url=auth_url)


@app.get("/callback")
async def callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handle Spotify OAuth callback"""
    print(f"[DEBUG] Callback received - code: {code is not None}, state: {state is not None}, error: {error}")
    
    if error:
        print(f"[ERROR] Spotify OAuth error: {error}")
        return RedirectResponse(
            url=f"http://localhost:3000?error={error}"
        )
    
    if not code:
        print("[ERROR] No authorization code received")
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("[ERROR] Spotify credentials not configured")
        raise HTTPException(status_code=500, detail="Spotify credentials not configured")
    
    print(f"[DEBUG] Using redirect URI: {SPOTIFY_REDIRECT_URI}")
    
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        }
        
        auth_header = f"Basic {encode_client_credentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)}"
        
        print("[DEBUG] Requesting access token from Spotify...")
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data=token_data,
            headers={"Authorization": auth_header},
        )
        
        print(f"[DEBUG] Token response status: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.text
            print(f"[ERROR] Failed to get access token: {error_detail}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to get access token: {error_detail}"
            )
        
        token_info = response.json()
        access_token = token_info["access_token"]
        refresh_token = token_info.get("refresh_token")
        
        print("[DEBUG] Access token received, fetching user info...")
        
        # Get user info to create a session
        user_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if user_response.status_code != 200:
            print(f"[ERROR] Failed to get user info: {user_response.status_code}")
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_id = user_response.json()["id"]
        print(f"[DEBUG] User authenticated: {user_id}")
        
        user_tokens[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": token_info.get("expires_in", 3600),
        }
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:3000?user_id={user_id}"
        print(f"[DEBUG] Redirecting to frontend: {frontend_url}")
        return RedirectResponse(url=frontend_url)


@app.get("/currently-playing/{user_id}")
async def get_currently_playing(user_id: str):
    """Get the currently playing track for a user"""
    if user_id not in user_tokens:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    access_token = user_tokens[user_id]["access_token"]
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if response.status_code == 204:
            return {"is_playing": False, "message": "No track currently playing"}
        
        if response.status_code != 200:
            # Try to refresh token if expired
            if response.status_code == 401:
                await __refresh_user_token(user_id)
                access_token = user_tokens[user_id]["access_token"]
                response = await client.get(
                    "https://api.spotify.com/v1/me/player/currently-playing",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to get currently playing track"
                )
        
        data = response.json()
        item = data.get("item")
        
        if not item:
            return {"is_playing": False, "message": "No track currently playing"}
        
        track_name = item["name"]
        artists = [artist["name"] for artist in item["artists"]]
        artist_name = ", ".join(artists)
        album_name = item["album"]["name"]
        album_art = item["album"]["images"][0]["url"] if item["album"]["images"] else None
        
        return CurrentlyPlaying(
            track_name=track_name,
            artist_name=artist_name,
            album_name=album_name,
            album_art=album_art,
            is_playing=data.get("is_playing", False),
            progress_ms=data.get("progress_ms", 0),
            duration_ms=item.get("duration_ms", 0),
        )


@app.get("/lyrics/{track_name}/{artist_name}")
async def get_lyrics(track_name: str, artist_name: str):
    """Get lyrics for a track"""
    # Try LRC (synchronized lyrics) first
    lrc_data = await get_lrc_lyrics(track_name, artist_name)
    if lrc_data and lrc_data.get("lines"):
        return LyricsResponse(
            lyrics=lrc_data.get("text", ""),
            track_name=track_name,
            artist_name=artist_name,
            synced=True,
            lines=lrc_data.get("lines"),
        )
    
    # Try Genius API
    if GENIUS_ACCESS_TOKEN:
        lyrics = await asyncio.get_event_loop().run_in_executor(
            executor,
            get_genius_lyrics_sync,
            track_name,
            artist_name,
            GENIUS_ACCESS_TOKEN
        )
        if lyrics:
            return LyricsResponse(
                lyrics=lyrics,
                track_name=track_name,
                artist_name=artist_name,
                synced=False,
            )
    
    # Fallback to Lyrics.ovh (free, no API key needed)
    lyrics = await get_lyrics_ovh(track_name, artist_name)
    
    if not lyrics:
        raise HTTPException(
            status_code=404,
            detail=f"Lyrics not found for {track_name} by {artist_name}"
        )
    
    return LyricsResponse(
        lyrics=lyrics,
        track_name=track_name,
        artist_name=artist_name,
        synced=False,
    )

# translate_lyrics_sync is now imported from translation_helpers


@app.post("/translate", response_model=TranslationResponse)
async def translate_lyrics(request: TranslationRequest):
    """Translate lyrics to a target language"""
    if not DEEPL_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DeepL API key not configured. Set DEEPL_API_KEY environment variable."
        )
    
    try:
        # If we have synced lyrics (lines), translate each line separately
        print("Trying plane text yay :D")
        # Translate plain text lyrics - use formatter like in example
        formatter = LyricFormatter()
        
        # Preprocess lyrics for better translation
        formatted_lyrics = formatter.preprocess_lyrics(request.lyrics)
        
        # Split into segments if too long
        segments = formatter.split_into_segments(formatted_lyrics, max_segment_length=1000)
        
        # Translate each segment using batch translation
        translations = []
        detected_lang = None
        
        for segment in segments:
            result = await asyncio.get_event_loop().run_in_executor(
                executor,
                translate_lyrics_sync,
                segment,
                request.target_lang,
                request.source_lang,
                DEEPL_API_KEY
            )
            translations.append(result)
            if not detected_lang:
                detected_lang = result.get('detected_language')
        
        # Reassemble translated segments
        translated_lyrics = formatter.reassemble_segments(translations)
        
        return TranslationResponse(
            translated_lyrics=translated_lyrics,
            original_lyrics=request.lyrics,
            target_language=request.target_lang,
            detected_language=detected_lang
        )
    
    except InvalidLanguageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except TranslationError as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# translate_batch_sync is now imported from translation_helpers


@app.post("/translate-lines", response_model=OverlayTranslationResponse)
async def translate_lines_overlay(request: OverlayTranslationRequest):
    """Translate lyrics line-by-line for overlay display (shows both original and translated)"""
    if not DEEPL_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DeepL API key not configured. Set DEEPL_API_KEY environment variable."
        )
    
    try:
        overlay_lines = []
        detected_lang = None
        
        # Batch size for translation (to avoid rate limits)
        BATCH_SIZE = 20  # Translate 20 lines at a time
        
        # If we have synced lyrics (lines), translate in batches
        if request.lines:
            # Create a list to store results in order
            overlay_lines = [None] * len(request.lines)
            lines_to_translate = []
            translate_indices = []  # Track which indices need translation
            
            for idx, line in enumerate(request.lines):
                if line.text.strip():  # Only translate non-empty lines
                    lines_to_translate.append(line.text)
                    translate_indices.append(idx)
                else:
                    # Empty line - set directly
                    overlay_lines[idx] = OverlayLine(
                        original="",
                        translated="",
                        timestamp_ms=line.timestamp_ms
                    )
            
            # Translate in batches
            for i in range(0, len(lines_to_translate), BATCH_SIZE):
                batch = lines_to_translate[i:i + BATCH_SIZE]
                batch_indices = translate_indices[i:i + BATCH_SIZE]
                
                # Add small delay between batches to avoid rate limits (except for first batch)
                if i > 0:
                    await asyncio.sleep(0.5)  # 500ms delay between batches
                
                try:
                    results = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        translate_batch_sync,
                        batch,
                        request.target_lang,
                        request.source_lang,
                        DEEPL_API_KEY
                    )
                    
                    for result, idx in zip(results, batch_indices):
                        line = request.lines[idx]
                        overlay_lines[idx] = OverlayLine(
                            original=line.text,
                            translated=result['translated_text'],
                            timestamp_ms=line.timestamp_ms
                        )
                        if not detected_lang:
                            detected_lang = result.get('detected_language')
                except Exception as e:
                    # If batch translation fails, fall back to individual translations
                    print(f"Error translating batch: {e}, falling back to individual")
                    for text, idx in zip(batch, batch_indices):
                        line = request.lines[idx]
                        try:
                            result = await asyncio.get_event_loop().run_in_executor(
                                executor,
                                translate_lyrics_sync,
                                text,
                                request.target_lang,
                                request.source_lang,
                                DEEPL_API_KEY
                            )
                            overlay_lines[idx] = OverlayLine(
                                original=line.text,
                                translated=result['translated_text'],
                                timestamp_ms=line.timestamp_ms
                            )
                        except Exception as e2:
                            print(f"Error translating line: {e2}")
                            overlay_lines[idx] = OverlayLine(
                                original=line.text,
                                translated=line.text,
                                timestamp_ms=line.timestamp_ms
                            )
        else:
            # Split plain text lyrics into lines
            original_lines = request.lyrics.split('\n')
            overlay_lines = [None] * len(original_lines)
            lines_to_translate = []
            translate_indices = []
            
            for idx, original_line in enumerate(original_lines):
                original_line = original_line.strip()
                if not original_line:  # Empty line
                    overlay_lines[idx] = OverlayLine(
                        original="",
                        translated=""
                    )
                else:
                    lines_to_translate.append(original_line)
                    translate_indices.append(idx)
            
            # Translate in batches
            for i in range(0, len(lines_to_translate), BATCH_SIZE):
                batch = lines_to_translate[i:i + BATCH_SIZE]
                batch_indices = translate_indices[i:i + BATCH_SIZE]
                
                # Add small delay between batches to avoid rate limits (except for first batch)
                if i > 0:
                    await asyncio.sleep(0.5)  # 500ms delay between batches
                
                try:
                    results = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        translate_batch_sync,
                        batch,
                        request.target_lang,
                        request.source_lang,
                        DEEPL_API_KEY
                    )
                    
                    for result, idx in zip(results, batch_indices):
                        overlay_lines[idx] = OverlayLine(
                            original=result['original_text'],
                            translated=result['translated_text']
                        )
                        if not detected_lang:
                            detected_lang = result.get('detected_language')
                except Exception as e:
                    # If batch translation fails, fall back to individual
                    print(f"Error translating batch: {e}, falling back to individual")
                    for text, idx in zip(batch, batch_indices):
                        try:
                            result = await asyncio.get_event_loop().run_in_executor(
                                executor,
                                translate_lyrics_sync,
                                text,
                                request.target_lang,
                                request.source_lang,
                                DEEPL_API_KEY
                            )
                            overlay_lines[idx] = OverlayLine(
                                original=result['original_text'],
                                translated=result['translated_text']
                            )
                        except Exception as e2:
                            print(f"Error translating line: {e2}")
                            overlay_lines[idx] = OverlayLine(
                                original=text,
                                translated=text
                            )
        
        return OverlayTranslationResponse(
            lines=overlay_lines,
            target_language=request.target_lang,
            detected_language=detected_lang
        )
    
    except InvalidLanguageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except TranslationError as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/translate-word", response_model=WordTranslationResponse)
async def translate_word(request: WordTranslationRequest):
    """Translate a single word to the target language"""
    if not DEEPL_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DeepL API key not configured. Set DEEPL_API_KEY environment variable."
        )
    
    try:
        # Clean the word (remove punctuation for better translation)
        import re
        clean_word = re.sub(r'[^\w\s]', '', request.word).strip()
        
        if not clean_word:
            # If word is just punctuation, return as-is
            return WordTranslationResponse(
                original_word=request.word,
                translated_word=request.word,
                target_language=request.target_lang
            )
        
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            translate_lyrics_sync,
            clean_word,
            request.target_lang,
            request.source_lang,
            DEEPL_API_KEY
        )
        
        return WordTranslationResponse(
            original_word=request.word,
            translated_word=result['translated_text'],
            target_language=request.target_lang,
            detected_language=result.get('detected_language')
        )
    
    except InvalidLanguageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except TranslationError as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    # Languages are hardcoded in the DeepLTranslator class, so we can access them directly
    try:
        languages = [
            {'code': code, 'name': name}
            for code, name in sorted(DeepLTranslator.SUPPORTED_LANGUAGES.items())
        ]
        return {"languages": languages}
    except Exception as e:
        # Final fallback
        languages = [
            {'code': 'EN', 'name': 'English'},
            {'code': 'ES', 'name': 'Spanish'},
            {'code': 'FR', 'name': 'French'},
            {'code': 'DE', 'name': 'German'},
            {'code': 'IT', 'name': 'Italian'},
            {'code': 'PT', 'name': 'Portuguese'},
            {'code': 'JA', 'name': 'Japanese'},
            {'code': 'KO', 'name': 'Korean'},
            {'code': 'ZH', 'name': 'Chinese'},
        ]
        return {"languages": languages}


# All helper functions have been moved to separate modules:
# - spotify_helpers.py: encode_client_credentials
# - lyrics_helpers.py: get_lrc_lyrics, get_lyrics_ovh, get_genius_lyrics_sync
# - translation_helpers.py: translate_lyrics_sync, translate_batch_sync


async def __refresh_user_token(user_id: str):
    """Refresh the access token for a user"""
    if user_id not in user_tokens:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    refresh_token = user_tokens[user_id].get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token available")
    
    async with httpx.AsyncClient() as client:
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        auth_header = f"Basic {encode_client_credentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)}"
        
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data=token_data,
            headers={"Authorization": auth_header},
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh token")
        
        token_info = response.json()
        user_tokens[user_id]["access_token"] = token_info["access_token"]
        if "refresh_token" in token_info:
            user_tokens[user_id]["refresh_token"] = token_info["refresh_token"]


@app.get("/top-artists/{genre}")
async def get_top_artists(genre: str, limit: int = 10):
    """
    Get top artists by genre/search query using Spotify API.
    Uses the helper functions from spotify_helpers.
    
    Args:
        genre: Search query (e.g., "french", "k-pop", "bad bunny")
        limit: Maximum number of artists to return (default: 10)
    
    Returns:
        List of top artists with their information
    """
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Spotify credentials not configured"
        )
    
    try:
        # Get access token using helper function
        token = await get_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        
        # Get top artists using helper function
        artists = await get_top_artists_by_genre(token, genre, limit)
        
        # Get top tracks for all artists concurrently
        all_tracks = await get_all_artists_top_tracks(token, artists, limit=10)
        
        # Format response
        result = []
        for artist in artists:
            artist_data = all_tracks.get(artist["name"], {})
            tracks = artist_data.get("tracks", [])
            
            result.append({
                "id": artist["id"],
                "name": artist["name"],
                "image": artist["image"],
                "popularity": artist["popularity"],
                "top_tracks": [track["name"] for track in tracks]
            })
        
        return {"artists": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top artists: {str(e)}"
        )


@app.post("/analyze-lyrics", response_model=LyricsAnalysisResponse)
async def analyze_song_lyrics(request: LyricsAnalysisRequest):
    """
    Analyze song lyrics using Google AI Studio to extract summary and language-specific insights.
    
    Args:
        request: Contains the lyrics to analyze
        
    Returns:
        Summary and list of language-specific insights (idioms, puns, wordplay, etc.)
    """
    try:
        # Run the synchronous analyze_lyrics function in executor
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            analyze_lyrics,
            request.lyrics
        )
        
        return LyricsAnalysisResponse(
            summary=result.get("summary", ""),
            insights=result.get("insights", [])
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze lyrics: {str(e)}"
        )

