"""
Example: Using Best Voice for Each Language (Filter-Based Approach)

This demonstrates the "best voice for each language" pattern from VOICE_SELECTION_GUIDE.md
using the new filtering capabilities:

1. Filter voices by characteristics (gender, accent, age, use case)
2. Get recommended voices for specific languages
3. Build custom language-to-voice mappings based on preferences
4. Translate to multiple languages with optimized voice selection
"""
import os
from translation_library import LyricsTTS


def example_1_filter_by_characteristics():
    """Example 1: Filter voices by specific characteristics"""
    print("\n" + "="*70)
    print("Example 1: Filter Voices by Characteristics")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    # Find female British voices
    print("Finding female British voices...")
    female_british = lyrics_tts.filter_voices_by_characteristics(
        gender='female',
        accent='british'
    )
    
    print(f"Found {len(female_british)} female British voices:")
    for voice in female_british[:5]:  # Show top 5
        print(f"  - {voice['name']}")
        print(f"    Labels: {voice.get('labels', {})}")
    
    # Find male American voices suitable for narration
    print("\nFinding male American voices for narration...")
    male_american_narration = lyrics_tts.filter_voices_by_characteristics(
        gender='male',
        accent='american',
        use_case='narration'
    )
    
    print(f"Found {len(male_american_narration)} matching voices:")
    for voice in male_american_narration[:3]:
        print(f"  - {voice['name']}")
        print(f"    Labels: {voice.get('labels', {})}")


def example_2_recommended_voices_for_language():
    """Example 2: Get recommended voices for specific languages"""
    print("\n" + "="*70)
    print("Example 2: Get Recommended Voices for Languages")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    languages = ['ES', 'FR', 'DE', 'IT', 'JA']
    
    for lang in languages:
        print(f"\n{lang} (Language):")
        
        # Get recommendations without preferences
        result = lyrics_tts.get_recommended_voices(lang)
        
        if result['recommended']:
            print(f"  Recommended: {result['recommended']['name']}")
            print(f"    Voice ID: {result['recommended']['voice_id']}")
            print(f"    Labels: {result['recommended'].get('labels', {})}")
        else:
            print(f"  Recommended: Auto-select")
        
        print(f"  Alternatives ({len(result['alternatives'])}):")
        for alt in result['alternatives'][:3]:
            print(f"    - {alt['name']}")


def example_3_recommended_with_preferences():
    """Example 3: Get recommended voices with gender preferences"""
    print("\n" + "="*70)
    print("Example 3: Recommended Voices with Preferences")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    # Get female voice for Spanish
    print("Spanish with female preference:")
    result = lyrics_tts.get_recommended_voices(
        'ES',
        preferences={'gender': 'female'}
    )
    
    if result['recommended']:
        print(f"  Recommended: {result['recommended']['name']}")
        print(f"    Gender: {result['recommended'].get('labels', {}).get('gender')}")
    
    print(f"  Other female alternatives:")
    for alt in result['alternatives'][:3]:
        print(f"    - {alt['name']}")
    
    # Get male voice for French
    print("\nFrench with male preference:")
    result = lyrics_tts.get_recommended_voices(
        'FR',
        preferences={'gender': 'male'}
    )
    
    if result['recommended']:
        print(f"  Recommended: {result['recommended']['name']}")
        print(f"    Gender: {result['recommended'].get('labels', {}).get('gender')}")


def example_4_build_voice_preferences():
    """Example 4: Build a custom voice preference mapping"""
    print("\n" + "="*70)
    print("Example 4: Build Custom Voice Preference Mapping")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    # Define preferences for each language
    language_preferences = {
        'ES': {'gender': 'female'},  # Spanish: female voice
        'FR': {'gender': 'male'},    # French: male voice
        'DE': {'gender': 'female'},  # German: female voice
        'IT': {'gender': 'male'},    # Italian: male voice
        'JA': {},                    # Japanese: any multilingual
    }
    
    # Build the voice mapping
    voice_mapping = {}
    
    for lang, prefs in language_preferences.items():
        result = lyrics_tts.get_recommended_voices(lang, preferences=prefs)
        
        if result['recommended']:
            voice_mapping[lang] = result['recommended']['name']
            print(f"{lang}: {result['recommended']['name']}")
            print(f"  Preferences: {prefs}")
            print(f"  Labels: {result['recommended'].get('labels', {})}")
        else:
            voice_mapping[lang] = None
            print(f"{lang}: Auto-select")
        print()
    
    return voice_mapping


def example_5_translate_with_best_voices():
    """Example 5: Translate to multiple languages with optimized voices"""
    print("\n" + "="*70)
    print("Example 5: Translate with Best Voices per Language")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    # Build voice mapping using preferences
    print("Building voice preferences...")
    preferences_map = {
        'ES': {'gender': 'female'},
        'FR': {'gender': 'female'},
        'DE': {'gender': 'female'},
        'IT': {'gender': 'female'},
    }
    
    voice_settings = {}
    for lang, prefs in preferences_map.items():
        result = lyrics_tts.get_recommended_voices(lang, preferences=prefs)
        if result['recommended']:
            voice_settings[lang] = result['recommended']['name']
            print(f"{lang}: Using {result['recommended']['name']}")
    
    print("\nTranslating lyrics...")
    lyrics = """
    In the morning light
    I see your face
    Every moment with you
    Is pure grace
    """
    
    # Translate with optimized voices
    results = lyrics_tts.batch_translate_and_speak(
        lyrics=lyrics,
        target_languages=list(voice_settings.keys()),
        output_dir="output/best_voices",
        voice_settings=voice_settings
    )
    
    print("\nResults:")
    for result in results:
        if 'error' not in result:
            print(f"\n{result['target_lang']}:")
            print(f"  Voice: {result['voice_name']}")
            print(f"  Audio: {result['audio_path']}")
            print(f"  Translation: {result['translated_text'][:60]}...")
        else:
            print(f"\n{result['target_lang']}: Error - {result['error']}")


def example_6_filter_by_use_case():
    """Example 6: Select voices by use case (narration, conversational, etc.)"""
    print("\n" + "="*70)
    print("Example 6: Filter Voices by Use Case")
    print("="*70 + "\n")
    
    lyrics_tts = LyricsTTS()
    
    use_cases = ['narration', 'conversational', 'news']
    
    for use_case in use_cases:
        print(f"\nVoices for '{use_case}':")
        voices = lyrics_tts.filter_voices_by_characteristics(
            use_case=use_case
        )
        
        print(f"  Found {len(voices)} voices:")
        for voice in voices[:3]:
            print(f"    - {voice['name']}")
            print(f"      Gender: {voice.get('labels', {}).get('gender', 'unknown')}")
            print(f"      Accent: {voice.get('labels', {}).get('accent', 'unknown')}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("BEST VOICE PER LANGUAGE - FILTER-BASED APPROACH")
    print("="*70)
    
    # Create output directory
    os.makedirs("output/best_voices", exist_ok=True)
    
    # Check for API keys
    if not os.getenv('ELEVENLABS_API_KEY') or not os.getenv('DEEPL_API_KEY'):
        print("\n⚠️  Please set both API keys:")
        print("  export ELEVENLABS_API_KEY='your-key'")
        print("  export DEEPL_API_KEY='your-key'")
        return
    
    try:
        # Run examples
        example_1_filter_by_characteristics()
        
        input("\nPress Enter to continue...")
        example_2_recommended_voices_for_language()
        
        input("\nPress Enter to continue...")
        example_3_recommended_with_preferences()
        
        input("\nPress Enter to continue...")
        voice_mapping = example_4_build_voice_preferences()
        
        input("\nPress Enter to continue...")
        example_5_translate_with_best_voices()
        
        input("\nPress Enter to continue...")
        example_6_filter_by_use_case()
        
        print("\n" + "="*70)
        print("All examples completed!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. Use filter_voices_by_characteristics() to find voices by traits")
        print("2. Use get_recommended_voices() for intelligent language-based selection")
        print("3. Build custom voice mappings based on your preferences")
        print("4. Apply preferences like gender, accent, age, and use case")
        print("5. Use batch_translate_and_speak() with voice_settings for efficiency")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()