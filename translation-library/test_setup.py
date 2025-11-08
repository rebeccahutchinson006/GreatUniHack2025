"""
Simple test to verify Eleven Labs TTS setup is working correctly.
Run this first to ensure everything is configured properly.
"""
import os
import sys

def test_api_keys():
    """Check if API keys are set"""
    print("Checking API keys...")
    
    deepl_key = os.getenv('DEEPL_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not deepl_key:
        print("❌ DEEPL_API_KEY not set")
        print("   Set it with: export DEEPL_API_KEY='your-key'")
        return False
    else:
        print(f"✅ DEEPL_API_KEY is set (starts with {deepl_key[:10]}...)")
    
    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY not set")
        print("   Set it with: export ELEVENLABS_API_KEY='your-key'")
        return False
    else:
        print(f"✅ ELEVENLABS_API_KEY is set (starts with {elevenlabs_key[:10]}...)")
    
    return True

def test_import():
    """Test if library can be imported"""
    print("\nTesting library import...")
    try:
        from translation_library import LyricsTTS
        print("✅ Library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import library: {e}")
        print("   Make sure you're in the translation-library directory")
        print("   Or install with: pip install -e .")
        return False

def test_voices():
    """Test fetching available voices"""
    print("\nFetching available voices...")
    try:
        from translation_library import LyricsTTS
        lyrics_tts = LyricsTTS()
        
        voices = lyrics_tts.get_available_voices()
        print(f"✅ Found {len(voices)} voices")
        
        multilingual = lyrics_tts.get_multilingual_voices()
        print(f"✅ Found {len(multilingual)} multilingual voices")
        
        if multilingual:
            print("\nFirst 3 multilingual voices:")
            for i, voice in enumerate(multilingual[:3], 1):
                print(f"  {i}. {voice['name']} (ID: {voice['voice_id']})")
        
        return True
    except Exception as e:
        print(f"❌ Failed to fetch voices: {e}")
        return False

def test_simple_tts():
    """Test generating a simple audio file"""
    print("\nTesting audio generation...")
    try:
        from translation_library import LyricsTTS
        
        lyrics_tts = LyricsTTS()
        
        # Create test output directory
        os.makedirs("test_output", exist_ok=True)
        
        # Generate simple test audio
        result = lyrics_tts.translate_and_speak(
            lyrics="Hello, this is a test",
            target_lang="ES",
            output_path="test_output/test.mp3",
            auto_play=False
        )
        
        print(f"✅ Audio generated successfully")
        print(f"   Original: {result['original_text']}")
        print(f"   Translated: {result['translated_text']}")
        print(f"   Audio file: {result['audio_path']}")
        print(f"   Voice used: {result.get('voice_name', 'Auto-selected')}")
        
        return True
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Eleven Labs TTS Setup Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: API Keys
    results.append(("API Keys", test_api_keys()))
    
    if not results[0][1]:
        print("\n⚠️  Please set API keys before continuing")
        sys.exit(1)
    
    # Test 2: Import
    results.append(("Library Import", test_import()))
    
    if not results[1][1]:
        print("\n⚠️  Please fix import issues before continuing")
        sys.exit(1)
    
    # Test 3: Voices
    results.append(("Voice Fetching", test_voices()))
    
    # Test 4: Simple TTS
    results.append(("Audio Generation", test_simple_tts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    if all(result[1] for result in results):
        print("\n🎉 All tests passed! You're ready to use the library.")
        print("\nTry running:")
        print("  python examples/quickstart_tts.py")
        print("  python elevenlabs_tts_example.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()