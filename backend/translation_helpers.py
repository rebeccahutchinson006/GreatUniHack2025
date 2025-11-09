"""
Translation Helper Functions
Provides functions for translating lyrics using DeepL
"""
import asyncio
from typing import Optional, List
from translation_library import DeepLTranslator, LyricFormatter
from translation_library.exceptions import TranslationError, RateLimitError, InvalidLanguageError


def translate_lyrics_sync(
    text: str, 
    target_lang: str, 
    source_lang: Optional[str] = None,
    api_key: str = None
) -> dict:
    """
    Synchronous wrapper for translation.
    
    Args:
        text: Text to translate
        target_lang: Target language code
        source_lang: Source language code (optional, auto-detect if not provided)
        api_key: DeepL API key
    
    Returns:
        Dictionary with translation results
    """
    translator = DeepLTranslator(api_key=api_key, use_cache=False)
    return translator.translate_lyrics(
        text=text,
        target_lang=target_lang,
        source_lang=source_lang,
        preserve_formatting=True,
        formality='prefer_less'
    )


def translate_batch_sync(
    texts: List[str], 
    target_lang: str, 
    source_lang: Optional[str] = None,
    api_key: str = None
) -> List[dict]:
    """
    Synchronous wrapper for batch translation - translates multiple texts in one API call.
    
    Args:
        texts: List of texts to translate
        target_lang: Target language code
        source_lang: Source language code (optional)
        api_key: DeepL API key
    
    Returns:
        List of translation result dictionaries
    
    Raises:
        RateLimitError: If API rate limit is exceeded
        TranslationError: If translation fails
    """
    translator = DeepLTranslator(api_key=api_key, use_cache=False)
    
    # Use DeepL's batch translation by sending multiple texts in one request
    import requests
    
    params = {
        'target_lang': target_lang.upper(),
        'preserve_formatting': '1',
        'formality': 'prefer_less'
    }
    
    if source_lang:
        params['source_lang'] = source_lang.upper()
    
    # Add all texts as separate 'text' parameters
    for text in texts:
        params.setdefault('text', []).append(text)
    
    headers = {
        'Authorization': f'DeepL-Auth-Key {translator.api_key}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # DeepL API expects multiple 'text' parameters
        data = []
        for key, value in params.items():
            if key == 'text':
                for text in value:
                    data.append(('text', text))
            else:
                data.append((key, value))
        
        response = requests.post(
            translator.base_url,
            data=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 429:
            raise RateLimitError("DeepL API rate limit exceeded")
        elif response.status_code != 200:
            raise TranslationError(f"DeepL API error: {response.status_code} - {response.text}")
        
        data_response = response.json()
        translations = data_response['translations']
        
        results = []
        for i, translation in enumerate(translations):
            results.append({
                'original_text': texts[i],
                'translated_text': translation['text'],
                'detected_language': translation.get('detected_source_language'),
                'target_language': target_lang
            })
        
        return results
        
    except requests.exceptions.RequestException as e:
        raise TranslationError(f"Network error: {str(e)}")

