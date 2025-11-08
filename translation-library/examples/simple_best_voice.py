"""
Simple Example: Using Best Voice Per Language Dictionary

This demonstrates the simplest approach - a pre-defined dictionary
that automatically selects the best voice for each language.
"""
import os
from translation_library import LyricsTTS
from translation_library.elevenlabs_tts import BEST_VOICES_PER_LANGUAGE


def example_1_view_best_voices():
    """Example 1: View the best voice mapping"""
    print("\n" + "="*70)
    print("Best Voice Per Language Dictionary")
    print("="*70 + "\n")
    
    print("Language -> Voice mappings:")
    for lang, voice in BEST_VOICES_PER_LANGUAGE.items():
        voice_str = voice if voice else "Auto-select multilingual"
        print(f"  {lang:8} -> {voice_str}")


def example_2_automatic_voice_selection():
    """Example 2: Automatic voice selection based on language"""
    print("\n" + "="*70)
    print("Automatic Voice Selection")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    lyrics = "Hello, how are you today?"
    
    # Translate to Spanish - automatically uses Matilda
    print("Translating to Spanish (will auto-use Matilda)...")
    result = lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang="ES",
        output_path="output/spanish_auto.mp3"
    )
    
    print(f"  Translation: {result['translated_text']}")
    print(f"  Voice used: {result['voice_name']}")
    print(f"  Audio: {result['audio_path']}")
    
    # Translate to French - automatically uses Charlotte
    print("\nTranslating to French (will auto-use Charlotte)...")
    result = lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang="FR",
        output_path="output/french_auto.mp3"
    )
    
    print(f"  Translation: {result['translated_text']}")
    print(f"  Voice used: {result['voice_name']}")
    print(f"  Audio: {result['audio_path']}")


def example_3_get_best_voice():
    """Example 3: Check what voice will be used for a language"""
    print("\n" + "="*70)
    print("Check Best Voice for Language")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    languages = ['ES', 'FR', 'DE', 'IT', 'JA']
    
    print("Checking best voices:")
    for lang in languages:
        voice = lyrics_tts.tts.get_best_voice_for_language(lang)
        voice_str = voice if voice else "Auto-select (multilingual)"
        print(f"  {lang}: {voice_str}")


def example_4_override_if_needed():
    """Example 4: Override the default voice if needed"""
    print("\n" + "="*70)
    print("Override Default Voice")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    lyrics = "Good morning!"
    
    # Use default voice for Spanish
    print("1. Using default voice for Spanish...")
    result1 = lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang="ES",
        output_path="output/spanish_default.mp3"
    )
    print(f"   Voice: {result1['voice_name']}")
    
    # Override with a different voice
    print("\n2. Overriding with different voice...")
    result2 = lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang="ES",
        output_path="output/spanish_custom.mp3",
        voice_name="Rachel"  # Explicitly specify a different voice
    )
    print(f"   Voice: {result2['voice_name']}")


def example_5_batch_with_auto_voices():
    """Example 5: Batch translate with automatic voice selection"""
    print("\n" + "="*70)
    print("Batch Translation with Auto Voice Selection")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    lyrics = "I love music and dancing"
    languages = ['ES', 'FR', 'DE', 'IT']
    
    print(f"Translating to {len(languages)} languages...")
    print("Each will automatically use the best voice:\n")
    
    for lang in languages:
        best_voice = lyrics_tts.tts.get_best_voice_for_language(lang)
        print(f"  {lang}: will use {best_voice}")
    
    print("\nProcessing...")
    results = lyrics_tts.batch_translate_and_speak(
        lyrics=lyrics,
        target_languages=languages,
        output_dir="output/batch_auto"
    )
    
    print("\nResults:")
    for result in results:
        if 'error' not in result:
            print(f"  {result['target_lang']}: {result['voice_name']}")
            print(f"    Audio: {result['audio_path']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SIMPLE BEST VOICE PER LANGUAGE")
    print("="*70)
    print("\nThis demonstrates using the predefined BEST_VOICES_PER_LANGUAGE")
    print("dictionary for automatic voice selection.\n")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/batch_auto", exist_ok=True)
    
    # Check for API keys
    if not os.getenv('ELEVENLABS_API_KEY') or not os.getenv('DEEPL_API_KEY'):
        print("\n⚠️  Please set both API keys:")
        print("  export ELEVENLABS_API_KEY='your-key'")
        print("  export DEEPL_API_KEY='your-key'")
        print("\nShowing dictionary only...")
        example_1_view_best_voices()
        return
    
    try:
        # Run examples
        example_1_view_best_voices()
        
        input("\nPress Enter to continue...")
        example_2_automatic_voice_selection()
        
        input("\nPress Enter to continue...")
        example_3_get_best_voice()
        
        input("\nPress Enter to continue...")
        example_4_override_if_needed()
        
        input("\nPress Enter to continue...")
        example_5_batch_with_auto_voices()
        
        print("\n" + "="*70)
        print("All examples completed!")
        print("="*70)
        print("\nKey Points:")
        print("  • BEST_VOICES_PER_LANGUAGE dictionary defines best voice per language")
        print("  • translate_and_speak() automatically uses the best voice")
        print("  • You can still override with voice_name parameter")
        print("  • Use get_best_voice_for_language() to check which voice will be used")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()