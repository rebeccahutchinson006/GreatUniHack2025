"""
Example: Using Eleven Labs TTS to read out lyrics in multiple languages.

This example demonstrates:
1. Basic text-to-speech generation
2. Translating and generating audio
3. Batch processing for multiple languages
4. Playing generated audio
"""
import os
from translation_library import LyricsTTS

def example_1_basic_tts():
    """Example 1: Basic text-to-speech without translation"""
    print("\n=== Example 1: Basic TTS ===")
    
    # Initialize (API keys from environment variables)
    lyrics_tts = LyricsTTS()
    
    # Generate audio from English lyrics
    lyrics = """
    Walking on sunshine
    And don't it feel good
    Hey, alright now
    """
    
    # Let the system auto-select a multilingual voice
    result = lyrics_tts.generate_audio(
        lyrics=lyrics,
        output_path="output/english.mp3",
        language="en",
        speed = 0.8,
        # voice_name parameter omitted - will auto-select a suitable voice
    )
    result2 = lyrics_tts.generate_audio(
        lyrics=lyrics,
        output_path="output/english2.mp3",
        language="en",
        speed = 1.1,
        # voice_name parameter omitted - will auto-select a suitable voice
    )
    
    print(f"Audio generated: {result['audio_path']}")
    print(f"Voice used: {result.get('voice_name', 'Auto-selected')}")


def example_2_translate_and_speak():
    """Example 2: Translate lyrics and generate audio"""
    print("\n=== Example 2: Translate & Speak ===")
    
    lyrics_tts = LyricsTTS()
    
    english_lyrics = """
    I love music
    It makes me feel alive
    Every melody tells a story
    """
    
    # Translate to Spanish and generate audio
    result = lyrics_tts.translate_and_speak(
        lyrics=english_lyrics,
        target_lang="ES",
        output_path="output/spanish.mp3",
        auto_play=False  # Set to True to play automatically
    )
    
    print(f"Original: {result['original_text'][:50]}...")
    print(f"Translated: {result['translated_text'][:50]}...")
    print(f"Audio: {result['audio_path']}")


def example_3_multiple_languages():
    """Example 3: Generate audio in multiple languages"""
    print("\n=== Example 3: Multiple Languages ===")
    
    lyrics_tts = LyricsTTS()
    
    lyrics = """
    Hello, how are you?
    The world is beautiful today
    """
    
    # Generate audio in multiple languages
    languages = ['ES', 'FR', 'DE', 'IT', 'JA','AR','EL']
    
    results = lyrics_tts.batch_translate_and_speak(
        lyrics=lyrics,
        target_languages=languages,
        output_dir="output/multilingual",
        base_filename="hello"
    )
    
    print(f"\nGenerated {len(results)} audio files:")
    for result in results:
        if 'error' not in result:
            print(f"  {result['target_lang']}: {result['audio_path']}")
            print(f"    Translation: {result['translated_text'][:50]}...")


def example_4_custom_voices():
    """Example 4: Using specific voices for different languages"""
    print("\n=== Example 4: Custom Voices ===")
    
    lyrics_tts = LyricsTTS()
    
    # First, list available multilingual voices
    print("\nAvailable multilingual voices:")
    voices = lyrics_tts.get_multilingual_voices()
    for i, voice in enumerate(voices[:5], 1):  # Show first 5
        print(f"  {i}. {voice['name']} (ID: {voice['voice_id']})")
    
    lyrics = "Good morning, sunshine!"
    
    # Use specific voice
    if voices:
        result = lyrics_tts.translate_and_speak(
            lyrics=lyrics,
            target_lang="AR",
            output_path="output/arabic_custom_voice.mp3",
            voice_name=voices[0]['name']
        )
        print(f"\nGenerated with voice '{result['voice_name']}'")
        print(f"Translation: {result['translated_text']}")


def example_5_play_audio():
    """Example 5: Generate and play audio"""
    print("\n=== Example 5: Play Audio ===")
    
    lyrics_tts = LyricsTTS()
    
    lyrics = "This is a test of the text to speech system"
    
    # Generate audio
    result = lyrics_tts.translate_and_speak(
        lyrics=lyrics,
        target_lang="FR",
        output_path="output/test_playback.mp3",
        auto_play=False
    )
    
    print(f"Audio generated: {result['audio_path']}")
    print("Playing audio... (set blocking=False for background playback)")
    
    # Play the audio
    try:
        lyrics_tts.play_audio(result['audio_path'], blocking=True)
        print("Playback complete!")
    except Exception as e:
        print(f"Playback error (may need audio player installed): {e}")


def example_6_long_lyrics():
    """Example 6: Handle long lyrics with segmentation"""
    print("\n=== Example 6: Long Lyrics ===")
    
    lyrics_tts = LyricsTTS()
    
    # long_lyrics = """
    # In the beginning, there was music
    # It echoed through the empty halls
    # Each note a promise, each chord a story
    # Weaving through time like golden thread
    
    # Through every season, through every change
    # The melody remained the same
    # A constant companion in life's journey
    # Guiding us home when we lose our way
    
    # And when the silence finally comes
    # The music still plays in our hearts
    # A timeless echo of love and life
    # Forever dancing in the stars
    # """
    long_lyrics = """
    Ground Control to Major Tom
    Ground Control to Major Tom
    Take your protein pills and put your helmet on
    Ground Control to Major Tom (ten, nine, eight, seven, six)
    Commencing countdown, engines on (five, four, three, two)
    Check ignition and may God's love be with you (one, lift off)
    This is Ground Control to Major Tom
    You've really made the grade
    And the papers want to know whose shirts you wear
    Now it's time to leave the capsule if you dare
    This is Major Tom to Ground Control
    I'm stepping through the door
    And I'm floating in a most peculiar way
    And the stars look very different today
    For here
    Am I sitting in a tin can
    Far above the world
    Planet Earth is blue
    And there's nothing I can do
    Though I'm past one hundred thousand miles
    I'm feeling very still
    And I think my spaceship knows which way to go
    Tell my wife I love her very much she knows
    Ground Control to Major Tom
    Your circuit's dead, there's something wrong
    Can you hear me, Major Tom?
    Can you hear me, Major Tom?
    Can you hear me, Major Tom? Can you-"""
    
    result = lyrics_tts.translate_and_speak(
        lyrics=long_lyrics,
        target_lang="ES",
        output_path="output/long_french.mp3",
        speed=1.1,
    )
    
    print(f"Long lyrics translated and converted to audio")
    print(f"Output: {result['audio_path']}")


def example_7_check_usage():
    """Example 7: Check API usage stats"""
    print("\n=== Example 7: API Usage Stats ===")
    
    lyrics_tts = LyricsTTS()
    
    try:
        stats = lyrics_tts.get_usage_stats()
        
        print("\nDeepL Translation Stats:")
        if 'deepl' in stats:
            deepl = stats['deepl']
            print(f"  Characters used: {deepl.get('character_count', 'N/A')}")
            print(f"  Character limit: {deepl.get('character_limit', 'N/A')}")
        
        print("\nEleven Labs TTS Stats:")
        if 'elevenlabs' in stats:
            el = stats['elevenlabs']
            if 'subscription' in el:
                sub = el['subscription']
                print(f"  Tier: {sub.get('tier', 'N/A')}")
                print(f"  Character count: {sub.get('character_count', 'N/A')}")
                print(f"  Character limit: {sub.get('character_limit', 'N/A')}")
    except Exception as e:
        print(f"Could not fetch stats: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Eleven Labs TTS + Translation Examples")
    print("=" * 60)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/multilingual", exist_ok=True)
    
    # Check for API keys
    if not os.getenv('DEEPL_API_KEY'):
        print("\n⚠️  Warning: DEEPL_API_KEY not set")
        print("Set it with: export DEEPL_API_KEY='your-key'")
    
    if not os.getenv('ELEVENLABS_API_KEY'):
        print("\n⚠️  Warning: ELEVENLABS_API_KEY not set")
        print("Set it with: export ELEVENLABS_API_KEY='your-key'")
        return
    
    try:
        # Run examples
        #example_1_basic_tts()
        #example_2_translate_and_speak()
        #example_3_multiple_languages()
        #example_4_custom_voices()
        example_5_play_audio()
        #example_6_long_lyrics()
        #example_7_check_usage()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("Check the 'output/' directory for generated audio files")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set DEEPL_API_KEY environment variable")
        print("2. Set ELEVENLABS_API_KEY environment variable")
        print("3. Installed all requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()