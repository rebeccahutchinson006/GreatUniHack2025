"""
Integrated module for translating and reading out lyrics in multiple languages.
Combines DeepL translation with Eleven Labs TTS.
"""
from typing import Optional, Dict, List
import os
from pathlib import Path

from .deepl_translator import DeepLTranslator
from .elevenlabs_tts import ElevenLabsTTS
from .audio_player import AudioPlayer
from .lyric_formatter import LyricFormatter
from .exceptions import TranslationError


class LyricsTTSError(TranslationError):
    """Exception for Lyrics TTS errors"""
    pass


class LyricsTTS:
    """
    Complete solution for translating and reading out lyrics in multiple languages.
    
    Combines:
    - DeepL translation for accurate lyric translation
    - Eleven Labs TTS for natural-sounding speech in multiple languages
    - Audio playback capabilities
    - Lyric formatting and preprocessing
    
    Example:
        >>> lyrics_tts = LyricsTTS(
        ...     deepl_api_key="your-deepl-key",
        ...     elevenlabs_api_key="your-elevenlabs-key"
        ... )
        >>> 
        >>> # Translate and generate audio
        >>> result = lyrics_tts.translate_and_speak(
        ...     lyrics="Hello, how are you?",
        ...     target_lang="ES",
        ...     output_path="output.mp3"
        ... )
        >>> 
        >>> # Play the audio
        >>> lyrics_tts.play_audio(result['audio_path'])
    """
    
    def __init__(
        self,
        deepl_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        use_cache: bool = True
    ):
        """
        Initialize the integrated Lyrics TTS system.
        
        Args:
            deepl_api_key: DeepL API key (or set DEEPL_API_KEY env var).
            elevenlabs_api_key: Eleven Labs API key (or set ELEVENLABS_API_KEY env var).
            use_cache: Whether to use Redis caching for translations.
        
        Raises:
            LyricsTTSError: If API keys are missing.
        """
        try:
            self.translator = DeepLTranslator(
                api_key=deepl_api_key,
                use_cache=use_cache
            )
        except Exception as e:
            raise LyricsTTSError(f"Failed to initialize translator: {str(e)}")
        
        try:
            self.tts = ElevenLabsTTS(api_key=elevenlabs_api_key)
        except Exception as e:
            raise LyricsTTSError(f"Failed to initialize TTS: {str(e)}")
        
        self.formatter = LyricFormatter()
        self.player = None  # Lazy initialization
    
    def _get_player(self) -> AudioPlayer:
        """Lazy initialization of audio player."""
        if self.player is None:
            self.player = AudioPlayer()
        return self.player
    
    def translate_lyrics(
        self,
        lyrics: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        preserve_formatting: bool = True
    ) -> Dict:
        """
        Translate lyrics to target language.
        
        Args:
            lyrics: The lyrics text to translate.
            target_lang: Target language code (e.g., 'ES', 'FR', 'DE', 'JA').
            source_lang: Source language code (auto-detected if None).
            preserve_formatting: Whether to preserve line breaks and formatting.
        
        Returns:
            Dictionary with translation results including 'translated_text'.
        """
        return self.translator.translate_lyrics(
            text=lyrics,
            target_lang=target_lang,
            source_lang=source_lang,
            preserve_formatting=preserve_formatting
        )
    
    def generate_audio(
        self,
        lyrics: str,
        output_path: str,
        language: str = "en",
        voice_name: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Dict:
        """
        Generate audio from lyrics.
        
        Args:
            lyrics: The lyrics text to convert to speech.
            output_path: Where to save the audio file.
            language: Language code for the lyrics.
            voice_name: Name of the voice to use.
            voice_id: ID of the voice (alternative to voice_name).
            model_id: TTS model to use.
            stability: Voice stability (0.0-1.0).
            similarity_boost: Voice similarity (0.0-1.0).
        
        Returns:
            Dictionary with audio generation results.
        """
        if voice_id:
            audio_path = self.tts.text_to_speech_file(
                text=lyrics,
                output_path=output_path,
                voice_id=voice_id,
                model_id=model_id,
                stability=stability,
                similarity_boost=similarity_boost
            )
            return {
                'audio_path': audio_path,
                'voice_id': voice_id
            }
        else:
            return self.tts.generate_lyrics_audio(
                lyrics=lyrics,
                output_path=output_path,
                language=language,
                voice_name=voice_name
            )
    
    def translate_and_speak(
        self,
        lyrics: str,
        target_lang: str,
        output_path: str,
        source_lang: Optional[str] = None,
        voice_name: Optional[str] = None,
        voice_id: Optional[str] = None,
        preserve_formatting: bool = True,
        auto_play: bool = False
    ) -> Dict:
        """
        Translate lyrics and generate audio in one step.
        
        Args:
            lyrics: Original lyrics text.
            target_lang: Target language code (e.g., 'ES', 'FR', 'DE', 'JA').
            output_path: Where to save the generated audio.
            source_lang: Source language (auto-detected if None).
            voice_name: Name of the voice to use.
            voice_id: ID of the voice (alternative to voice_name).
            preserve_formatting: Whether to preserve lyric formatting.
            auto_play: Whether to automatically play the audio after generation.
        
        Returns:
            Dictionary with translation and audio results including:
            - 'original_text': Original lyrics
            - 'translated_text': Translated lyrics
            - 'target_lang': Target language code
            - 'audio_path': Path to generated audio file
            - 'voice_name': Name of the voice used
            - 'voice_id': ID of the voice used
        
        Example:
            >>> result = lyrics_tts.translate_and_speak(
            ...     lyrics="I love music",
            ...     target_lang="ES",
            ...     output_path="spanish.mp3",
            ...     auto_play=True
            ... )
            >>> print(result['translated_text'])
            Me encanta la música
        """
        # Step 1: Translate lyrics
        translation_result = self.translate_lyrics(
            lyrics=lyrics,
            target_lang=target_lang,
            source_lang=source_lang,
            preserve_formatting=preserve_formatting
        )
        
        translated_text = translation_result['translated_text']
        
        # Step 2: Determine best voice if not specified
        if not voice_name and not voice_id:
            # Try to use the best voice for this language from the predefined mapping
            suggested_voice = self.tts.get_best_voice_for_language(target_lang)
            
            # Verify the suggested voice exists before using it
            if suggested_voice:
                try:
                    voice_check = self.tts.get_voice_by_name(suggested_voice)
                    if voice_check:
                        voice_name = suggested_voice
                    # If not found, voice_name stays None and will auto-select
                except Exception:
                    # If there's any error checking the voice, fall back to auto-select
                    pass
        
        # Step 3: Generate audio from translated lyrics
        # Map language codes to ISO codes for TTS
        lang_map = {
            'ES': 'es', 'FR': 'fr', 'DE': 'de', 'IT': 'it',
            'JA': 'ja', 'ZH': 'zh', 'KO': 'ko', 'PT': 'pt',
            'RU': 'ru', 'AR': 'ar', 'NL': 'nl', 'PL': 'pl',
            'EN': 'en', 'EN-GB': 'en', 'EN-US': 'en'
        }
        language_code = lang_map.get(target_lang.upper(), 'en')
        
        audio_result = self.generate_audio(
            lyrics=translated_text,
            output_path=output_path,
            language=language_code,
            voice_name=voice_name,
            voice_id=voice_id
        )
        
        # Combine results
        result = {
            'original_text': lyrics,
            'translated_text': translated_text,
            'source_lang': translation_result.get('source_lang'),
            'target_lang': target_lang,
            'audio_path': audio_result['audio_path'],
            'voice_name': audio_result.get('voice_name'),
            'voice_id': audio_result.get('voice_id')
        }
        
        # Auto-play if requested
        if auto_play:
            self.play_audio(audio_result['audio_path'])
        
        return result
    
    def batch_translate_and_speak(
        self,
        lyrics: str,
        target_languages: List[str],
        output_dir: str,
        base_filename: str = "lyrics",
        source_lang: Optional[str] = None,
        voice_settings: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Translate and generate audio for lyrics in multiple languages.
        
        Args:
            lyrics: Original lyrics text.
            target_languages: List of target language codes.
            output_dir: Directory to save all audio files.
            base_filename: Base name for output files.
            source_lang: Source language (auto-detected if None).
            voice_settings: Optional dict mapping language codes to voice names/IDs.
        
        Returns:
            List of result dictionaries, one for each language.
        
        Example:
            >>> results = lyrics_tts.batch_translate_and_speak(
            ...     lyrics="I love music",
            ...     target_languages=['ES', 'FR', 'DE', 'JA'],
            ...     output_dir="./multilingual_lyrics"
            ... )
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        voice_settings = voice_settings or {}
        
        for lang in target_languages:
            output_path = os.path.join(
                output_dir,
                f"{base_filename}_{lang.lower()}.mp3"
            )
            
            # Get voice for this language if specified
            voice_name = voice_settings.get(lang)
            
            try:
                result = self.translate_and_speak(
                    lyrics=lyrics,
                    target_lang=lang,
                    output_path=output_path,
                    source_lang=source_lang,
                    voice_name=voice_name
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'target_lang': lang,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def play_audio(self, audio_path: str, blocking: bool = True):
        """
        Play an audio file.
        
        Args:
            audio_path: Path to the audio file.
            blocking: If True, wait for playback to complete.
        """
        player = self._get_player()
        player.play(audio_path, blocking=blocking)
    
    def get_available_voices(self) -> List[Dict]:
        """
        Get all available TTS voices.
        
        Returns:
            List of voice dictionaries with name, voice_id, and language info.
        """
        return self.tts.get_voices()
    
    def get_multilingual_voices(self) -> List[Dict]:
        """
        Get voices that support multiple languages.
        
        Returns:
            List of multilingual voice dictionaries.
        """
        return self.tts.get_multilingual_voices()
    
    def filter_voices_by_characteristics(
        self,
        gender: Optional[str] = None,
        accent: Optional[str] = None,
        age: Optional[str] = None,
        use_case: Optional[str] = None,
        description: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter voices by specific characteristics.
        
        Args:
            gender: Filter by gender (e.g., "male", "female").
            accent: Filter by accent (e.g., "british", "american", "australian").
            age: Filter by age (e.g., "young", "middle aged", "old").
            use_case: Filter by use case (e.g., "narration", "news", "conversational").
            description: Filter by description text (case-insensitive substring match).
        
        Returns:
            List of voices matching the specified criteria.
        
        Example:
            >>> lyrics_tts = LyricsTTS()
            >>> # Find female British voices
            >>> voices = lyrics_tts.filter_voices_by_characteristics(
            ...     gender='female',
            ...     accent='british'
            ... )
            >>> for voice in voices:
            ...     print(f"{voice['name']} - {voice.get('labels', {})}")
        """
        return self.tts.filter_voices_by_characteristics(
            gender=gender,
            accent=accent,
            age=age,
            use_case=use_case,
            description=description
        )
    
    def get_recommended_voices(
        self,
        target_lang: str,
        preferences: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Get recommended voices for a specific language with optional preferences.
        
        This implements the "best voice for each language" approach from the
        Voice Selection Guide. It intelligently selects appropriate voices based on:
        - Language compatibility (prefers multilingual voices for non-English)
        - Accent matching (e.g., Spanish voice for Spanish translation)
        - User preferences (gender, accent, age, use case)
        
        Args:
            target_lang: Target language code (e.g., 'ES', 'FR', 'DE', 'JA').
            preferences: Optional dict with voice preferences:
                        - 'gender': 'male' or 'female'
                        - 'accent': specific accent preference
                        - 'age': 'young', 'middle aged', 'old'
                        - 'use_case': 'narration', 'news', 'conversational'
        
        Returns:
            Dictionary with:
            - 'recommended': The top recommended voice (or None for auto-select)
            - 'alternatives': List of alternative voices
            - 'all_matching': All voices that match the criteria
        
        Example:
            >>> lyrics_tts = LyricsTTS()
            >>> # Get recommended voice for Spanish with female preference
            >>> result = lyrics_tts.get_recommended_voices(
            ...     'ES',
            ...     preferences={'gender': 'female'}
            ... )
            >>> print(f"Recommended: {result['recommended']['name']}")
            >>> print(f"Alternatives: {[v['name'] for v in result['alternatives'][:3]]}")
        """
        # Get the primary recommendation
        recommended_voice = self.tts.get_voice_for_language(
            target_lang,
            preferences=preferences
        )
        
        # Get all matching voices for alternatives
        all_matching = []
        
        # For non-English, start with multilingual voices
        if target_lang.upper() not in ['EN', 'EN-GB', 'EN-US']:
            all_matching = self.get_multilingual_voices()
        else:
            all_matching = self.get_available_voices()
        
        # Apply preference filters if provided
        if preferences:
            for key, value in preferences.items():
                if key == 'gender':
                    all_matching = [
                        v for v in all_matching
                        if v.get('labels', {}).get('gender') == value
                    ]
                elif key == 'accent':
                    all_matching = [
                        v for v in all_matching
                        if value.lower() in str(v.get('labels', {}).get('accent', '')).lower()
                    ]
                elif key == 'age':
                    all_matching = [
                        v for v in all_matching
                        if v.get('labels', {}).get('age') == value
                    ]
                elif key == 'use_case':
                    all_matching = [
                        v for v in all_matching
                        if v.get('labels', {}).get('use case') == value
                    ]
        
        # Prepare alternatives (exclude the recommended one)
        alternatives = []
        if recommended_voice:
            alternatives = [
                v for v in all_matching
                if v.get('voice_id') != recommended_voice.get('voice_id')
            ]
        else:
            alternatives = all_matching
        
        return {
            'recommended': recommended_voice,
            'alternatives': alternatives[:5],  # Top 5 alternatives
            'all_matching': all_matching
        }
    
    def get_supported_languages(self) -> List[Dict]:
        """
        Get supported translation languages.
        
        Returns:
            List of language dictionaries with code and name.
        """
        return self.translator.get_supported_languages()
    
    def get_usage_stats(self) -> Dict:
        """
        Get API usage statistics for both services.
        
        Returns:
            Dictionary with usage stats for DeepL and Eleven Labs.
        """
        return {
            'deepl': self.translator.get_usage_stats(),
            'elevenlabs': self.tts.get_user_info()
        }