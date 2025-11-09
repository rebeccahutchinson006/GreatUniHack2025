<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Music Discovery App

A music discovery application that showcases top artists from different regions/genres with integration between a React frontend and FastAPI backend using the Spotify API.

## Project Structure

```
.
├── backend/              # FastAPI backend server
│   ├── server.py        # Main server file
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables (create from .env.example)
├── components/          # React components
├── App.tsx             # Main React application
├── types.ts            # TypeScript type definitions
├── constants.ts        # Application constants and genre mappings
└── package.json        # Node.js dependencies
```

## Features

- 🎵 Discover top artists by genre/region (French, Spanish, Japanese, German)
- 🎨 Beautiful UI with artist cards and detailed artist pages
- 🔄 Real-time data from Spotify API
- 📱 Responsive design
- 🎯 Fallback to local data if API is unavailable

## Setup Instructions

### Frontend Setup

**Prerequisites:** Node.js

1. **Install dependencies:**
   ```powershell
   npm install
   ```

2. **Set the `GEMINI_API_KEY` in `.env.local`** (if using AI features)

3. **Run the development server:**
   ```powershell
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

### Backend Setup

**Prerequisites:** Python 3.8+

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Get your Spotify API credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Add your credentials to the `.env` file:
     ```
     SPOTIFY_CLIENT_ID=your_actual_client_id
     SPOTIFY_CLIENT_SECRET=your_actual_client_secret
     ```

4. **Run the backend server:**
   ```powershell
   python server.py
   ```
   
   Or with uvicorn:
   ```powershell
   uvicorn server:app --reload --port 8000
   ```

The backend API will be available at `http://localhost:8000`

## API Integration

The frontend fetches data from the backend for each genre:
- `/top-artists/french` - French artists
- `/top-artists/spanish` - Spanish artists
- `/top-artists/japanese` - Japanese artists
- `/top-artists/german` - German artists

Each endpoint returns:
```json
{
  "artists": [
    {
      "id": "artist_id",
      "name": "Artist Name",
      "image": "https://...",
      "popularity": 82,
      "top_tracks": ["Track 1", "Track 2", ...]
    }
  ]
}
```

## Running Both Frontend and Backend

1. **Terminal 1 - Backend:**
   ```powershell
   cd backend
   python server.py
   ```

2. **Terminal 2 - Frontend:**
   ```powershell
   npm run dev
   ```

## How It Works

1. The frontend (`App.tsx`) fetches data from the backend for all genres in parallel
2. The backend (`server.py`) queries the Spotify API for top artists matching each genre
3. For each artist, it fetches their top 10 tracks
4. The data is transformed to match the frontend's expected structure
5. If the backend is unavailable, the app falls back to hardcoded data from `constants.ts`

## Technologies Used

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS

### Backend
- FastAPI
- Python 3
- Spotify Web API
- CORS middleware for cross-origin requests

## Troubleshooting

### Backend Issues
- **"Failed to authenticate with Spotify"**: Check your Spotify credentials in `.env`
- **CORS errors**: Ensure the frontend URL is in the `allow_origins` list in `server.py`

### Frontend Issues
- **"Failed to load music data"**: Make sure the backend is running on `http://localhost:8000`
- **Using fallback data**: The app will show this message if it can't reach the backend

## AI Studio

View your app in AI Studio: https://ai.studio/apps/drive/19was2G88iVtocTrLbOWHWyh26EvaX6-H

