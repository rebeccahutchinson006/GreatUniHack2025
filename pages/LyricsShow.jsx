import React, { useState, useEffect } from 'react';
import '../public/Lyrics.css';
import TrackInfo from '../components/TrackInfo';
import LyricsDisplay from '../components/LyricsDisplay';
import { api } from '../services/api';

function LyricsShow() {
  const [userId, setUserId] = useState(null);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [lyrics, setLyrics] = useState(null);
  const [lyricsLoading, setLyricsLoading] = useState(false);
  const [lyricsError, setLyricsError] = useState(null);
  const [lastTrackId, setLastTrackId] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('EN');
  const [translatedLyrics, setTranslatedLyrics] = useState(null);
  const [translating, setTranslating] = useState(false);
  const [translationError, setTranslationError] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [overlayMode, setOverlayMode] = useState(false);
  const [overlayData, setOverlayData] = useState(null);
  const [playbackLoading, setPlaybackLoading] = useState(false);

  // Fetch supported languages on mount
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const data = await api.getSupportedLanguages();
        setSupportedLanguages(data.languages || []);
      } catch (error) {
        console.error('Error fetching supported languages:', error);
        // Set default languages if API fails
        setSupportedLanguages([
          { code: 'EN', name: 'English' },
          { code: 'ES', name: 'Spanish' },
          { code: 'FR', name: 'French' },
          { code: 'DE', name: 'German' },
          { code: 'IT', name: 'Italian' },
          { code: 'PT', name: 'Portuguese' },
          { code: 'JA', name: 'Japanese' },
          { code: 'KO', name: 'Korean' },
          { code: 'ZH', name: 'Chinese' },
        ]);
      }
    };
    fetchLanguages();
  }, []);

  // Check for user_id in URL after OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get('user_id');
    const error = urlParams.get('error');
    
    if (error) {
      console.error('OAuth error:', error);
      alert(`Authentication error: ${error}`);
      // Clean up URL
      window.history.replaceState({}, document.title, '/');
      return;
    }
    
    if (userIdFromUrl) {
      console.log('User ID received from callback:', userIdFromUrl);
      setUserId(userIdFromUrl);
      // Clean up URL
      window.history.replaceState({}, document.title, '/');
    } else {
      // Check localStorage for saved userId
      const savedUserId = localStorage.getItem('spotify_user_id');
      if (savedUserId) {
        console.log('User ID loaded from localStorage:', savedUserId);
        setUserId(savedUserId);
      }
    }
  }, []);

  // Save userId to localStorage
  useEffect(() => {
    if (userId) {
      localStorage.setItem('spotify_user_id', userId);
    }
  }, [userId]);

  // Poll for currently playing track
  useEffect(() => {
    if (!userId) return;

    const fetchCurrentlyPlaying = async () => {
      try {
        const track = await api.getCurrentlyPlaying(userId);
        setCurrentTrack(track);
      } catch (error) {
        console.error('Error fetching currently playing:', error);
        setCurrentTrack(null);
      }
    };

    // Fetch immediately
    fetchCurrentlyPlaying();

    // Poll every 2 seconds
    const interval = setInterval(fetchCurrentlyPlaying, 2000);

    return () => clearInterval(interval);
  }, [userId]);

  // Fetch lyrics when track changes
  useEffect(() => {
    if (!currentTrack) {
      setLyrics(null);
      setTranslatedLyrics(null);
      setLastTrackId(null);
      return;
    }

    const trackId = `${currentTrack.track_name}-${currentTrack.artist_name}`;
    
    // Only fetch if track changed
    if (trackId === lastTrackId) {
      return;
    }

    setLastTrackId(trackId);
    setLyricsLoading(true);
    setLyricsError(null);
    setLyrics(null);
    setTranslatedLyrics(null);

    const fetchLyrics = async () => {
      try {
        const lyricsData = await api.getLyrics(
          currentTrack.track_name,
          currentTrack.artist_name
        );
        setLyrics(lyricsData);
        setLyricsError(null);
      } catch (error) {
        console.error('Error fetching lyrics:', error);
        setLyricsError('Could not fetch lyrics for this track');
        setLyrics(null);
      } finally {
        setLyricsLoading(false);
      }
    };

    fetchLyrics();
  }, [currentTrack, lastTrackId]);

  // Translate lyrics when language changes or lyrics change (full translation mode)
  useEffect(() => {
    if (!lyrics || selectedLanguage === 'EN' || overlayMode) {
      setTranslatedLyrics(null);
      setTranslationError(null);
      return;
    }

    const translateLyrics = async () => {
      setTranslating(true);
      setTranslationError(null);

      try {
        const translationData = await api.translateLyrics(
          lyrics.lyrics || '',
          selectedLanguage,
          null,
          lyrics.lines || null
        );

        // Create a translated lyrics object with the same structure
        const translated = {
          ...lyrics,
          lyrics: translationData.translated_lyrics,
          lines: translationData.translated_lines || lyrics.lines,
        };
        setTranslatedLyrics(translated);
      } catch (error) {
        console.error('Error translating lyrics:', error);
        setTranslationError(error.message || 'Failed to translate lyrics');
        setTranslatedLyrics(null);
      } finally {
        setTranslating(false);
      }
    };

    translateLyrics();
  }, [lyrics, selectedLanguage, overlayMode]);

  // Translate lyrics line-by-line for overlay mode
  useEffect(() => {
    if (!lyrics || selectedLanguage === 'EN' || !overlayMode) {
      setOverlayData(null);
      setTranslationError(null);
      return;
    }

    const translateLinesOverlay = async () => {
      setTranslating(true);
      setTranslationError(null);

      try {
        console.log('Fetching overlay translation...', { 
          lyricsLength: lyrics.lyrics?.length, 
          hasLines: !!lyrics.lines,
          language: selectedLanguage 
        });
        const overlayData = await api.translateLinesOverlay(
          lyrics.lyrics || '',
          selectedLanguage,
          null,
          lyrics.lines || null
        );
        console.log('Overlay data received:', overlayData);
        setOverlayData(overlayData);
      } catch (error) {
        console.error('Error translating lyrics overlay:', error);
        setTranslationError(error.message || 'Failed to translate lyrics line-by-line');
        setOverlayData(null);
      } finally {
        setTranslating(false);
      }
    };

    translateLinesOverlay();
  }, [lyrics, selectedLanguage, overlayMode]);

  const handleLogin = () => {
    api.login();
  };

  const handleLogout = () => {
    setUserId(null);
    setCurrentTrack(null);
    setLyrics(null);
    setLastTrackId(null);
    localStorage.removeItem('spotify_user_id');
  };

  const handlePlaybackToggle = async () => {
    if (!userId || !currentTrack || playbackLoading) return;

    setPlaybackLoading(true);
    try {
      if (currentTrack.is_playing) {
        await api.pause(userId);
      } else {
        await api.play(userId);
      }
      // Wait a moment then fetch updated status
      setTimeout(async () => {
        try {
          const data = await api.getCurrentlyPlaying(userId);
          if (data && data.item) {
            setCurrentTrack(data);
          }
        } catch (error) {
          console.error('Error refreshing playback state:', error);
        }
      }, 500);
    } catch (error) {
      console.error('Error toggling playback:', error);
      alert(error.message || 'Failed to control playback. Make sure Spotify is open and playing.');
    } finally {
      setPlaybackLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>
          <span className="material-icons">headphones</span>
          Live Spotify Lyrics
        </h1>
        {userId ? (
          <button onClick={handleLogout} className="logout-btn">
            <span className="material-icons">logout</span>
            Logout
          </button>
        ) : (
          <button onClick={handleLogin} className="login-btn">
            <span className="material-icons">login</span>
            Login with Spotify
          </button>
        )}
      </header>

      <main className="App-main">
        {userId ? (
          <>
            <TrackInfo 
              track={currentTrack}
              playbackButton={
                currentTrack && (
                  <button
                    className={`playback-btn ${playbackLoading ? 'loading' : ''}`}
                    onClick={handlePlaybackToggle}
                    disabled={playbackLoading}
                    title={currentTrack.is_playing ? 'Pause' : 'Play'}
                  >
                    <span className="material-icons">
                      {playbackLoading ? 'hourglass_empty' : (currentTrack.is_playing ? 'pause' : 'play_arrow')}
                    </span>
                  </button>
                )
              }
            />
            {lyrics && !lyricsLoading && (
              <div className="language-selector">
                <label htmlFor="language-select">
                  <span className="material-icons">translate</span>
                  Translate to:
                </label>
                <select
                  id="language-select"
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  disabled={translating}
                >
                  {supportedLanguages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
                <button
                  className={`overlay-toggle ${overlayMode ? 'active' : ''}`}
                  onClick={() => setOverlayMode(!overlayMode)}
                  disabled={translating || selectedLanguage === 'EN'}
                  title={overlayMode ? 'Switch to full translation' : 'Switch to line-by-line overlay'}
                >
                  <span className="material-icons">
                    {overlayMode ? 'view_agenda' : 'view_column'}
                  </span>
                  {overlayMode ? 'Full Translation' : 'Line Overlay'}
                </button>
                {translating && (
                  <span className="translating-indicator">
                    <span className="spinner-small"></span>
                    Translating...
                  </span>
                )}
                {translationError && (
                  <span className="translation-error">{translationError}</span>
                )}
              </div>
            )}
            <LyricsDisplay
              lyrics={overlayMode ? null : (translatedLyrics || lyrics)}
              overlayData={overlayMode ? overlayData : null}
              isLoading={lyricsLoading || translating}
              error={lyricsError || translationError}
              progressMs={currentTrack?.progress_ms}
              durationMs={currentTrack?.duration_ms}
              selectedLanguage={selectedLanguage}
            />
          </>
        ) : (
          <div className="welcome-screen">
            <div className="welcome-content">
              <h2>Welcome to Live Spotify Lyrics!</h2>
              <p>See the lyrics of whatever you're listening to on Spotify in real-time.</p>
              <button onClick={handleLogin} className="login-btn-large">
                <span className="material-icons">login</span>
                Login with Spotify to Get Started
              </button>
              <div className="features">
                <div className="feature">
                  <span className="material-icons feature-icon">graphic_eq</span>
                  <p>Real-time track detection</p>
                </div>
                <div className="feature">
                  <span className="material-icons feature-icon">lyrics</span>
                  <p>Automatic lyrics display</p>
                </div>
                <div className="feature">
                  <span className="material-icons feature-icon">sync</span>
                  <p>Auto-updates when track changes</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default LyricsShow;
