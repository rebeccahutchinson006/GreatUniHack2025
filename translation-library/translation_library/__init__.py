"""
DeepL Lyrics Translator Library with Eleven Labs TTS Integration

A Python library for translating song lyrics using the DeepL API,
with Eleven Labs text-to-speech, caching, formatting, and music-specific optimizations.
"""

from .deepl_translator import DeepLTranslator
from .translation_cache import TranslationCache
from .exceptions import TranslationError, RateLimitError, InvalidLanguageError
from .elevenlabs_tts import ElevenLabsTTS, ElevenLabsError, VoiceNotFoundError, AudioGenerationError
from .audio_player import AudioPlayer, AudioPlaybackError, StreamingAudioPlayer
from .lyrics_tts import LyricsTTS, LyricsTTSError

__version__ = "0.2.0"
__all__ = [
    "DeepLTranslator",
    "LyricFormatter",
    "TranslationCache",
    "TranslationError",
    "RateLimitError",
    "InvalidLanguageError",
    "ElevenLabsTTS",
    "ElevenLabsError",
    "VoiceNotFoundError",
    "AudioGenerationError",
    "AudioPlayer",
    "AudioPlaybackError",
    "StreamingAudioPlayer",
    "LyricsTTS",
    "LyricsTTSError",
]