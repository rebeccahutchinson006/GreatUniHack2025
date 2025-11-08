# Quick Start: Eleven Labs TTS Integration

Get started with translating and speaking lyrics in minutes!

## 1. Install

```bash
cd translation-library
pip install -r requirements.txt
```

## 2. Get API Keys

- **Eleven Labs**: Sign up at [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys
- **DeepL**: Get free key at [deepl.com/pro-api](https://www.deepl.com/pro-api)

## 3. Set Environment Variables

```bash
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export DEEPL_API_KEY="your-deepl-api-key"
```

## 4. Run Your First Script

Create a file `test_tts.py`:

```python
from translation_library import LyricsTTS

# Initialize
lyrics_tts = LyricsTTS()

# Translate to Spanish and generate audio
result = lyrics_tts.translate_and_speak(
    lyrics="Hello, how are you today?",
    target_lang="ES",
    output_path="spanish.mp3",
    auto_play=True
)

print(f"Translation: {result['translated_text']}")
print(f"Audio saved to: {result['audio_path']}")
```

Run it:
```bash
python test_tts.py
```

## Common Use Cases

### Translate and Speak One Language

```python
result = lyrics_tts.translate_and_speak(
    lyrics="I love music",
    target_lang="FR",  # French
    output_path="french.mp3"
)
```

### Multiple Languages at Once

```python
results = lyrics_tts.batch_translate_and_speak(
    lyrics="Good morning!",
    target_languages=['ES', 'FR', 'DE', 'IT', 'JA'],
    output_dir="multilingual"
)
```

### Just TTS (No Translation)

```python
result = lyrics_tts.generate_audio(
    lyrics="Bonjour!",  # Already in French
    output_path="hello.mp3",
    language="fr"
)
```

### Use Specific Voice

```python
# List available voices
voices = lyrics_tts.get_multilingual_voices()
for voice in voices[:5]:
    print(voice['name'])

# Use specific voice
result = lyrics_tts.translate_and_speak(
    lyrics="Hello",
    target_lang="ES",
    output_path="spanish.mp3",
    voice_name="Matilda"
)
```

## Language Codes

Common codes:
- `ES` = Spanish
- `FR` = French
- `DE` = German
- `IT` = Italian
- `JA` = Japanese
- `ZH` = Chinese
- `KO` = Korean
- `PT` = Portuguese
- `RU` = Russian
- `AR` = Arabic

## Troubleshooting

❌ **"No API key provided"**
→ Set environment variables (see step 3)

❌ **"No audio player found"** (Linux)
→ Install: `sudo apt-get install mpg123`

❌ **Audio doesn't play**
→ Set `auto_play=False` and check the generated MP3 file manually

## Next Steps

- 📖 Read [Full TTS Guide](./ELEVENLABS_TTS_GUIDE.md)
- 🎯 Try [Examples](./examples/)
- 🎤 Explore voice customization options

## Need Help?

Check:
1. [TTS Guide](./ELEVENLABS_TTS_GUIDE.md) - Complete documentation
2. [Examples](./examples/) - Working code samples  
3. [README](./README.md) - Library overview