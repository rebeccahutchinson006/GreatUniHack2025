import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { MUSIC_SECTIONS, GENRE_MAPPINGS } from '../constants';
import { MusicSectionData, BackendArtistResponse, Artist } from '../types';

interface MusicDataContextType {
  musicData: MusicSectionData[];
  loading: boolean;
  error: string | null;
  getGenreByCountry: (country: string) => MusicSectionData | undefined;
  getArtistById: (artistId: string) => { artist: Artist; genre: MusicSectionData } | undefined;
}

const MusicDataContext = createContext<MusicDataContextType | undefined>(undefined);

export const useMusicData = () => {
  const context = useContext(MusicDataContext);
  if (!context) {
    throw new Error('useMusicData must be used within a MusicDataProvider');
  }
  return context;
};

interface MusicDataProviderProps {
  children: ReactNode;
}

export const MusicDataProvider: React.FC<MusicDataProviderProps> = ({ children }) => {
  const [musicData, setMusicData] = useState<MusicSectionData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMusicData = async () => {
      try {
        setLoading(true);
        
        // Fetch data for all genres in parallel
        const fetchPromises = GENRE_MAPPINGS.map(async (mapping) => {
          try {
            const response = await fetch(`http://localhost:8000/top-artists/${mapping.genre}`);
            
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data: BackendArtistResponse = await response.json();
            
            console.log(`${mapping.genre} API response:`, data);
            
            // Transform backend data to match frontend structure
            const transformedArtists: Artist[] = data.artists.map(artist => {
              console.log(`Transforming ${artist.name}:`, {
                track_details: artist.track_details,
                track_details_length: artist.track_details?.length
              });
              
              return {
                id: artist.id,
                name: artist.name,
                imageUrl: artist.image,
                image: artist.image,
                topSongs: artist.top_tracks,
                top_tracks: artist.top_tracks,
                track_details: artist.track_details,
                popularity: artist.popularity
              };
            });
            
            return {
              title: mapping.title,
              country: mapping.country,
              genre: mapping.genre,
              artists: transformedArtists
            };
          } catch (err) {
            console.error(`Error fetching ${mapping.genre} music data:`, err);
            // Return fallback data for this genre
            return MUSIC_SECTIONS.find(section => section.country === mapping.country) || {
              title: mapping.title,
              country: mapping.country,
              genre: mapping.genre,
              artists: []
            };
          }
        });
        
        const results = await Promise.all(fetchPromises);
        setMusicData(results);
        setError(null);
      } catch (err) {
        console.error('Error fetching music data:', err);
        setError('Failed to load music data. Using fallback data.');
        // Use hardcoded data as fallback
        setMusicData(MUSIC_SECTIONS);
      } finally {
        setLoading(false);
      }
    };

    fetchMusicData();
  }, []);

  const getGenreByCountry = (country: string) => {
    return musicData.find(section => section.country === country);
  };

  const getArtistById = (artistId: string) => {
    for (const genre of musicData) {
      const artist = genre.artists.find(a => a.id === artistId || a.name === artistId);
      if (artist) {
        return { artist, genre };
      }
    }
    return undefined;
  };

  return (
    <MusicDataContext.Provider value={{ musicData, loading, error, getGenreByCountry, getArtistById }}>
      {children}
    </MusicDataContext.Provider>
  );
};
