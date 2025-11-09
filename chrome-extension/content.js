// Content script that injects the music player UI into booking.com pages
// Uses Spotify Web Playback SDK for direct playback

const API_BASE_URL = 'http://localhost:8000';

// Global state
let player = null;
let deviceId = null;
let accessToken = null;
let userId = null;
let currentTrack = null;
let playlist = [];
let currentTrackIndex = 0;
let isPlaying = false;
let progressInterval = null;

// Create and inject the music player UI
function createMusicPlayer() {
  // Remove existing player if it exists
  const existingPlayer = document.getElementById('libby-music-player');
  if (existingPlayer) {
    existingPlayer.remove();
  }
  
  // Detect country from URL or page content
  const country = detectCountry();
  
  // Create player container
  const playerEl = document.createElement('div');
  playerEl.id = 'libby-music-player';
  playerEl.innerHTML = `
    <div class="libby-player-container">
      <div class="libby-player-header">
        <h3>🎵 Discover Music</h3>
        <button id="libby-close-btn" class="libby-close-btn">×</button>
      </div>
      <div class="libby-player-content">
        <div id="libby-login-section" class="libby-login-section">
          <p>Connect your Spotify account to discover music from ${country}</p>
          <button id="libby-spotify-login" class="libby-spotify-btn">
            Connect Spotify
          </button>
        </div>
        <div id="libby-loading-section" class="libby-loading-section" style="display: none;">
          <div class="libby-spinner"></div>
          <p>Loading music from ${country}...</p>
        </div>
        <div id="libby-player-section" class="libby-player-section" style="display: none;">
          <div class="libby-playlist-info">
            <div id="libby-playlist-status" class="libby-playlist-status">Playing from ${country}</div>
            <div id="libby-playlist-progress" class="libby-playlist-progress">Track 1 of ${playlist.length}</div>
          </div>
          <div class="libby-circular-player">
            <svg class="libby-progress-ring" width="200" height="200">
              <circle
                class="libby-progress-ring-circle"
                stroke="#1DB954"
                stroke-width="4"
                fill="transparent"
                r="90"
                cx="100"
                cy="100"
                transform="rotate(-90 100 100)"
              />
            </svg>
            <button id="libby-play-pause-btn" class="libby-play-pause-btn">
              <span class="libby-play-icon">▶</span>
              <span class="libby-pause-icon" style="display: none;">⏸</span>
            </button>
          </div>
          <div class="libby-track-info">
            <div id="libby-track-name" class="libby-track-name">No track playing</div>
            <div id="libby-artist-name" class="libby-artist-name">—</div>
          </div>
          <div id="libby-lyrics-container" class="libby-lyrics-container">
            <div class="libby-lyrics-loading">Loading lyrics...</div>
          </div>
          <div class="libby-explore-link">
            <a id="libby-explore-link" href="#" target="_blank">
              Explore more of ${country} →
            </a>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Inject styles if not already present
  if (!document.getElementById('libby-player-styles')) {
    const link = document.createElement('link');
    link.id = 'libby-player-styles';
    link.rel = 'stylesheet';
    link.href = chrome.runtime.getURL('content.css');
    document.head.appendChild(link);
  }
  
  // Load Spotify Web Playback SDK
  if (!window.Spotify) {
    const script = document.createElement('script');
    script.src = 'https://sdk.scdn.co/spotify-player.js';
    script.onload = () => {
      window.onSpotifyWebPlaybackSDKReady = initializeSpotifyPlayer;
    };
    document.head.appendChild(script);
  } else {
    initializeSpotifyPlayer();
  }
  
  // Append to page
  document.body.appendChild(playerEl);
  
  // Setup event listeners
  setupEventListeners(country);
  
  // Check if user is already logged in
  checkAuthStatus(country);
}

// Detect country from booking.com URL or page
function detectCountry() {
  const url = window.location.href;
  
  // Try to extract country from URL patterns
  const countryPatterns = [
    /booking\.com\/.*\/([a-z]{2})\//i,
    /country=([a-z]{2})/i,
  ];
  
  for (const pattern of countryPatterns) {
    const match = url.match(pattern);
    if (match) {
      const countryCode = match[1].toUpperCase();
      return getCountryName(countryCode);
    }
  }
  
  // Try to detect from page title or content
  const title = document.title.toLowerCase();
  const countryMap = {
    'france': 'France',
    'spain': 'Spain',
    'italy': 'Italy',
    'germany': 'Germany',
    'portugal': 'Portugal',
    'japan': 'Japan',
    'korea': 'Korea',
    'china': 'China',
  };
  
  for (const [key, value] of Object.entries(countryMap)) {
    if (title.includes(key)) {
      return value;
    }
  }
  
  return 'this destination';
}

// Get country name from country code
function getCountryName(code) {
  const countryNames = {
    'FR': 'France', 'ES': 'Spain', 'IT': 'Italy', 'DE': 'Germany',
    'PT': 'Portugal', 'JP': 'Japan', 'KR': 'Korea', 'CN': 'China',
    'US': 'United States', 'GB': 'United Kingdom', 'MX': 'Mexico',
    'BR': 'Brazil', 'AR': 'Argentina', 'AU': 'Australia', 'IN': 'India',
  };
  return countryNames[code] || code;
}

// Setup event listeners
function setupEventListeners(country) {
  // Close button
  const closeBtn = document.getElementById('libby-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      const playerEl = document.getElementById('libby-music-player');
      if (playerEl) {
        playerEl.style.display = 'none';
      }
    });
  }
  
  // Spotify login button
  const loginBtn = document.getElementById('libby-spotify-login');
  if (loginBtn) {
    loginBtn.addEventListener('click', () => handleSpotifyLogin(country));
  }
  
  // Play/pause button
  const playPauseBtn = document.getElementById('libby-play-pause-btn');
  if (playPauseBtn) {
    playPauseBtn.addEventListener('click', handlePlayPause);
  }
  
  // Explore link
  const exploreLink = document.getElementById('libby-explore-link');
  if (exploreLink) {
    exploreLink.href = `https://booking.com/searchresults.html?ss=${encodeURIComponent(country)}`;
  }
}

// Check if user is authenticated
async function checkAuthStatus(country) {
  const result = await chrome.storage.local.get(['spotify_user_id']);
  if (result.spotify_user_id) {
    userId = result.spotify_user_id;
    await initializePlayerAndPlaylist(country);
  }
}

// Handle Spotify login
async function handleSpotifyLogin(country) {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'spotifyLogin' });
    if (response.success) {
      userId = response.userId;
      await initializePlayerAndPlaylist(country);
    } else {
      alert('Failed to connect Spotify: ' + response.error);
    }
  } catch (error) {
    console.error('Login error:', error);
    alert('Failed to connect Spotify. Please make sure the backend is running on http://localhost:8000');
  }
}

// Initialize player and load playlist
async function initializePlayerAndPlaylist(country) {
  try {
    // Show loading
    const loginSection = document.getElementById('libby-login-section');
    const loadingSection = document.getElementById('libby-loading-section');
    const playerSection = document.getElementById('libby-player-section');
    
    if (loginSection) loginSection.style.display = 'none';
    if (loadingSection) loadingSection.style.display = 'block';
    if (playerSection) playerSection.style.display = 'none';
    
    // Get access token
    const tokenResponse = await chrome.runtime.sendMessage({
      action: 'getAccessToken',
      userId
    });
    
    if (!tokenResponse.success) {
      throw new Error(tokenResponse.error);
    }
    
    accessToken = tokenResponse.token;
    
    // Fetch top artists for country
    const artistsResponse = await chrome.runtime.sendMessage({
      action: 'getTopArtists',
      country
    });
    
    if (!artistsResponse.success) {
      throw new Error(artistsResponse.error);
    }
    
    // Build playlist from top tracks
    playlist = [];
    for (const artist of artistsResponse.artists.artists) {
      if (artist.track_details && artist.track_details.length > 0) {
        for (const track of artist.track_details) {
          if (track.uri) {
            playlist.push({
              uri: track.uri,
              name: track.name,
              artist: artist.name,
              id: track.id
            });
          }
        }
      }
    }
    
    if (playlist.length === 0) {
      throw new Error('No tracks found for this country');
    }
    
    // Initialize Spotify player (will be called when SDK is ready)
    if (window.Spotify && window.Spotify.Player) {
      initializeSpotifyPlayer();
    } else {
      // Wait for SDK to load
      window.onSpotifyWebPlaybackSDKReady = initializeSpotifyPlayer;
    }
    
  } catch (error) {
    console.error('Error initializing player:', error);
    alert('Failed to load music: ' + error.message);
    const loadingSection = document.getElementById('libby-loading-section');
    const loginSection = document.getElementById('libby-login-section');
    if (loadingSection) loadingSection.style.display = 'none';
    if (loginSection) loginSection.style.display = 'block';
  }
}

// Initialize Spotify Web Playback SDK
function initializeSpotifyPlayer() {
  if (!accessToken) return;
  
  if (player) {
    player.disconnect();
  }
  
  player = new window.Spotify.Player({
    name: 'Libby Translate Player',
    getOAuthToken: cb => { cb(accessToken); },
    volume: 0.5
  });
  
  // Error handling
  player.addListener('initialization_error', ({ message }) => {
    console.error('Initialization error:', message);
  });
  
  player.addListener('authentication_error', ({ message }) => {
    console.error('Authentication error:', message);
    alert('Spotify authentication failed. Please reconnect.');
  });
  
  player.addListener('account_error', ({ message }) => {
    console.error('Account error:', message);
    alert('Spotify Premium required for playback.');
  });
  
  // Ready
  player.addListener('ready', ({ device_id }) => {
    console.log('Ready with Device ID', device_id);
    deviceId = device_id;
    
    // Start playing first track
    playTrack(0);
  });
  
  // Not ready
  player.addListener('not_ready', ({ device_id }) => {
    console.log('Device ID has gone offline', device_id);
  });
  
  // Playback state updates
  player.addListener('player_state_changed', async (state) => {
    if (!state) return;
    
    const track = state.track_window.current_track;
    if (track) {
      currentTrack = {
        name: track.name,
        artist: track.artists.map(a => a.name).join(', '),
        duration_ms: track.duration_ms,
        progress_ms: state.position,
        is_playing: !state.paused
      };
      
      updateTrackInfo(currentTrack);
      updatePlaybackState(!state.paused);
      updateProgress(state.position, track.duration_ms);
      updateLyrics(currentTrack);
      
      // Check if track ended (position is near end and paused)
      if (state.paused && state.position > 0 && 
          Math.abs(state.position - track.duration_ms) < 2000) {
        // Track ended, play next
        setTimeout(() => {
          playNextTrack();
        }, 500);
      }
    }
  });
  
  // Connect to the player
  player.connect();
  
  // Show player section
  const loadingSection = document.getElementById('libby-loading-section');
  const playerSection = document.getElementById('libby-player-section');
  if (loadingSection) loadingSection.style.display = 'none';
  if (playerSection) playerSection.style.display = 'block';
  
  // Update playlist progress
  updatePlaylistProgress();
}

// Play a track by index
async function playTrack(index) {
  if (index < 0 || index >= playlist.length) return;
  
  currentTrackIndex = index;
  const track = playlist[index];
  
  try {
    // Transfer playback to our device first
    const transferResponse = await fetch(`https://api.spotify.com/v1/me/player`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        device_ids: [deviceId]
      })
    });
    
    // Wait a bit for transfer to complete
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Start playback
    const playResponse = await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        uris: [track.uri]
      })
    });
    
    if (!playResponse.ok) {
      const errorText = await playResponse.text();
      console.error('Play error:', playResponse.status, errorText);
    }
    
    updatePlaylistProgress();
  } catch (error) {
    console.error('Error playing track:', error);
  }
}

// Play next track
function playNextTrack() {
  if (currentTrackIndex < playlist.length - 1) {
    playTrack(currentTrackIndex + 1);
  } else {
    // Loop back to start
    playTrack(0);
  }
}

// Handle play/pause
async function handlePlayPause() {
  if (!player) return;
  
  const state = await player.getCurrentState();
  if (!state) {
    console.error('Player state not available');
    return;
  }
  
  if (state.paused) {
    player.resume();
  } else {
    player.pause();
  }
}

// Update track info display
function updateTrackInfo(track) {
  const trackNameEl = document.getElementById('libby-track-name');
  const artistNameEl = document.getElementById('libby-artist-name');
  
  if (trackNameEl) trackNameEl.textContent = track.name || 'No track playing';
  if (artistNameEl) artistNameEl.textContent = track.artist || '—';
}

// Update playback state
function updatePlaybackState(playing) {
  isPlaying = playing;
  const playIcon = document.querySelector('.libby-play-icon');
  const pauseIcon = document.querySelector('.libby-pause-icon');
  
  if (playing) {
    if (playIcon) playIcon.style.display = 'none';
    if (pauseIcon) pauseIcon.style.display = 'inline';
  } else {
    if (playIcon) playIcon.style.display = 'inline';
    if (pauseIcon) pauseIcon.style.display = 'none';
  }
}

// Update progress ring
function updateProgress(progressMs, durationMs) {
  if (!durationMs) return;
  
  const progress = progressMs / durationMs;
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (progress * circumference);
  
  const circle = document.querySelector('.libby-progress-ring-circle');
  if (circle) {
    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = offset;
  }
}

// Update playlist progress
function updatePlaylistProgress() {
  const progressEl = document.getElementById('libby-playlist-progress');
  if (progressEl) {
    progressEl.textContent = `Track ${currentTrackIndex + 1} of ${playlist.length}`;
  }
}

// Update lyrics display
let currentTrackId = null;
let lyricsData = null;

async function updateLyrics(track) {
  if (!track || !track.name || !track.artist) {
    return;
  }
  
  const trackId = `${track.name}-${track.artist}`;
  if (trackId === currentTrackId && lyricsData) {
    updateActiveLyricLine(track.progress_ms, track.duration_ms);
    return;
  }
  
  currentTrackId = trackId;
  
  // Show loading
  const lyricsContainer = document.getElementById('libby-lyrics-container');
  if (lyricsContainer) {
    lyricsContainer.innerHTML = '<div class="libby-lyrics-loading">Loading lyrics...</div>';
  }
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getLyrics',
      trackName: track.name,
      artistName: track.artist
    });
    
    if (response.success && response.lyrics) {
      lyricsData = response.lyrics;
      renderLyrics(response.lyrics);
      updateActiveLyricLine(track.progress_ms, track.duration_ms);
    } else {
      if (lyricsContainer) {
        lyricsContainer.innerHTML = '<div class="libby-lyrics-error">No lyrics available</div>';
      }
    }
  } catch (error) {
    console.error('Error fetching lyrics:', error);
    if (lyricsContainer) {
      lyricsContainer.innerHTML = '<div class="libby-lyrics-error">Failed to load lyrics</div>';
    }
  }
}

// Render lyrics
function renderLyrics(lyrics) {
  const lyricsContainer = document.getElementById('libby-lyrics-container');
  if (!lyricsContainer) return;
  
  let html = '<div class="libby-lyrics-text">';
  
  if (lyrics.synced && lyrics.lines) {
    lyrics.lines.forEach((line, index) => {
      html += `<div class="libby-lyrics-line" data-index="${index}" data-timestamp="${line.timestamp_ms || 0}">${line.text}</div>`;
    });
  } else {
    const lines = lyrics.lyrics.split('\n').filter(l => l.trim());
    lines.forEach((line, index) => {
      html += `<div class="libby-lyrics-line" data-index="${index}">${line}</div>`;
    });
  }
  
  html += '</div>';
  lyricsContainer.innerHTML = html;
}

// Update active lyric line
function updateActiveLyricLine(progressMs, durationMs) {
  if (!lyricsData) return;
  
  const lines = document.querySelectorAll('.libby-lyrics-line');
  if (lines.length === 0) return;
  
  let activeIndex = -1;
  
  if (lyricsData.synced && lyricsData.lines) {
    for (let i = lyricsData.lines.length - 1; i >= 0; i--) {
      const line = lyricsData.lines[i];
      if (line.timestamp_ms && progressMs >= line.timestamp_ms) {
        activeIndex = i;
        break;
      }
    }
    if (activeIndex === -1) activeIndex = 0;
  } else {
    if (durationMs) {
      const progress = progressMs / durationMs;
      activeIndex = Math.floor(progress * lines.length);
      activeIndex = Math.min(activeIndex, lines.length - 1);
    }
  }
  
  lines.forEach((line, index) => {
    line.classList.remove('active', 'near-active');
    if (index === activeIndex) {
      line.classList.add('active');
    } else if (Math.abs(index - activeIndex) <= 1) {
      line.classList.add('near-active');
    }
  });
  
  if (activeIndex >= 0 && lines[activeIndex]) {
    lines[activeIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createMusicPlayer);
} else {
  createMusicPlayer();
}

// Re-inject if page changes (SPA navigation)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(createMusicPlayer, 1000);
  }
}).observe(document, { subtree: true, childList: true });
