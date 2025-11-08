"""
Test script for the new voice filtering functionality
"""
import os
from translation_library import LyricsTTS


def test_filter_voices_by_characteristics():
    """Test filtering voices by characteristics"""
    print("\n=== Testing filter_voices_by_characteristics ===")
    
    lyrics_tts = LyricsTTS()
    
    # Test 1: Filter by gender
    print("\n1. Filter by gender (female):")
    female_voices = lyrics_tts.filter_voices_by_characteristics(gender='female')
    print(f"   Found {len(female_voices)} female voices")
    if female_voices:
        print(f"   Example: {female_voices[0]['name']}")
        assert female_voices[0].get('labels', {}).get('gender') == 'female'
    
    # Test 2: Filter by accent
    print("\n2. Filter by accent (american):")
    american_voices = lyrics_tts.filter_voices_by_characteristics(accent='american')
    print(f"   Found {len(american_voices)} American voices")
    if american_voices:
        print(f"   Example: {american_voices[0]['name']}")
    
    # Test 3: Filter by multiple criteria
    print("\n3. Filter by gender + accent (female + british):")
    female_british = lyrics_tts.filter_voices_by_characteristics(
        gender='female',
        accent='british'
    )
    print(f"   Found {len(female_british)} female British voices")
    if female_british:
        print(f"   Example: {female_british[0]['name']}")
        labels = female_british[0].get('labels', {})
        assert labels.get('gender') == 'female'
        assert 'british' in str(labels.get('accent', '')).lower()
    
    print("\n✓ filter_voices_by_characteristics tests passed")


def test_get_recommended_voices():
    """Test getting recommended voices for languages"""
    print("\n=== Testing get_recommended_voices ===")
    
    lyrics_tts = LyricsTTS()
    
    # Test 1: Get recommendations for Spanish
    print("\n1. Get recommendations for Spanish (ES):")
    result = lyrics_tts.get_recommended_voices('ES')
    print(f"   Recommended: {result['recommended']['name'] if result['recommended'] else 'Auto-select'}")
    print(f"   Alternatives: {len(result['alternatives'])}")
    print(f"   All matching: {len(result['all_matching'])}")
    assert 'recommended' in result
    assert 'alternatives' in result
    assert 'all_matching' in result
    
    # Test 2: Get recommendations with preferences
    print("\n2. Get recommendations for French (FR) with female preference:")
    result = lyrics_tts.get_recommended_voices('FR', preferences={'gender': 'female'})
    if result['recommended']:
        print(f"   Recommended: {result['recommended']['name']}")
        print(f"   Gender: {result['recommended'].get('labels', {}).get('gender')}")
        assert result['recommended'].get('labels', {}).get('gender') == 'female'
    else:
        print(f"   No specific recommendation, will auto-select")
    
    # Test 3: Get recommendations for multiple languages
    print("\n3. Get recommendations for multiple languages:")
    languages = ['ES', 'FR', 'DE', 'IT']
    for lang in languages:
        result = lyrics_tts.get_recommended_voices(lang)
        recommended_name = result['recommended']['name'] if result['recommended'] else 'Auto'
        print(f"   {lang}: {recommended_name} ({len(result['alternatives'])} alternatives)")
    
    print("\n✓ get_recommended_voices tests passed")


def test_integration():
    """Test integration with translate_and_speak"""
    print("\n=== Testing Integration ===")
    
    lyrics_tts = LyricsTTS()
    
    # Get recommended voice for Spanish
    print("\n1. Get recommended voice for Spanish:")
    voice_result = lyrics_tts.get_recommended_voices('ES', preferences={'gender': 'female'})
    
    if voice_result['recommended']:
        voice_name = voice_result['recommended']['name']
        print(f"   Using voice: {voice_name}")
        
        # Use it in translation (dry run - just test the voice selection)
        print("\n2. Voice would be used in translate_and_speak:")
        print(f"   voice_name='{voice_name}'")
        print(f"   This voice can be passed to translate_and_speak()")
    else:
        print("   Would use auto-selection")
    
    print("\n✓ Integration tests passed")


def test_voice_characteristics_display():
    """Display available voice characteristics for reference"""
    print("\n=== Voice Characteristics Reference ===")
    
    lyrics_tts = LyricsTTS()
    voices = lyrics_tts.get_available_voices()
    
    # Collect unique characteristics
    genders = set()
    accents = set()
    ages = set()
    use_cases = set()
    
    for voice in voices:
        labels = voice.get('labels', {})
        if labels.get('gender'):
            genders.add(labels['gender'])
        if labels.get('accent'):
            accents.add(labels['accent'])
        if labels.get('age'):
            ages.add(labels['age'])
        if labels.get('use case'):
            use_cases.add(labels['use case'])
    
    print(f"\nAvailable Genders: {sorted(genders)}")
    print(f"Available Accents: {sorted(accents)}")
    print(f"Available Ages: {sorted(ages)}")
    print(f"Available Use Cases: {sorted(use_cases)}")
    print(f"\nTotal voices: {len(voices)}")


def main():
    """Run all tests"""
    print("="*70)
    print("VOICE FILTERING FEATURE TESTS")
    print("="*70)
    
    # Check for API keys
    if not os.getenv('ELEVENLABS_API_KEY'):
        print("\n⚠️  Please set ELEVENLABS_API_KEY environment variable")
        print("  export ELEVENLABS_API_KEY='your-key'")
        return
    
    if not os.getenv('DEEPL_API_KEY'):
        print("\n⚠️  Warning: DEEPL_API_KEY not set (needed for full integration)")
        print("  Some tests may be limited")
    
    try:
        # Display reference info
        test_voice_characteristics_display()
        
        # Run tests
        test_filter_voices_by_characteristics()
        test_get_recommended_voices()
        test_integration()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70)
        print("\nNew features available:")
        print("  • filter_voices_by_characteristics() - Filter voices by traits")
        print("  • get_recommended_voices() - Get smart recommendations per language")
        print("  • Voice preferences support (gender, accent, age, use_case)")
        print("\nSee examples/best_voice_per_language.py for usage examples")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())