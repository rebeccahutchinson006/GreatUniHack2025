# DeepL Lyrics Translator

A Python library for translating song lyrics using the DeepL API, with built-in caching, formatting utilities, and music-specific optimizations.

## Features

- 🎵 **Lyric-optimized translation** with formatting preservation
- 🚀 **Built-in caching** using Redis for improved performance
- 🌍 **30+ language support** via DeepL API
- 📝 **Smart text segmentation** for long lyrics
- 🛡️ **Comprehensive error handling** with custom exceptions
- ⚡ **Optional caching** - works with or without Redis

## Installation

### From source
```bash
cd translation-library
pip install -e .
```

### Install with development dependencies
```bash
pip install -e ".[dev]"
```

## Prerequisites

1. **DeepL API Key**: Get your free API key from [DeepL](https://www.deepl.com/pro-api)
2. **Redis (optional)**: For caching functionality
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Install Redis (macOS)
   brew install redis
   ```

## Setup

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your DeepL API key:
   ```bash
   DEEPL_API_KEY=your_actual_deepl_api_key_here
   ```

3. (Optional) Load the environment variables:
   ```bash
   # Load for current session
   source .env
   
   # Or export manually
   export DEEPL_API_KEY="your-deepl-api-key"
   ```

**Note**: The `.env` file is already in [`.gitignore`](.gitignore) to prevent accidentally committing your API keys.

## Quick Start

### Basic Usage

```python
from translation_library import DeepLTranslator

# Initialize with API key
translator = DeepLTranslator(api_key="your-deepl-api-key")

# Or use environment variable
# export DEEPL_API_KEY="your-deepl-api-key"
translator = DeepLTranslator()

# Translate lyrics
lyrics = """
I'm walking on sunshine
And don't it feel good
"""

result = translator.translate_lyrics(
    text=lyrics,
    target_lang='ES',  # Spanish
    preserve_formatting=True
)

print(result['translated_text'])
# Output: Camino sobre el sol
#         Y no se siente bien
```

### Without Caching (No Redis Required)

```python
# Disable caching if Redis is not available
translator = DeepLTranslator(
    api_key="your-deepl-api-key",
    use_cache=False
)
```

### Advanced Usage

```python
from translation_library import DeepLTranslator, LyricFormatter

translator = DeepLTranslator(api_key="your-deepl-api-key")

# Translate with source language specification
result = translator.translate_lyrics(
    text="Bonjour, comment allez-vous?",
    source_lang='FR',
    target_lang='EN',
    formality='prefer_more'  # More formal translation
)

# Process long lyrics with formatter
long_lyrics = "..." # Your long lyrics text
formatter = LyricFormatter()

# Preprocess and segment
clean_lyrics = formatter.preprocess_lyrics(long_lyrics)
segments = formatter.split_into_segments(clean_lyrics, max_segment_length=500)

# Translate each segment
translations = translator.translate_batch_lyrics(segments, target_lang='JA')

# Reassemble
final_translation = formatter.reassemble_segments(translations)
```

### Check Supported Languages

```python
translator = DeepLTranslator(api_key="your-deepl-api-key")

languages = translator.get_supported_languages()
for lang in languages:
    print(f"{lang['code']}: {lang['name']}")
```

### Monitor API Usage

```python
translator = DeepLTranslator(api_key="your-deepl-api-key")

stats = translator.get_usage_stats()
print(f"Character count: {stats['character_count']}")
print(f"Character limit: {stats['character_limit']}")
```

## API Reference

### DeepLTranslator

#### `__init__(api_key: Optional[str] = None, use_cache: bool = True)`
Initialize the translator.

- `api_key`: DeepL API key (or set `DEEPL_API_KEY` environment variable)
- `use_cache`: Enable/disable Redis caching (default: True)

#### `translate_lyrics(text, target_lang='EN', source_lang=None, preserve_formatting=True, formality='prefer_less')`
Translate lyrics text.

**Parameters:**
- `text` (str): The lyrics to translate
- `target_lang` (str): Target language code (e.g., 'EN', 'ES', 'FR')
- `source_lang` (Optional[str]): Source language (auto-detected if not provided)
- `preserve_formatting` (bool): Keep line breaks and formatting
- `formality` (str): Translation formality ('default', 'prefer_more', 'prefer_less')

**Returns:** Dictionary with translation results

#### `translate_batch_lyrics(texts, target_lang='EN')`
Translate multiple lyric segments.

#### `get_supported_languages()`
Get list of supported languages.

#### `get_usage_stats()`
Get DeepL API usage statistics.

### LyricFormatter

#### `split_into_segments(text, max_segment_length=1000)`
Split long lyrics into manageable segments.

#### `reassemble_segments(translations)`
Combine translated segments back into full lyrics.

#### `preprocess_lyrics(text)`
Clean and prepare lyrics for translation.

### Custom Exceptions

```python
from translation_library import TranslationError, RateLimitError, InvalidLanguageError

try:
    result = translator.translate_lyrics("Hello", target_lang="INVALID")
except InvalidLanguageError as e:
    print(f"Invalid language: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except TranslationError as e:
    print(f"Translation failed: {e}")
```

## Supported Languages

The library supports all DeepL languages including:
- Arabic (AR), Bulgarian (BG), Czech (CS), Danish (DA)
- German (DE), Greek (EL), English (EN/EN-GB/EN-US)
- Spanish (ES), Estonian (ET), Finnish (FI), French (FR)
- Hungarian (HU), Indonesian (ID), Italian (IT), Japanese (JA)
- Korean (KO), Lithuanian (LT), Latvian (LV), Norwegian (NB)
- Dutch (NL), Polish (PL), Portuguese (PT/PT-BR/PT-PT)
- Romanian (RO), Russian (RU), Slovak (SK), Slovenian (SL)
- Swedish (SV), Turkish (TR), Ukrainian (UK), Chinese (ZH)

## Configuration

### Environment Variables

```bash
# Required
export DEEPL_API_KEY="your-deepl-api-key"

# Optional (for caching)
export REDIS_URL="redis://localhost:6379"
```

## Example Use Cases

### Translate a Song Database
```python
songs = [
    {"title": "Song 1", "lyrics": "..."},
    {"title": "Song 2", "lyrics": "..."},
]

translator = DeepLTranslator()

for song in songs:
    translation = translator.translate_lyrics(
        song['lyrics'],
        target_lang='ES'
    )
    song['lyrics_es'] = translation['translated_text']
```

### Build a Multilingual Lyrics Website
```python
# Translate to multiple languages
languages = ['ES', 'FR', 'DE', 'IT', 'JA']
translations = {}

for lang in languages:
    result = translator.translate_lyrics(original_lyrics, target_lang=lang)
    translations[lang] = result['translated_text']
```

## Error Handling

The library provides specific exceptions for different failure scenarios:

- `TranslationError`: Base exception for all translation errors
- `RateLimitError`: API rate limit exceeded
- `InvalidLanguageError`: Unsupported language code

## Performance Tips

1. **Enable caching**: Use Redis for repeated translations
2. **Batch translations**: Use `translate_batch_lyrics()` for multiple segments
3. **Segment long texts**: Use `LyricFormatter` for texts over 1000 characters
4. **Reuse translator instance**: Create one instance and reuse it

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Check the [DeepL API documentation](https://www.deepl.com/docs-api)
- Open an issue on GitHub

## Changelog

### Version 0.1.0
- Initial release
- Basic translation functionality
- Redis caching support
- Lyric formatting utilities
- Comprehensive error handling