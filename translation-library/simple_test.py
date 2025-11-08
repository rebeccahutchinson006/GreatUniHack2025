#!/usr/bin/env python3
"""
Simple script to test DeepL API key (no dependencies needed)
"""

import os

# Set your API key here directly or use environment variable
#API_KEY = "b885f340-7558-4656-9a64-12dfda3389ef:fx"
API_KEY = os.getenv('DEEPL_API_KEY')

# Import the translator
from translation_library import DeepLTranslator

def test_api():
    """Test if the DeepL API key is working"""
    print("=" * 60)
    print("Testing DeepL API")
    print("=" * 60)
    print()
    
    try:
        # Initialize translator (disable cache to avoid Redis requirement)
        print("Initializing translator...")
        translator = DeepLTranslator(use_cache=False)
        print("✓ Translator initialized successfully")
        print()
        
        # Test 1: Simple translation
        print("Test 1: Simple Translation (English → Latvian)")
        print("-" * 60)
        test_text = " a walking pizza?"
        print(f"Original: {test_text}")
        
        result = translator.translate_lyrics(
            text=test_text,
            target_lang='LV'
        )
        
        print(f"Translated: {result['translated_text']}")
        print(f"Detected language: {result['detected_language']}")
        print("✓ Translation successful!")
        print()
        
        # Test 2: Song lyrics translation
        print("Test 2: Lyrics Translation (English → French)")
        print("-" * 60)
        lyrics = """I'm walking on sunshine
And don't it feel good"""
        
        print(f"Original lyrics:\n{lyrics}")
        print()
        
        result = translator.translate_lyrics(
            text=lyrics,
            target_lang='FR',
            preserve_formatting=True
        )
        
        print(f"Translated lyrics:\n{result['translated_text']}")
        print("✓ Lyrics translation successful!")
        print()
        
        # Test 3: Multiple languages
        print("Test 3: Translate to Multiple Languages")
        print("-" * 60)
        text = "a walking pizza walks into a bar and says OW!"
        languages = ['ES', 'FR', 'DE', 'IT', 'JA']
        
        print(f"Original: {text}\n")
        for lang in languages:
            result = translator.translate_lyrics(text, target_lang=lang)
            lang_name = translator.SUPPORTED_LANGUAGES.get(lang, lang)
            print(f"{lang_name:20} ({lang}): {result['translated_text']}")
        print()
        
        # Success summary
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour DeepL API key is working correctly.")
        print("You can now use the translation library.")
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key - check your DeepL API key")
        print("2. Network connection - make sure you're connected to internet")
        print("3. API quota exceeded - check your DeepL account limits")
        return False

if __name__ == "__main__":
    test_api()