// Background service worker for Chrome extension
// Handles Spotify OAuth using chrome.identity API

const API_BASE_URL = 'http://localhost:8000';

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'spotifyLogin') {
    handleSpotifyLogin()
      .then(userId => sendResponse({ success: true, userId }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Indicates we will send a response asynchronously
  }
  
  if (request.action === 'getCurrentlyPlaying') {
    getCurrentlyPlaying(request.userId)
      .then(track => sendResponse({ success: true, track }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (request.action === 'togglePlayback') {
    togglePlayback(request.userId, request.isPlaying)
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (request.action === 'getLyrics') {
    getLyrics(request.trackName, request.artistName)
      .then(lyrics => sendResponse({ success: true, lyrics }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (request.action === 'getTopArtists') {
    getTopArtists(request.country)
      .then(artists => sendResponse({ success: true, artists }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (request.action === 'getAccessToken') {
    getAccessToken(request.userId)
      .then(token => sendResponse({ success: true, token }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

// Handle Spotify OAuth login
// Since Spotify OAuth requires a redirect URI that matches the registered one,
// and Chrome extensions have special redirect URIs, we'll use the backend's
// existing OAuth flow and listen for the callback
async function handleSpotifyLogin() {
  // Check if we have a stored user ID
  const result = await chrome.storage.local.get(['spotify_user_id']);
  if (result.spotify_user_id) {
    return result.spotify_user_id;
  }
  
  // Use backend's login endpoint and handle redirect manually
  // The backend will redirect to localhost:3000/lyrics?user_id=...
  // We'll intercept this redirect and extract the user_id
  const authUrl = `${API_BASE_URL}/login`;
  
  return new Promise((resolve, reject) => {
    // Create a tab to handle the OAuth flow
    chrome.tabs.create({ url: authUrl }, (tab) => {
      let tabClosed = false;
      let listener = null;
      let removedListener = null;
      
      // Helper function to clean up listeners
      const cleanup = () => {
        if (tabClosed) return;
        tabClosed = true;
        if (listener) chrome.tabs.onUpdated.removeListener(listener);
        if (removedListener) chrome.tabs.onRemoved.removeListener(removedListener);
      };
      
      // Listen for tab removal (user closed it)
      removedListener = (removedTabId) => {
        if (removedTabId === tab.id && !tabClosed) {
          cleanup();
          reject(new Error('Login cancelled by user'));
        }
      };
      
      // Listen for tab updates to detect when callback happens
      listener = async (tabId, changeInfo, updatedTab) => {
        if (tabId !== tab.id || tabClosed) return;
        
        if (changeInfo.url) {
          const url = new URL(changeInfo.url);
          
          // Check if this is the callback URL with user_id
          // Backend redirects to: http://localhost:3000/lyrics?user_id=...
          // Or we can check for any URL with user_id parameter
          const userId = url.searchParams.get('user_id');
          
          if (userId) {
            cleanup();
            chrome.tabs.remove(tabId).catch(() => {});
            
            // Store user ID
            await chrome.storage.local.set({ spotify_user_id: userId });
            resolve(userId);
            return;
          }
          
          // Also check for error parameter
          const error = url.searchParams.get('error');
          if (error) {
            cleanup();
            chrome.tabs.remove(tabId).catch(() => {});
            reject(new Error(`OAuth error: ${error}`));
            return;
          }
        }
        
        // Check if tab was closed manually
        if (changeInfo.status === 'complete') {
          // Give it a moment, then check if URL has user_id
          setTimeout(async () => {
            try {
              const currentTab = await chrome.tabs.get(tabId);
              if (currentTab && currentTab.url) {
                const url = new URL(currentTab.url);
                const userId = url.searchParams.get('user_id');
                if (userId) {
                  cleanup();
                  chrome.tabs.remove(tabId).catch(() => {});
                  await chrome.storage.local.set({ spotify_user_id: userId });
                  resolve(userId);
                }
              }
            } catch (e) {
              // Tab might have been closed
            }
          }, 1000);
        }
      };
      
      chrome.tabs.onUpdated.addListener(listener);
      chrome.tabs.onRemoved.addListener(removedListener);
      
      // Timeout after 60 seconds
      setTimeout(() => {
        if (!tabClosed) {
          cleanup();
          chrome.tabs.remove(tab.id).catch(() => {});
          reject(new Error('Login timeout'));
        }
      }, 60000);
    });
  });
}

// Get currently playing track
async function getCurrentlyPlaying(userId) {
  const response = await fetch(`${API_BASE_URL}/currently-playing/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to get currently playing track');
  }
  return response.json();
}

// Toggle playback
async function togglePlayback(userId, isPlaying) {
  const endpoint = isPlaying ? 'pause' : 'play';
  const response = await fetch(`${API_BASE_URL}/${endpoint}/${userId}`, {
    method: 'POST'
  });
  if (!response.ok) {
    throw new Error(`Failed to ${endpoint} track`);
  }
  return response.json();
}

// Get lyrics
async function getLyrics(trackName, artistName) {
  const encodedTrack = encodeURIComponent(trackName);
  const encodedArtist = encodeURIComponent(artistName);
  const response = await fetch(
    `${API_BASE_URL}/lyrics/${encodedTrack}/${encodedArtist}`
  );
  if (!response.ok) {
    throw new Error('Failed to get lyrics');
  }
  return response.json();
}

// Get top artists by country/genre
async function getTopArtists(country) {
  // Map country to genre/search term
  const countryToGenre = {
    'France': 'french',
    'Spain': 'spanish',
    'Italy': 'italian',
    'Germany': 'german',
    'Portugal': 'portuguese',
    'Japan': 'japanese',
    'Korea': 'k-pop',
    'China': 'chinese',
    'Mexico': 'mexican',
    'Brazil': 'brazilian',
    'Argentina': 'argentinian',
    'India': 'indian',
  };
  
  const genre = countryToGenre[country] || country.toLowerCase();
  const response = await fetch(`${API_BASE_URL}/top-artists/${encodeURIComponent(genre)}?limit=10`);
  if (!response.ok) {
    throw new Error('Failed to get top artists');
  }
  return response.json();
}

// Get user's access token from backend
async function getAccessToken(userId) {
  const response = await fetch(`${API_BASE_URL}/user-token/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to get access token');
  }
  const data = await response.json();
  return data.access_token;
}

// Helper function to generate random string
function generateRandomString(length) {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

