"""
Quick Start: Translate and speak lyrics in different languages

This is the simplest way to get started with the library.
"""
from translation_library import LyricsTTS

# Initialize with API keys (from environment variables)
lyrics_tts = LyricsTTS()

# Original English lyrics
lyrics = """
Hello, my friend
How are you today?
Let's make some music
"""

# Translate to Spanish and generate audio
result = lyrics_tts.translate_and_speak(
    lyrics=lyrics,
    target_lang="ES",
    output_path="spanish_hello.mp3",
    auto_play=True  # Automatically play after generation
)

print(f"Original: {result['original_text']}")
print(f"Spanish: {result['translated_text']}")
print(f"Audio saved to: {result['audio_path']}")

# Want more languages? Try this:
languages = ['FR', 'DE', 'IT', 'JA']  # French, German, Italian, Japanese
results = lyrics_tts.batch_translate_and_speak(
    lyrics=lyrics,
    target_languages=languages,
    output_dir="multilingual_output"
)

print(f"\nGenerated audio in {len(results)} languages!")
for r in results:
    if 'error' not in r:
        print(f"  {r['target_lang']}: {r['audio_path']}")