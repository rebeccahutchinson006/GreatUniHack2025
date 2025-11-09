# Libby Translate - Chrome Extension

A Chrome extension that works on Booking.com to discover music from countries you're exploring. Connect your Spotify account and see synchronized lyrics while browsing destinations.

## Features

- 🎵 **Circular Play/Pause Button**: Beautiful circular player with progress timeline
- 🎤 **Synchronized Lyrics**: Real-time lyrics that sync with your Spotify playback
- 🌍 **Country Detection**: Automatically detects the country you're exploring on Booking.com
- 🔗 **Explore Link**: Quick link to explore more of the destination

## Setup

### 1. Backend Setup

Make sure your backend is running on `http://localhost:8000`. The extension will connect to it for:
- Spotify OAuth authentication
- Fetching currently playing tracks
- Getting lyrics
- Controlling playback

### 2. Install the Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder

### 3. Configure (if needed)

The extension uses the backend's existing Spotify OAuth flow. No additional configuration needed in the extension itself, but make sure:
- Backend has `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` set
- Backend's redirect URI is configured in Spotify Developer Dashboard

## Usage

1. Navigate to any Booking.com page
2. Click the extension icon in Chrome toolbar
3. Click "Open Music Player" (or the player will appear automatically)
4. Click "Connect Spotify" to authenticate
5. Start playing music on Spotify
6. See synchronized lyrics and control playback from the extension!

## How It Works

### OAuth Flow

The extension uses a tab-based OAuth flow:
1. Opens backend's `/login` endpoint in a new tab
2. User authenticates with Spotify
3. Backend redirects to `http://localhost:3000/lyrics?user_id=...`
4. Extension detects the `user_id` parameter and stores it
5. Tab is automatically closed

### Country Detection

The extension detects the country from:
- URL patterns (e.g., `booking.com/country-name`)
- Page title
- URL parameters

### Lyrics Syncing

Uses the same syncing logic as the main frontend:
- For synced lyrics (LRC format): Uses precise timestamps
- For plain text lyrics: Estimates based on progress percentage

## File Structure

```
chrome-extension/
├── manifest.json       # Extension manifest
├── background.js      # Service worker for OAuth and API calls
├── content.js         # Script injected into Booking.com pages
├── content.css        # Styles for the music player UI
├── popup.html         # Extension popup HTML
├── popup.js           # Popup script
└── README.md          # This file
```

## Troubleshooting

### "Failed to connect Spotify"
- Make sure the backend is running on `http://localhost:8000`
- Check that Spotify credentials are configured in backend `.env`

### "No track playing"
- Make sure Spotify is open and playing music
- Check that you have Spotify Premium (required for playback control)

### Lyrics not showing
- Some tracks may not have lyrics available
- Check browser console for errors

## Development

To modify the extension:
1. Make changes to the files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension card
4. Reload the Booking.com page

## Notes

- The extension requires the backend to be running
- Spotify Premium is required for playback control features
- The extension only works on Booking.com pages

