"""
Example: Selecting voices based on the target language

This demonstrates how to:
1. List available voices
2. Select voices by language/accent
3. Use specific voices for different languages
"""
import os
from translation_library import LyricsTTS

def list_voices_by_language():
    """Show how to find voices for specific languages"""
    print("\n=== Listing Voices by Language ===\n")
    
    lyrics_tts = LyricsTTS()
    
    # Get all available voices
    all_voices = lyrics_tts.get_available_voices()
    
    print(f"Total voices available: {len(all_voices)}\n")
    
    # Group voices by their characteristics
    for voice in all_voices:
        name = voice['name']
        voice_id = voice['voice_id']
        labels = voice.get('labels', {})
        
        # Get language/accent info from labels
        accent = labels.get('accent', 'Unknown')
        use_case = labels.get('use case', 'general')
        
        print(f"Voice: {name}")
        print(f"  ID: {voice_id}")
        print(f"  Accent: {accent}")
        print(f"  Use Case: {use_case}")
        print(f"  Labels: {labels}")
        print()

def example_1_select_voice_by_name():
    """Example 1: Use a specific voice by name"""
    print("\n=== Example 1: Select Voice by Name ===\n")
    
    lyrics_tts = LyricsTTS()
    
    # Translate to French using a specific voice
    result = lyrics_tts.translate_and_speak(
        lyrics="Hello, how are you today?",
        target_lang="FR",
        output_path="output/french_specific_voice.mp3",
        voice_name="Charlotte"  # Specify the voice by name
    )
    
    print(f"Translation: {result['translated_text']}")
    print(f"Voice used: {result['voice_name']}")
    print(f"Audio: {result['audio_path']}\n")

def example_2_language_to_voice_mapping():
    """Example 2: Map languages to specific voices"""
    print("\n=== Example 2: Language-to-Voice Mapping ===\n")
    
    lyrics_tts = LyricsTTS()
    
    # Define which voice to use for each language
    language_voice_map = {
        'ES': 'Matilda',    # Spanish
        'FR': 'Charlotte',  # French
        'DE': 'Daniel',     # German
        'IT': 'Gianna',     # Italian
        'JA': None          # Japanese - auto-select
    }
    
    lyrics = "Good morning, how are you?"
    
    for lang_code, voice_name in language_voice_map.items():
        try:
            result = lyrics_tts.translate_and_speak(
                lyrics=lyrics,
                target_lang=lang_code,
                output_path=f"output/{lang_code.lower()}_custom_voice.mp3",
                voice_name=voice_name  # None = auto-select
            )
            
            print(f"{lang_code}: {result['translated_text']}")
            print(f"  Voice: {result['voice_name']}")
            print(f"  Audio: {result['audio_path']}\n")
        except Exception as e:
            print(f"{lang_code}: Error - {e}\n")

def example_3_interactive_voice_selection():
    """Example 3: Let user choose voice interactively"""
    print("\n=== Example 3: Interactive Voice Selection ===\n")
    
    lyrics_tts = LyricsTTS()
    
    # Get available voices
    voices = lyrics_tts.get_available_voices()
    
    print("Available voices:")
    for i, voice in enumerate(voices, 1):
        accent = voice.get('labels', {}).get('accent', 'Unknown')
        print(f"{i}. {voice['name']} (Accent: {accent})")
    
    # In a real app, you'd get user input
    # For demo, we'll just use the first voice
    selected_voice = voices[0]['name']
    
    print(f"\nUsing voice: {selected_voice}\n")
    
    result = lyrics_tts.translate_and_speak(
        lyrics="This is a test",
        target_lang="ES",
        output_path="output/interactive_selection.mp3",
        voice_name=selected_voice
    )
    
    print(f"Translation: {result['translated_text']}")
    print(f"Audio: {result['audio_path']}")

def example_4_batch_with_voice_mapping():
    """Example 4: Batch processing with language-specific voices"""
    print("\n=== Example 4: Batch with Custom Voices ===\n")
    
    lyrics_tts = LyricsTTS()
    
    # First, let's see what voices are available
    voices = lyrics_tts.get_available_voices()
    print(f"Available voices: {[v['name'] for v in voices[:5]]}\n")
    
    # Define voice preferences for each language
    # Use first available voice as default
    default_voice = voices[0]['name'] if voices else None
    
    voice_settings = {
        'ES': default_voice,  # Spanish
        'FR': default_voice,  # French
        'DE': default_voice,  # German
        'IT': default_voice,  # Italian
    }
    
    lyrics = "Music brings us together"
    
    results = lyrics_tts.batch_translate_and_speak(
        lyrics=lyrics,
        target_languages=list(voice_settings.keys()),
        output_dir="output/batch_custom",
        voice_settings=voice_settings
    )
    
    print("Generated files:")
    for result in results:
        if 'error' not in result:
            print(f"{result['target_lang']}: {result['audio_path']}")
            print(f"  Voice: {result.get('voice_name', 'Auto')}")
            print(f"  Translation: {result['translated_text']}\n")

def example_5_find_voice_by_accent():
    """Example 5: Filter voices by accent/language"""
    print("\n=== Example 5: Find Voices by Accent ===\n")
    
    lyrics_tts = LyricsTTS()
    voices = lyrics_tts.get_available_voices()
    
    # Find voices with specific accent
    target_accent = "british"  # Change this to search for different accents
    
    matching_voices = [
        v for v in voices 
        if target_accent.lower() in str(v.get('labels', {}).get('accent', '')).lower()
    ]
    
    if matching_voices:
        print(f"Voices with '{target_accent}' accent:")
        for voice in matching_voices:
            print(f"  - {voice['name']}")
    else:
        print(f"No voices found with '{target_accent}' accent")
        print("\nAvailable accents:")
        accents = set()
        for v in voices:
            accent = v.get('labels', {}).get('accent')
            if accent:
                accents.add(accent)
        for accent in sorted(accents):
            print(f"  - {accent}")

def main():
    """Run all examples"""
    print("=" * 60)
    print("Language-Specific Voice Selection Examples")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/batch_custom", exist_ok=True)
    
    # Check for API keys
    if not os.getenv('ELEVENLABS_API_KEY') or not os.getenv('DEEPL_API_KEY'):
        print("\n⚠️  Please set both API keys:")
        print("  export ELEVENLABS_API_KEY='your-key'")
        print("  export DEEPL_API_KEY='your-key'")
        return
    
    try:
        # First, show available voices
        list_voices_by_language()
        
        input("\nPress Enter to continue to examples...")
        
        # Run examples
        example_1_select_voice_by_name()
        example_2_language_to_voice_mapping()
        example_3_interactive_voice_selection()
        example_4_batch_with_voice_mapping()
        example_5_find_voice_by_accent()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()