# Backend-Frontend Integration Guide

## Overview
This document explains how the backend and frontend work together.

## Data Flow

1. **Frontend Request** (`App.tsx`)
   - On load, fetches data for all genres: `french`, `spanish`, `japanese`, `german`
   - Makes parallel requests to: `http://localhost:8000/top-artists/{genre}`

2. **Backend Processing** (`backend/server.py`)
   - Receives genre parameter
   - Authenticates with Spotify API
   - Searches for top artists matching the genre
   - Fetches top 10 tracks for each artist
   - Returns formatted JSON response

3. **Frontend Display**
   - Transforms backend data to match component structure
   - Displays artists in scrollable cards
   - Shows artist details and top tracks on click

## Data Structure Compatibility

### Backend Response Format
```typescript
{
  "artists": [
    {
      "id": "string",
      "name": "string",
      "image": "string",
      "popularity": number,
      "top_tracks": string[]
    }
  ]
}
```

### Frontend Internal Format
```typescript
{
  title: "string",
  country: "string",
  genre: "string",
  artists: [
    {
      id: "string",
      name: "string",
      imageUrl: "string",  // mapped from backend 'image'
      topSongs: string[],  // mapped from backend 'top_tracks'
      popularity: number
    }
  ]
}
```

## Component Updates

### Updated Files
1. **`types.ts`** - Added flexible Artist interface supporting both formats
2. **`constants.ts`** - Added GENRE_MAPPINGS for backend integration
3. **`App.tsx`** - Implemented parallel genre fetching with data transformation
4. **`ArtistCard.tsx`** - Supports both `imageUrl` and `image` properties
5. **`ArtistSongsModal.tsx`** - Supports both `topSongs` and `top_tracks` properties

## Error Handling

### Backend Unavailable
- Frontend falls back to hardcoded data from `constants.ts`
- User sees a warning message: "Failed to load music data. Using fallback data."

### Spotify API Issues
- Backend returns 500 error with details
- Frontend catches error and uses fallback data

## Environment Variables

### Backend (`.env`)
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Frontend (`.env.local`)
```
GEMINI_API_KEY=your_api_key  # Optional, for AI features
```

## Testing the Integration

1. **Start Backend:**
   ```powershell
   cd backend
   python server.py
   ```

2. **Test Backend Endpoint:**
   ```powershell
   curl http://localhost:8000/top-artists/french
   ```

3. **Start Frontend:**
   ```powershell
   npm run dev
   ```

4. **Verify:**
   - Open browser to `http://localhost:5173`
   - Check Network tab for API calls
   - Verify artist images are from Spotify (not picsum.photos)
   - Check for popularity scores in artist details

## Quick Start (Both Servers)

Run the PowerShell script:
```powershell
.\start-servers.ps1
```

This will:
- Check for `.env` file
- Start backend on port 8000
- Start frontend on port 5173
- Open in separate terminal windows

## Customization

### Add More Genres
1. Add to `constants.ts` GENRE_MAPPINGS:
   ```typescript
   { title: "Discover Korean Beats", country: "Korea", genre: "korean" }
   ```

2. Backend automatically handles any genre search query

### Change Number of Artists
Modify the `limit` parameter in `App.tsx`:
```typescript
const response = await fetch(`http://localhost:8000/top-artists/${mapping.genre}?limit=20`);
```

### Change Port
Backend: Edit `server.py` line with `uvicorn.run(app, host="0.0.0.0", port=8000)`
Frontend: Update `GENRE_MAPPINGS` API calls in `App.tsx`
