# Eleven Labs TTS Integration Guide

Complete guide for using Eleven Labs text-to-speech to read out lyrics in multiple languages.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Supported Languages](#supported-languages)
- [Voice Selection](#voice-selection)
- [Audio Playback](#audio-playback)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Eleven Labs TTS integration allows you to:
- Convert lyrics to natural-sounding speech in 29+ languages
- Automatically translate lyrics and generate audio
- Use multilingual voices for consistent quality across languages
- Play audio directly or save to files
- Batch process lyrics in multiple languages

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

You need two API keys:

**Eleven Labs API Key:**
1. Sign up at [ElevenLabs.io](https://elevenlabs.io)
2. Go to Profile Settings → API Keys
3. Copy your API key

**DeepL API Key** (for translation):
1. Sign up at [DeepL.com/pro](https://www.deepl.com/pro-api)
2. Get your free API key

### 3. Set Environment Variables

```bash
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export DEEPL_API_KEY="your-deepl-api-key"
```

Or create a `.env` file:
```bash
ELEVENLABS_API_KEY=your-elevenlabs-api-key
DEEPL_API_KEY=your-deepl-api-key
```

### 4. Install Audio Player (Linux only)

For audio playback on Linux, install one of:
```bash
# Ubuntu/Debian
sudo apt-get install mpg123
# or
sudo apt-get install ffmpeg

# Fedora
sudo dnf install mpg123
```

macOS and Windows have built-in audio players.

## Quick Start

### Basic Translation + TTS

```python
from translation_library import LyricsTTS

# Initialize
lyrics_tts = LyricsTTS()

# Translate English to Spanish and generate audio
result = lyrics_tts.translate_and_speak(
    lyrics="Hello, how are you today?",
    target_lang="ES",
    output_path="spanish.mp3",
    auto_play=True
)

print(result['translated_text'])  # "Hola, ¿cómo estás hoy?"
```

### Multiple Languages

```python
# Generate audio in 5 languages
languages = ['ES', 'FR', 'DE', 'IT', 'JA']

results = lyrics_tts.batch_translate_and_speak(
    lyrics="I love music!",
    target_languages=languages,
    output_dir="multilingual_output"
)
```

### Without Translation (Direct TTS)

```python
# Just generate audio without translation
result = lyrics_tts.generate_audio(
    lyrics="Bonjour, comment allez-vous?",
    output_path="french.mp3",
    language="fr"
)
```

## API Reference

### LyricsTTS Class

#### `__init__(deepl_api_key, elevenlabs_api_key, use_cache=True)`

Initialize the integrated TTS system.

**Parameters:**
- `deepl_api_key` (str, optional): DeepL API key
- `elevenlabs_api_key` (str, optional): Eleven Labs API key
- `use_cache` (bool): Enable Redis caching for translations

#### `translate_and_speak(lyrics, target_lang, output_path, ...)`

Translate lyrics and generate audio in one step.

**Parameters:**
- `lyrics` (str): Original lyrics text
- `target_lang` (str): Target language code (e.g., 'ES', 'FR', 'JA')
- `output_path` (str): Where to save the audio file
- `source_lang` (str, optional): Source language (auto-detected if None)
- `voice_name` (str, optional): Specific voice to use
- `voice_id` (str, optional): Voice ID (alternative to voice_name)
- `preserve_formatting` (bool): Keep line breaks (default: True)
- `auto_play` (bool): Automatically play after generation (default: False)

**Returns:** Dictionary with:
- `original_text`: Original lyrics
- `translated_text`: Translated lyrics
- `audio_path`: Path to generated audio
- `voice_name`: Voice used
- `voice_id`: Voice ID used

#### `generate_audio(lyrics, output_path, language, ...)`

Generate audio without translation.

**Parameters:**
- `lyrics` (str): Text to convert to speech
- `output_path` (str): Where to save audio
- `language` (str): Language code ('en', 'es', 'fr', etc.)
- `voice_name` (str, optional): Voice to use
- `voice_id` (str, optional): Voice ID
- `model_id` (str): TTS model (default: 'eleven_multilingual_v2')
- `stability` (float): Voice stability 0.0-1.0 (default: 0.5)
- `similarity_boost` (float): Voice similarity 0.0-1.0 (default: 0.75)

#### `batch_translate_and_speak(lyrics, target_languages, output_dir, ...)`

Generate audio in multiple languages.

**Parameters:**
- `lyrics` (str): Original lyrics
- `target_languages` (list): List of language codes
- `output_dir` (str): Directory for output files
- `base_filename` (str): Base name for files (default: 'lyrics')
- `source_lang` (str, optional): Source language
- `voice_settings` (dict, optional): Map of lang→voice_name

**Returns:** List of result dictionaries

#### `play_audio(audio_path, blocking=True)`

Play an audio file.

#### `get_available_voices()`

Get all available TTS voices.

#### `get_multilingual_voices()`

Get voices supporting multiple languages.

#### `get_supported_languages()`

Get supported translation languages.

#### `get_usage_stats()`

Get API usage statistics.

### ElevenLabsTTS Class

For direct TTS usage without translation:

```python
from translation_library import ElevenLabsTTS

tts = ElevenLabsTTS(api_key="your-key")

# Generate audio
audio_data = tts.text_to_speech(
    text="Hello world",
    voice_name="Rachel",
    model_id="eleven_multilingual_v2"
)

# Save to file
tts.text_to_speech_file(
    text="Hello world",
    output_path="hello.mp3",
    voice_name="Rachel"
)
```

## Examples

### Example 1: Song Lyrics Translation

```python
from translation_library import LyricsTTS

lyrics_tts = LyricsTTS()

song_lyrics = """
In the morning light
I see your face
Every moment with you
Is pure grace
"""

# Translate to Japanese and generate audio
result = lyrics_tts.translate_and_speak(
    lyrics=song_lyrics,
    target_lang="JA",
    output_path="song_japanese.mp3"
)

print(f"Japanese version saved to: {result['audio_path']}")
print(f"Translation:\n{result['translated_text']}")
```

### Example 2: Multiple Language Versions

```python
# Create versions in 5 languages
languages = {
    'ES': 'Spanish',
    'FR': 'French', 
    'DE': 'German',
    'IT': 'Italian',
    'PT': 'Portuguese'
}

for lang_code, lang_name in languages.items():
    result = lyrics_tts.translate_and_speak(
        lyrics=song_lyrics,
        target_lang=lang_code,
        output_path=f"song_{lang_code.lower()}.mp3"
    )
    print(f"{lang_name} version created!")
```

### Example 3: Custom Voice Selection

```python
# List available multilingual voices
voices = lyrics_tts.get_multilingual_voices()

for voice in voices:
    print(f"{voice['name']}: {voice['voice_id']}")

# Use specific voice
result = lyrics_tts.translate_and_speak(
    lyrics="Beautiful day",
    target_lang="FR",
    output_path="french.mp3",
    voice_name="Bella"  # Use a specific voice
)
```

### Example 4: Batch Processing with Custom Voices

```python
# Different voices for different languages
voice_settings = {
    'ES': 'Matilda',
    'FR': 'Charlotte',
    'DE': 'Daniel',
    'IT': 'Gianna'
}

results = lyrics_tts.batch_translate_and_speak(
    lyrics="Good morning, sunshine!",
    target_languages=['ES', 'FR', 'DE', 'IT'],
    output_dir="output",
    voice_settings=voice_settings
)
```

### Example 5: Stream and Play

```python
# Generate and play immediately
result = lyrics_tts.translate_and_speak(
    lyrics="Let's dance!",
    target_lang="ES",
    output_path="dance.mp3",
    auto_play=True  # Play immediately after generation
)
```

## Supported Languages

### Translation Languages (DeepL)
Arabic (AR), Bulgarian (BG), Czech (CS), Danish (DA), German (DE), Greek (EL), English (EN), Spanish (ES), Estonian (ET), Finnish (FI), French (FR), Hungarian (HU), Indonesian (ID), Italian (IT), Japanese (JA), Korean (KO), Lithuanian (LT), Latvian (LV), Norwegian (NB), Dutch (NL), Polish (PL), Portuguese (PT), Romanian (RO), Russian (RU), Slovak (SK), Slovenian (SL), Swedish (SV), Turkish (TR), Ukrainian (UK), Chinese (ZH)

### TTS Languages (Eleven Labs Multilingual v2)
English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Swedish, Czech, Arabic, Chinese, Japanese, Korean, Hindi, and more.

## Voice Selection

### Listing Voices

```python
# Get all voices
all_voices = lyrics_tts.get_available_voices()

# Get only multilingual voices
multilingual = lyrics_tts.get_multilingual_voices()

for voice in multilingual:
    print(f"Name: {voice['name']}")
    print(f"ID: {voice['voice_id']}")
    print(f"Languages: {voice.get('labels', {})}")
```

### Recommended Voices for Lyrics

**For Music/Songs:**
- Use `stability: 0.3-0.5` for more expressive delivery
- Use `style: 0.3-0.5` for emotional variation

**For Narration:**
- Use `stability: 0.6-0.8` for consistent delivery
- Use `style: 0.0-0.2` for neutral tone

### Voice Parameters

```python
result = lyrics_tts.generate_audio(
    lyrics="Your lyrics here",
    output_path="output.mp3",
    language="en",
    stability=0.4,          # Lower = more variable, higher = consistent
    similarity_boost=0.75,  # How close to original voice
    style=0.3              # Exaggeration of style (0.0-1.0)
)
```

## Audio Playback

### Cross-Platform Playback

```python
from translation_library import AudioPlayer

player = AudioPlayer()

# Play and wait for completion
player.play("audio.mp3", blocking=True)

# Play in background
process = player.play("audio.mp3", blocking=False)
# ... do other things ...
player.stop(process)  # Stop playback
```

### Streaming Playback

```python
from translation_library import StreamingAudioPlayer, ElevenLabsTTS

tts = ElevenLabsTTS()
stream_player = StreamingAudioPlayer()

# Generate audio data
audio_bytes = tts.text_to_speech(
    text="Hello",
    voice_name="Rachel"
)

# Play directly without saving to file
stream_player.play_bytes(audio_bytes, blocking=True)
```

## Best Practices

### 1. Character Limits

Free Eleven Labs accounts have monthly character limits. For long lyrics:

```python
from translation_library import LyricFormatter

formatter = LyricFormatter()

# Split long lyrics into segments
segments = formatter.split_into_segments(long_lyrics, max_segment_length=500)

# Process each segment
for i, segment in enumerate(segments):
    result = lyrics_tts.translate_and_speak(
        lyrics=segment,
        target_lang="ES",
        output_path=f"segment_{i}.mp3"
    )
```

### 2. Caching Translations

Enable caching to avoid re-translating:

```python
# With caching (requires Redis)
lyrics_tts = LyricsTTS(use_cache=True)

# Without caching
lyrics_tts = LyricsTTS(use_cache=False)
```

### 3. Error Handling

```python
from translation_library import LyricsTTSError, AudioGenerationError

try:
    result = lyrics_tts.translate_and_speak(
        lyrics="Test",
        target_lang="ES",
        output_path="output.mp3"
    )
except AudioGenerationError as e:
    print(f"Audio generation failed: {e}")
except LyricsTTSError as e:
    print(f"TTS error: {e}")
```

### 4. Voice Consistency

For a series of songs, use the same voice:

```python
voice_id = "your-preferred-voice-id"

for song in song_list:
    result = lyrics_tts.translate_and_speak(
        lyrics=song['lyrics'],
        target_lang="FR",
        output_path=f"{song['title']}_fr.mp3",
        voice_id=voice_id
    )
```

## Troubleshooting

### "No API key provided"

Solution: Set environment variables:
```bash
export ELEVENLABS_API_KEY="your-key"
export DEEPL_API_KEY="your-key"
```

### "No audio player found" (Linux)

Solution: Install an audio player:
```bash
sudo apt-get install mpg123
```

### "Rate limit exceeded"

Solution: Check your usage and wait, or upgrade your plan:
```python
stats = lyrics_tts.get_usage_stats()
print(stats['elevenlabs'])
```

### Audio Quality Issues

Solution: Adjust voice parameters:
```python
result = lyrics_tts.generate_audio(
    lyrics=text,
    output_path="output.mp3",
    stability=0.7,          # Increase for more consistent voice
    similarity_boost=0.8,   # Increase for better quality
    use_speaker_boost=True  # Enable for clarity
)
```

### Import Errors

Solution: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Additional Resources

- [Eleven Labs Documentation](https://docs.elevenlabs.io/)
- [DeepL API Documentation](https://www.deepl.com/docs-api)
- [Example Scripts](./examples/)
- [Main README](./README.md)

## Support

For issues specific to this library, please check:
1. The [examples](./examples/) directory
2. This guide's troubleshooting section
3. API provider documentation

For API-specific issues:
- Eleven Labs: [support@elevenlabs.io](mailto:support@elevenlabs.io)
- DeepL: [support@deepl.com](mailto:support@deepl.com)