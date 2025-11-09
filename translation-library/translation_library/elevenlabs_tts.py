"""
Eleven Labs Text-to-Speech module for reading out lyrics in multiple languages.
"""
import os
import requests
import json
from typing import Optional, Dict, List, BinaryIO
from pathlib import Path
from .exceptions import TranslationError


# Default best voice recommendations per language
# These are commonly available voices that work well for each language.
# NOTE: If a suggested voice is not available in your account, the system
# will automatically fall back to selecting a suitable multilingual voice.
BEST_VOICES_PER_LANGUAGE = {
    'EN': 'Sarah',       # English - American female
    'EN-US': 'Sarah',    # English (US) - American female
    'EN-GB': 'Alice',    # English (UK) - British female
    'ES': 'Matilda',     # Spanish - female (supports multilingual)
    'FR': 'River',       # French - neutral voice (#7)
    'DE': 'Daniel',      # German - male
    'IT': 'River',       # Italian - neutral voice
    'PT': 'River',       # Portuguese - neutral voice
    'PT-BR': 'River',    # Portuguese (Brazil) - neutral voice
    'JA': 'Alice',       # Japanese - female (supports ja)
    'ZH': 'River',       # Chinese - neutral voice
    'KO': None,          # Korean - auto-select multilingual
    'RU': None,          # Russian - auto-select multilingual
    'AR': 'Sarah',       # Arabic - female (supports ar)
    'NL': 'Daniel',      # Dutch - male
    'PL': 'Alice',       # Polish - female (supports pl)
    'HI': 'Sarah',       # Hindi - female (supports hi)
    'CS': 'George',      # Czech - male (supports cs)
}


class ElevenLabsError(TranslationError):
    """Base exception for Eleven Labs TTS errors"""
    pass


class VoiceNotFoundError(ElevenLabsError):
    """Raised when a voice is not found"""
    pass


class AudioGenerationError(ElevenLabsError):
    """Raised when audio generation fails"""
    pass


class ElevenLabsTTS:
    """
    Eleven Labs Text-to-Speech integration for converting lyrics to speech.
    Supports multiple languages and voices.
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Eleven Labs TTS client.
        
        Args:
            api_key: Eleven Labs API key. If not provided, will try to get from
                    ELEVENLABS_API_KEY environment variable.
        
        Raises:
            ElevenLabsError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ElevenLabsError(
                "No API key provided. Set ELEVENLABS_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
    
    def get_voices(self) -> List[Dict]:
        """
        Get all available voices from Eleven Labs.
        
        Returns:
            List of voice dictionaries with name, voice_id, and language info.
        
        Raises:
            ElevenLabsError: If the API request fails.
        """
        url = f"{self.BASE_URL}/voices"
        
        try:
            response = requests.get(
                url,
                headers={"xi-api-key": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
            return data.get('voices', [])
        except requests.exceptions.RequestException as e:
            raise ElevenLabsError(f"Failed to fetch voices: {str(e)}")
    
    def get_voice_by_name(self, name: str) -> Optional[Dict]:
        """
        Find a voice by name.
        
        Args:
            name: The name of the voice to find.
        
        Returns:
            Voice dictionary if found, None otherwise.
        """
        voices = self.get_voices()
        for voice in voices:
            if voice.get('name', '').lower() == name.lower():
                return voice
        return None
    
    def get_multilingual_voices(self) -> List[Dict]:
        """
        Get voices that support multiple languages.
        
        Returns:
            List of multilingual voice dictionaries.
        """
        voices = self.get_voices()
        return [
            voice for voice in voices
            if 'multilingual' in voice.get('labels', {}).values()
        ]
    
    def get_best_voice_for_language(self, language_code: str) -> Optional[str]:
        """
        Get the best voice name for a specific language from the default mapping.
        
        Args:
            language_code: Language code (e.g., 'ES', 'FR', 'DE', 'en').
        
        Returns:
            Voice name string, or None to use auto-selection.
        
        Example:
            >>> tts = ElevenLabsTTS()
            >>> voice = tts.get_best_voice_for_language('ES')
            >>> print(voice)  # 'Matilda'
        """
        # Try exact match first (case-insensitive)
        lang_upper = language_code.upper()
        if lang_upper in BEST_VOICES_PER_LANGUAGE:
            return BEST_VOICES_PER_LANGUAGE[lang_upper]
        
        # Try lowercase version
        lang_lower = language_code.lower()
        for key in BEST_VOICES_PER_LANGUAGE:
            if key.lower() == lang_lower:
                return BEST_VOICES_PER_LANGUAGE[key]
        
        # Return None for auto-selection
        return None
    
    
    def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        speed: float = 1.0,
        use_speaker_boost: bool = True
    ) -> bytes:
        """
        Convert text to speech using Eleven Labs API.
        
        Args:
            text: The text to convert to speech (lyrics).
            voice_id: The ID of the voice to use. If not provided, voice_name must be given.
            voice_name: Name of the voice (e.g., "Rachel", "Adam"). Will look up voice_id.
            model_id: Model to use. Options:
                     - "eleven_multilingual_v2" (default, supports 29 languages)
                     - "eleven_monolingual_v1" (English only, highest quality)
                     - "eleven_turbo_v2" (fastest, good quality)
            stability: Voice stability (0.0-1.0). Higher = more consistent.
            similarity_boost: Voice similarity (0.0-1.0). Higher = closer to original voice.
            style: Style exaggeration (0.0-1.0). Higher = more expressive.
            use_speaker_boost: Whether to use speaker boost for better clarity.
        
        Returns:
            Audio data as bytes (MP3 format).
        
        Raises:
            VoiceNotFoundError: If the specified voice is not found.
            AudioGenerationError: If audio generation fails.
        """
        # Get voice_id if voice_name is provided
        if not voice_id and voice_name:
            voice = self.get_voice_by_name(voice_name)
            if not voice:
                raise VoiceNotFoundError(f"Voice '{voice_name}' not found")
            voice_id = voice['voice_id']
        elif not voice_id:
            raise ElevenLabsError("Either voice_id or voice_name must be provided")
        
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "speed": speed,
                "use_speaker_boost": use_speaker_boost
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                stream=True
            )
            response.raise_for_status()
            
            # Collect audio data
            audio_data = b''
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_data += chunk
            
            return audio_data
            
        except requests.exceptions.RequestException as e:
            raise AudioGenerationError(f"Failed to generate audio: {str(e)}")
    
    def text_to_speech_file(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        speed: float = 1.0,
        use_speaker_boost: bool = True
    ) -> str:
        """
        Convert text to speech and save to a file.
        
        Args:
            text: The text to convert to speech.
            output_path: Path where the audio file will be saved.
            voice_id: The ID of the voice to use.
            voice_name: Name of the voice (alternative to voice_id).
            model_id: Model to use for generation.
            stability: Voice stability (0.0-1.0).
            similarity_boost: Voice similarity (0.0-1.0).
            style: Style exaggeration (0.0-1.0).
            use_speaker_boost: Whether to use speaker boost.
        
        Returns:
            Path to the saved audio file.
        
        Raises:
            VoiceNotFoundError: If the specified voice is not found.
            AudioGenerationError: If audio generation or file saving fails.
        """
        audio_data = self.text_to_speech(
            text=text,
            voice_id=voice_id,
            voice_name=voice_name,
            model_id=model_id,
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            speed=speed,
            use_speaker_boost=use_speaker_boost
        )
        
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return output_path
            
        except IOError as e:
            raise AudioGenerationError(f"Failed to save audio file: {str(e)}")
    
    def generate_lyrics_audio(
        self,
        lyrics: str,
        output_path: str,
        language: str = "en",
        voice_name: Optional[str] = None,
        speed: float = 1.0,
        auto_select_voice: bool = True
    ) -> Dict[str, str]:
        """
        Generate audio for lyrics with language-specific optimization.
        
        Args:
            lyrics: The lyrics text to convert to speech.
            output_path: Path where the audio file will be saved.
            language: Language code (e.g., "en", "es", "fr", "de", "ja").
            voice_name: Specific voice to use. If not provided and auto_select_voice
                       is True, will select a suitable voice automatically.
            auto_select_voice: If True and no voice_name is given, automatically
                             select a suitable voice (prefers multilingual).
        
        Returns:
            Dictionary with 'audio_path', 'voice_name', and 'voice_id'.
        
        Raises:
            VoiceNotFoundError: If no suitable voice is found.
            AudioGenerationError: If audio generation fails.
        """
        voice_id = None
        selected_voice_name = voice_name
        model_id = "eleven_multilingual_v2"
        
        # Auto-select a voice if needed
        if not voice_name and auto_select_voice:
            # First try to get multilingual voices
            multilingual_voices = self.get_multilingual_voices()
            
            if multilingual_voices:
                # Use the first multilingual voice
                voice = multilingual_voices[0]
                voice_id = voice['voice_id']
                selected_voice_name = voice['name']
            else:
                # Fall back to ANY available voice
                all_voices = self.get_voices()
                if not all_voices:
                    raise VoiceNotFoundError("No voices available in your account")
                
                # Use the first available voice
                voice = all_voices[0]
                voice_id = voice['voice_id']
                selected_voice_name = voice['name']
                # Use monolingual model if no multilingual voices
                model_id = "eleven_monolingual_v1"
        
        # Generate audio
        audio_path = self.text_to_speech_file(
            text=lyrics,
            output_path=output_path,
            voice_id=voice_id,
            voice_name=voice_name,
            model_id=model_id,
            speed=speed,
        )
        
        return {
            'audio_path': audio_path,
            'voice_name': selected_voice_name,
            'voice_id': voice_id or self.get_voice_by_name(voice_name)['voice_id']
        }
    
    def get_user_info(self) -> Dict:
        """
        Get user subscription information and usage stats.
        
        Returns:
            Dictionary with user information including character quota.
        
        Raises:
            ElevenLabsError: If the API request fails.
        """
        url = f"{self.BASE_URL}/user"
        
        try:
            response = requests.get(
                url,
                headers={"xi-api-key": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ElevenLabsError(f"Failed to fetch user info: {str(e)}")