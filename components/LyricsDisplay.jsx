import React, { useEffect, useRef, useState } from 'react';
import './LyricsDisplay.css';
import { api } from '../services/api';

const Word = ({ word, selectedLanguage, onTranslation }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [translation, setTranslation] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);

  const handleClick = async (e) => {
    e.stopPropagation();
    
    if (translation) {
      onTranslation(word, translation, e);
      return;
    }

    if (isTranslating || selectedLanguage === 'EN') return;

    setIsTranslating(true);
    try {
      const result = await api.translateWord(word, selectedLanguage);
      setTranslation(result.translated_word);
      onTranslation(word, result.translated_word, e);
    } catch (error) {
      console.error('Error translating word:', error);
      onTranslation(word, word, e); // Fallback to original word
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <span
      className={`lyrics-word ${isHovered ? 'hovered' : ''} ${translation ? 'translated' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
      title={translation ? `${word} → ${translation}` : `Click to translate "${word}"`}
    >
      {word}
    </span>
  );
};

const LyricsDisplay = ({ lyrics, overlayData, isLoading, error, progressMs, durationMs, selectedLanguage = 'EN' }) => {
  const lyricsRef = useRef(null);
  const activeLineRef = useRef(null);
  const [lyricsLines, setLyricsLines] = useState([]);
  const [isSynced, setIsSynced] = useState(false);
  const [wordTranslation, setWordTranslation] = useState(null);
  const [translationPosition, setTranslationPosition] = useState({ x: 0, y: 0 });

  // Split text into words (preserving punctuation and spaces)
  const splitIntoWords = (text) => {
    if (!text) return [];
    // Split by word boundaries but keep punctuation attached
    const words = text.match(/\S+|\s+/g) || [];
    return words;
  };

  const handleWordTranslation = (word, translation, event) => {
    if (event) {
      // Position popup near the cursor, but keep it on screen
      const x = Math.min(event.clientX + 10, window.innerWidth - 250);
      const y = Math.max(event.clientY - 50, 10);
      setTranslationPosition({ x, y });
    }
    setWordTranslation({ word, translation });
  };

  // Close translation popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.lyrics-word') && !e.target.closest('.word-translation-popup')) {
        setWordTranslation(null);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Parse lyrics into lines (for normal mode)
  useEffect(() => {
    if (overlayData && overlayData.lines) {
      // Overlay mode - use overlay data
      console.log('Processing overlay data:', overlayData);
      // Check if any line has a timestamp (for synced lyrics)
      const hasTimestamps = overlayData.lines.some(line => line.timestamp_ms !== undefined && line.timestamp_ms !== null);
      setIsSynced(hasTimestamps);
      setLyricsLines(overlayData.lines.map(line => ({
        text: line.original || '',
        translated: line.translated || '',
        timestamp: line.timestamp_ms || null
      })));
      return;
    }

    if (!lyrics) {
      setLyricsLines([]);
      setIsSynced(false);
      return;
    }

    // Check if lyrics is synced (object with lines) or plain text
    if (typeof lyrics === 'object' && lyrics.synced && lyrics.lines) {
      // Synced lyrics from LRC
      setIsSynced(true);
      setLyricsLines(lyrics.lines.map(line => ({
        text: line.text,
        timestamp: line.timestamp_ms
      })));
    } else {
      // Plain text lyrics
      setIsSynced(false);
      const text = typeof lyrics === 'string' ? lyrics : lyrics.lyrics || '';
      const lines = text.split('\n').filter(line => line.trim() !== '');
      setLyricsLines(lines.map(text => ({ text, timestamp: null })));
    }
  }, [lyrics, overlayData]);

  // Calculate which line should be active based on progress
  const getActiveLineIndex = () => {
    if (!progressMs || lyricsLines.length === 0) return -1;
    
    if (isSynced) {
      // Use precise timestamps from LRC
      for (let i = lyricsLines.length - 1; i >= 0; i--) {
        if (lyricsLines[i].timestamp !== null && progressMs >= lyricsLines[i].timestamp) {
          return i;
        }
      }
      return 0; // If before first timestamp, show first line
    } else {
      // Fallback to percentage-based estimation
      if (!durationMs) return -1;
      const progressPercent = progressMs / durationMs;
      const introOffset = 0.05; // 5% for intro
      const adjustedProgress = Math.max(0, Math.min(1, (progressPercent - introOffset) / (1 - introOffset * 2)));
      const activeIndex = Math.floor(adjustedProgress * lyricsLines.length);
      return Math.min(activeIndex, lyricsLines.length - 1);
    }
  };

  const activeLineIndex = getActiveLineIndex();

  // Scroll to active line
  useEffect(() => {
    if (activeLineRef.current && lyricsRef.current) {
      const container = lyricsRef.current;
      const activeLine = activeLineRef.current;
      
      const containerRect = container.getBoundingClientRect();
      const activeLineRect = activeLine.getBoundingClientRect();
      
      const scrollTop = container.scrollTop;
      const containerHeight = containerRect.height;
      const activeLineTop = activeLineRect.top - containerRect.top + scrollTop;
      const activeLineHeight = activeLineRect.height;
      
      // Center the active line in the viewport
      const targetScroll = activeLineTop - (containerHeight / 2) + (activeLineHeight / 2);
      
      container.scrollTo({
        top: targetScroll,
        behavior: 'smooth'
      });
    }
  }, [activeLineIndex, progressMs]);

  if (isLoading) {
    return (
      <div className="lyrics-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading lyrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lyrics-container">
        <div className="error">
          <p>
            <span className="material-icons">error_outline</span>
            {error}
          </p>
          <p className="error-hint">
            Lyrics might not be available for this track.
          </p>
        </div>
      </div>
    );
  }

  if ((!lyrics && !overlayData) || lyricsLines.length === 0) {
    if (overlayData && overlayData.lines && overlayData.lines.length > 0) {
      // If we have overlay data but no lines processed, there might be an issue
      console.warn('Overlay data exists but no lines processed:', overlayData);
    }
    return (
      <div className="lyrics-container">
        <div className="no-lyrics">
          <p>No lyrics available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="lyrics-container" ref={lyricsRef}>
      {wordTranslation && (
        <div 
          className="word-translation-popup"
          style={{
            position: 'fixed',
            left: `${translationPosition.x}px`,
            top: `${translationPosition.y}px`,
            zIndex: 1000
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="word-translation-content">
            <div className="word-translation-original">{wordTranslation.word}</div>
            <div className="word-translation-arrow">→</div>
            <div className="word-translation-translated">{wordTranslation.translation}</div>
            <button 
              className="word-translation-close"
              onClick={() => setWordTranslation(null)}
              aria-label="Close translation"
            >
              ×
            </button>
          </div>
        </div>
      )}
      <div className="lyrics-content">
        <div className={`lyrics-text ${overlayData ? 'overlay-mode' : ''}`}>
          {lyricsLines.map((line, index) => {
            const isActive = index === activeLineIndex;
            const isNearActive = Math.abs(index - activeLineIndex) <= 1;
            
            if (overlayData && line.translated !== undefined) {
              // Overlay mode - show both original and translated
              // Skip empty lines
              if (!line.text && !line.translated) {
                return <div key={index} className="lyrics-line-empty"></div>;
              }
              
              return (
                <div
                  key={index}
                  ref={isActive ? activeLineRef : null}
                  className={`lyrics-line overlay-line ${isActive ? 'active' : ''} ${isNearActive ? 'near-active' : ''}`}
                >
                  <div className="overlay-original">{line.text}</div>
                  <div className="overlay-translated">{line.translated}</div>
                </div>
              );
            } else {
              // Normal mode - show single line with clickable words
              const words = splitIntoWords(line.text);
              return (
                <div
                  key={index}
                  ref={isActive ? activeLineRef : null}
                  className={`lyrics-line ${isActive ? 'active' : ''} ${isNearActive ? 'near-active' : ''}`}
                >
                  {words.map((word, wordIndex) => {
                    // Only make actual words clickable (skip pure whitespace)
                    if (word.trim() === '') {
                      return <span key={wordIndex}>{word}</span>;
                    }
                    return (
                      <Word
                        key={wordIndex}
                        word={word}
                        selectedLanguage={selectedLanguage}
                        onTranslation={handleWordTranslation}
                      />
                    );
                  })}
                </div>
              );
            }
          })}
        </div>
      </div>
    </div>
  );
};

export default LyricsDisplay;

