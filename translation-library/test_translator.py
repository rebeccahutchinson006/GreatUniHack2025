#!/usr/bin/env python3
"""
Basic unit tests for the DeepL Lyrics Translator library
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from translation_library import (
    DeepLTranslator,
    LyricFormatter,
    TranslationError,
    RateLimitError,
    InvalidLanguageError
)


class TestDeepLTranslator:
    """Test suite for DeepLTranslator class"""
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        assert translator.api_key == "test-key"
        assert translator.cache is None
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(TranslationError, match="API key is required"):
                DeepLTranslator()
    
    def test_init_with_cache(self):
        """Test initialization with cache enabled"""
        with patch('translation_library.deepl_translator.TranslationCache'):
            translator = DeepLTranslator(api_key="test-key", use_cache=True)
            assert translator.use_cache is True
    
    def test_validate_language_valid(self):
        """Test language validation with valid code"""
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        # Should not raise exception
        translator._validate_language('EN')
        translator._validate_language('ES')
        translator._validate_language('FR')
    
    def test_validate_language_invalid(self):
        """Test language validation with invalid code"""
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        with pytest.raises(InvalidLanguageError):
            translator._validate_language('INVALID')
    
    def test_supported_languages(self):
        """Test get_supported_languages returns correct structure"""
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        languages = translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert all('code' in lang and 'name' in lang for lang in languages)
        
        # Check some expected languages
        codes = [lang['code'] for lang in languages]
        assert 'EN' in codes
        assert 'ES' in codes
        assert 'FR' in codes
    
    @patch('requests.post')
    def test_translate_lyrics_success(self, mock_post):
        """Test successful translation"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'translations': [{
                'text': 'Hola',
                'detected_source_language': 'EN'
            }]
        }
        mock_post.return_value = mock_response
        
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        result = translator.translate_lyrics("Hello", target_lang='ES')
        
        assert result['original_text'] == "Hello"
        assert result['translated_text'] == 'Hola'
        assert result['detected_language'] == 'EN'
        assert result['target_language'] == 'ES'
    
    @patch('requests.post')
    def test_translate_lyrics_rate_limit(self, mock_post):
        """Test rate limit error handling"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        
        with pytest.raises(RateLimitError):
            translator.translate_lyrics("Hello", target_lang='ES')
    
    @patch('requests.post')
    def test_translate_lyrics_api_error(self, mock_post):
        """Test API error handling"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        
        with pytest.raises(TranslationError):
            translator.translate_lyrics("Hello", target_lang='ES')
    
    @patch('requests.post')
    def test_translate_batch_lyrics(self, mock_post):
        """Test batch translation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'translations': [{
                'text': 'Hola',
                'detected_source_language': 'EN'
            }]
        }
        mock_post.return_value = mock_response
        
        translator = DeepLTranslator(api_key="test-key", use_cache=False)
        results = translator.translate_batch_lyrics(
            ["Hello", "Goodbye"],
            target_lang='ES'
        )
        
        assert len(results) == 2
        assert all('translated_text' in r for r in results)


class TestLyricFormatter:
    """Test suite for LyricFormatter class"""
    
    def test_preprocess_lyrics(self):
        """Test lyric preprocessing"""
        text = "  Hello   World  \n\n\n  Test  "
        result = LyricFormatter.preprocess_lyrics(text)
        
        assert result == "Hello World\n\nTest"
    
    def test_split_into_segments_short(self):
        """Test splitting short text"""
        text = "Short text"
        segments = LyricFormatter.split_into_segments(text, max_segment_length=100)
        
        assert len(segments) == 1
        assert segments[0] == text
    
    def test_split_into_segments_long(self):
        """Test splitting long text"""
        text = "Line 1\n\nLine 2\n\nLine 3\n\nLine 4"
        segments = LyricFormatter.split_into_segments(text, max_segment_length=15)
        
        assert len(segments) > 1
    
    def test_reassemble_segments(self):
        """Test reassembling translated segments"""
        translations = [
            {'translated_text': 'Part 1'},
            {'translated_text': 'Part 2'},
            {'translated_text': 'Part 3'}
        ]
        
        result = LyricFormatter.reassemble_segments(translations)
        assert result == "Part 1\n\nPart 2\n\nPart 3"


class TestExceptions:
    """Test custom exceptions"""
    
    def test_translation_error(self):
        """Test TranslationError"""
        error = TranslationError("Test error")
        assert str(error) == "Test error"
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        error = RateLimitError("Rate limit")
        assert str(error) == "Rate limit"
        assert isinstance(error, TranslationError)
    
    def test_invalid_language_error(self):
        """Test InvalidLanguageError"""
        error = InvalidLanguageError("Invalid language")
        assert str(error) == "Invalid language"
        assert isinstance(error, TranslationError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])