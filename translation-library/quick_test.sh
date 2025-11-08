#!/bin/bash

echo "🧪 Testing Translation Library"
echo "=============================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-mock
fi

echo "1️⃣  Running Unit Tests (no API key needed)..."
pytest test_translator.py -v --tb=short

echo ""
echo "2️⃣  Testing Language Support..."
python -c "
from translation_library import DeepLTranslator
try:
    t = DeepLTranslator(api_key='test', use_cache=False)
    langs = t.get_supported_languages()
    print(f'✓ Supports {len(langs)} languages')
except Exception as e:
    print(f'✗ Error: {e}')
"

echo ""
echo "3️⃣  Testing Error Handling..."
python -c "
from translation_library import DeepLTranslator, InvalidLanguageError
try:
    t = DeepLTranslator(api_key='test', use_cache=False)
    t.translate_lyrics('test', target_lang='INVALID')
except InvalidLanguageError:
    print('✓ Invalid language handling works')
"

if [ -n "$DEEPL_API_KEY" ]; then
    echo ""
    echo "4️⃣  Testing Real Translation (API key found)..."
    python -c "
from translation_library import DeepLTranslator
t = DeepLTranslator(use_cache=False)
result = t.translate_lyrics('Hello world', target_lang='ES')
print(f\"✓ Translation: '{result['original_text']}' → '{result['translated_text']}'\" )
"
else
    echo ""
    echo "⚠️  Skipping real API test (DEEPL_API_KEY not set)"
fi

echo ""
echo "=============================="
echo "✅ Testing Complete!"