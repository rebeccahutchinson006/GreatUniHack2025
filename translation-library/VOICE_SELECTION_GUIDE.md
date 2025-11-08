# Voice Selection Guide

How to select specific voices for different languages when using Eleven Labs TTS.

## Quick Reference

### Method 1: Specify Voice by Name

```python
from translation_library import LyricsTTS

lyrics_tts = LyricsTTS()

result = lyrics_tts.translate_and_speak(
    lyrics="Hello, how are you?",
    target_lang="FR",
    output_path="french.mp3",
    voice_name="Charlotte"  # Specify voice name
)
```

### Method 2: Specify Voice by ID

```python
result = lyrics_tts.translate_and_speak(
    lyrics="Hello, how are you?",
    target_lang="ES",
    output_path="spanish.mp3",
    voice_id="your-voice-id-here"
)
```

### Method 3: Language-to-Voice Mapping

```python
# Define which voice to use for each language
language_voices = {
    'ES': 'Matilda',    # Spanish
    'FR': 'Charlotte',  # French
    'DE': 'Daniel',     # German
    'IT': 'Gianna',     # Italian
}

# Translate to Spanish with Matilda's voice
result = lyrics_tts.translate_and_speak(
    lyrics="Hello world",
    target_lang="ES",
    output_path="spanish.mp3",
    voice_name=language_voices['ES']
)
```

### Method 4: Batch Processing with Different Voices

```python
voice_settings = {
    'ES': 'Matilda',
    'FR': 'Charlotte',
    'DE': 'Daniel',
    'IT': 'Gianna',
}

results = lyrics_tts.batch_translate_and_speak(
    lyrics="Hello, how are you?",
    target_languages=['ES', 'FR', 'DE', 'IT'],
    output_dir="multilingual",
    voice_settings=voice_settings  # Map each language to a voice
)
```

## Discovering Available Voices

### List All Voices

```python
lyrics_tts = LyricsTTS()

# Get all voices
all_voices = lyrics_tts.get_available_voices()

for voice in all_voices:
    print(f"Name: {voice['name']}")
    print(f"ID: {voice['voice_id']}")
    print(f"Labels: {voice.get('labels', {})}")
    print()
```

### Get Multilingual Voices Only

```python
# Get voices that support multiple languages
multilingual = lyrics_tts.get_multilingual_voices()

for voice in multilingual:
    print(f"{voice['name']} - {voice['voice_id']}")
```

### Filter by Accent/Language

```python
all_voices = lyrics_tts.get_available_voices()

# Find British accent voices
british_voices = [
    v for v in all_voices
    if 'british' in str(v.get('labels', {}).get('accent', '')).lower()
]

# Find American accent voices
american_voices = [
    v for v in all_voices
    if 'american' in str(v.get('labels', {}).get('accent', '')).lower()
]
```

## Common Voice Selection Patterns

### Pattern 1: Use Best Voice for Each Language

```python
# Define your preferred voices per language
VOICE_PREFERENCES = {
    'EN': 'Rachel',      # English
    'ES': 'Matilda',     # Spanish
    'FR': 'Charlotte',   # French
    'DE': 'Daniel',      # German
    'IT': 'Gianna',      # Italian
    'PT': 'Camila',      # Portuguese
    'JA': None,          # Japanese - auto-select
}

def translate_with_preferred_voice(lyrics, target_lang):
    """Translate using language-specific voice preference"""
    voice_name = VOICE_PREFERENCES.get(target_lang)
    
    return lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang=target_lang,
        output_path=f"{target_lang.lower()}.mp3",
        voice_name=voice_name  # Will auto-select if None
    )

# Use it
result = translate_with_preferred_voice("Hello", "ES")
```

### Pattern 2: Interactive Voice Selection

```python
def choose_voice_interactively():
    """Let user choose voice from available options"""
    lyrics_tts = LyricsTTS()
    voices = lyrics_tts.get_available_voices()
    
    print("Available voices:")
    for i, voice in enumerate(voices, 1):
        accent = voice.get('labels', {}).get('accent', 'Unknown')
        print(f"{i}. {voice['name']} ({accent})")
    
    choice = int(input("\nSelect voice number: ")) - 1
    selected_voice = voices[choice]['name']
    
    return selected_voice

# Use it
voice_name = choose_voice_interactively()
result = lyrics_tts.translate_and_speak(
    lyrics="Your text here",
    target_lang="ES",
    output_path="output.mp3",
    voice_name=voice_name
)
```

### Pattern 3: Dynamic Voice Selection Based on Content

```python
def select_voice_by_mood(lyrics, target_lang):
    """Select voice based on lyric content mood"""
    lyrics_tts = LyricsTTS()
    
    # Simple mood detection (you could use AI for this)
    if any(word in lyrics.lower() for word in ['happy', 'joy', 'dance']):
        mood = 'energetic'
    elif any(word in lyrics.lower() for word in ['sad', 'cry', 'lonely']):
        mood = 'calm'
    else:
        mood = 'neutral'
    
    # Define mood-to-voice mapping
    mood_voices = {
        'energetic': 'Matilda',
        'calm': 'Charlotte',
        'neutral': 'Rachel',
    }
    
    voice_name = mood_voices.get(mood)
    
    return lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang=target_lang,
        output_path=f"{mood}_{target_lang}.mp3",
        voice_name=voice_name
    )
```

## Voice Characteristics

When selecting voices, consider these characteristics available in voice labels:

- **accent**: e.g., "american", "british", "australian"
- **age**: e.g., "young", "middle aged", "old"
- **gender**: e.g., "male", "female"
- **use case**: e.g., "narration", "news", "conversational"

### Example: Filter by Characteristics

```python
def find_voices_by_characteristics(gender=None, accent=None, age=None):
    """Find voices matching specific characteristics"""
    lyrics_tts = LyricsTTS()
    voices = lyrics_tts.get_available_voices()
    
    matching = []
    for voice in voices:
        labels = voice.get('labels', {})
        
        if gender and labels.get('gender') != gender:
            continue
        if accent and accent.lower() not in str(labels.get('accent', '')).lower():
            continue
        if age and labels.get('age') != age:
            continue
        
        matching.append(voice)
    
    return matching

# Find female British voices
female_british = find_voices_by_characteristics(
    gender='female',
    accent='british'
)

for voice in female_british:
    print(voice['name'])
```

## Tips

1. **Test voices first**: Generate short samples with different voices to find what works best
2. **Consider your audience**: Different accents may be more familiar to different audiences
3. **Match voice to content**: Use energetic voices for upbeat lyrics, calm voices for ballads
4. **Save your preferences**: Create a configuration file with your favorite voices per language
5. **Auto-select when uncertain**: Use `voice_name=None` to let the system choose

## Complete Example

```python
from translation_library import LyricsTTS
import json

# Save your voice preferences
VOICE_CONFIG = {
    "spanish": "Matilda",
    "french": "Charlotte",
    "german": "Daniel",
    "italian": "Gianna",
    "japanese": None,  # Auto-select
}

def translate_song_multilingual(lyrics, languages):
    """Translate a song to multiple languages with appropriate voices"""
    lyrics_tts = LyricsTTS()
    results = []
    
    # Language code to config key mapping
    lang_map = {
        'ES': 'spanish',
        'FR': 'french',
        'DE': 'german',
        'IT': 'italian',
        'JA': 'japanese',
    }
    
    for lang_code in languages:
        config_key = lang_map.get(lang_code)
        voice_name = VOICE_CONFIG.get(config_key) if config_key else None
        
        result = lyrics_tts.translate_and_speak(
            lyrics=lyrics,
            target_lang=lang_code,
            output_path=f"song_{lang_code.lower()}.mp3",
            voice_name=voice_name
        )
        
        results.append({
            'language': lang_code,
            'translation': result['translated_text'],
            'audio': result['audio_path'],
            'voice': result['voice_name']
        })
    
    return results

# Use it
song_lyrics = """
In the morning light
I see your face
Every moment with you
Is pure grace
"""

results = translate_song_multilingual(
    song_lyrics,
    ['ES', 'FR', 'DE', 'IT', 'JA']
)

# Print results
for r in results:
    print(f"\n{r['language']}:")
    print(f"  Voice: {r['voice']}")
    print(f"  Audio: {r['audio']}")
    print(f"  Translation: {r['translation'][:50]}...")
```

## See Also

- [`language_specific_voices.py`](examples/language_specific_voices.py) - Complete working examples
- [Eleven Labs TTS Guide](ELEVENLABS_TTS_GUIDE.md) - Full API documentation
- [Quick Start Guide](QUICKSTART_TTS.md) - Getting started