# React Router Implementation

## Overview
The app now uses **React Router v6** for proper URL-based navigation with clean, shareable URLs.

## Route Structure

```
/ (Home)
├── /genre/:country (Genre Page)
│   └── /genre/:country/artist/:artistId (Artist Detail Page)
```

### Route Examples
- **Home**: `/`
- **Genre**: `/genre/france`, `/genre/spain`, `/genre/japan`, `/genre/germany`
- **Artist**: `/genre/france/artist/4tZwfgrHOc3mvqYlEYSvVi` (using Spotify ID)

## Architecture

### 1. **Context Provider** (`context/MusicDataContext.tsx`)
- Centralized music data management
- Fetches data once on app load
- Provides data to all routes via React Context
- Helper functions:
  - `getGenreByCountry(country)` - Get genre data by country name
  - `getArtistById(artistId)` - Find artist across all genres

### 2. **Layout Component** (`components/Layout.tsx`)
- Wraps all routes
- Contains Header and Footer
- Handles loading state
- Displays error messages
- Uses `<Outlet />` to render child routes

### 3. **Page Components** (`pages/`)

#### HomePage (`pages/HomePage.tsx`)
- Route: `/`
- Displays all genres with artist previews
- Navigation:
  - Click "See All" → Navigate to `/genre/:country`
  - Click artist card → Navigate to `/genre/:country/artist/:artistId`

#### GenrePage (`pages/GenrePage.tsx`)
- Route: `/genre/:country`
- Displays all artists from a specific genre
- Uses `useParams()` to get country from URL
- Navigation:
  - Click artist → Navigate to `/genre/:country/artist/:artistId`
  - Back button → Navigate to `/`

#### ArtistDetailPage (`pages/ArtistDetailPage.tsx`)
- Route: `/genre/:country/artist/:artistId`
- Displays artist details and top tracks
- Uses `useParams()` to get country and artistId from URL
- Navigation:
  - Back button → Navigate to `/genre/:country`

## Key Features

### ✅ **URL-Based Navigation**
- Every page has a unique URL
- URLs are shareable and bookmarkable
- Browser back/forward buttons work correctly

### ✅ **Context API for Data Sharing**
- Music data loaded once at app level
- Shared across all routes via Context
- No prop drilling needed

### ✅ **Type-Safe Routing**
- TypeScript types for route params
- Type-safe context usage with custom hook `useMusicData()`

### ✅ **Smart Breadcrumbs**
- Now use React Router `<Link>` components
- Proper navigation without full page reload
- Path-based instead of callback-based

### ✅ **404 Handling**
- Genre not found shows error message
- Artist not found shows error message
- Easy navigation back to valid routes

## File Structure

```
src/
├── App.tsx                          # Router setup and route definitions
├── context/
│   └── MusicDataContext.tsx         # Context provider for music data
├── pages/
│   ├── HomePage.tsx                 # Home route (/)
│   ├── GenrePage.tsx               # Genre route (/genre/:country)
│   └── ArtistDetailPage.tsx        # Artist route (/genre/:country/artist/:artistId)
├── components/
│   ├── Layout.tsx                  # Layout wrapper with Outlet
│   ├── Header.tsx                  # App header (with navigation)
│   ├── Footer.tsx                  # App footer
│   ├── Breadcrumbs.tsx            # Navigation breadcrumbs (updated for routing)
│   ├── MusicSection.tsx           # Genre section on home
│   ├── CountryPage.tsx            # Genre page content
│   ├── ArtistCard.tsx             # Artist card component
│   └── ArtistSongsModal.tsx       # Artist detail content
└── ...
```

## Benefits of This Structure

### 1. **Separation of Concerns**
- **App.tsx**: Only routing configuration
- **Pages**: Route-level logic and navigation
- **Components**: Reusable UI components
- **Context**: Global state management

### 2. **Better Performance**
- Data fetched once at app load
- No unnecessary re-fetching when navigating
- React Router's optimized navigation

### 3. **Developer Experience**
- Clean, readable route structure
- Easy to add new routes
- Type-safe with TypeScript
- Clear data flow

### 4. **User Experience**
- Real URLs that can be shared
- Browser history works correctly
- Breadcrumbs provide clear navigation
- Fast page transitions

## Usage Examples

### Navigate Programmatically
```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

// Go to genre page
navigate('/genre/france');

// Go to artist page
navigate(`/genre/france/artist/${artistId}`);

// Go back
navigate(-1);

// Go to home
navigate('/');
```

### Access Route Params
```typescript
import { useParams } from 'react-router-dom';

const { country, artistId } = useParams<{ country: string; artistId: string }>();
```

### Use Music Data Context
```typescript
import { useMusicData } from '../context/MusicDataContext';

const { musicData, loading, error, getGenreByCountry, getArtistById } = useMusicData();
```

### Create Links
```typescript
import { Link } from 'react-router-dom';

<Link to="/genre/france" className="...">
  Explore French Music
</Link>
```

## Migration from Old Structure

### Before (State-based)
```typescript
const [view, setView] = useState({ type: 'home' });
setView({ type: 'genre', genre: genreData });
```

### After (Route-based)
```typescript
navigate('/genre/france');
```

### Before (Breadcrumb with callbacks)
```typescript
<Breadcrumbs items={[
  { label: 'Home', onClick: handleBack }
]} />
```

### After (Breadcrumb with paths)
```typescript
<Breadcrumbs items={[
  { label: 'Home', path: '/' }
]} />
```

## Testing Routes

1. **Home**: `http://localhost:5173/`
2. **French Genre**: `http://localhost:5173/genre/france`
3. **Artist**: `http://localhost:5173/genre/france/artist/4tZwfgrHOc3mvqYlEYSvVi`

## Adding New Routes

To add a new route:

1. Create a page component in `pages/`
2. Add route in `App.tsx`:
```typescript
<Route path="your-route" element={<YourPage />} />
```
3. Use `useNavigate()` to navigate to it
4. Access params with `useParams()`

## Best Practices

1. **Always use `navigate()` for programmatic navigation**
2. **Use `<Link>` for clickable navigation elements**
3. **Access data through context, not props**
4. **Use URL params for dynamic data (country, artistId)**
5. **Keep route definitions in App.tsx**
6. **Keep page logic in page components**
