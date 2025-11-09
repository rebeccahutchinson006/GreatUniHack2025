import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMusicData } from '../context/MusicDataContext';
import MusicSection from '../components/MusicSection';
import { Artist } from '../types';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { musicData } = useMusicData();

  const handleSelectGenre = (country: string) => {
    navigate(`/genre/${country.toLowerCase()}`);
  };

  const handleSelectArtist = (artist: Artist, country: string) => {
    navigate(`/genre/${country.toLowerCase()}/artist/${encodeURIComponent(artist.id || artist.name)}`);
  };

  return (
    <>
      <div className="text-center mb-12">
        <h1 className="text-5xl sm:text-6xl font-extrabold mb-4 bg-gradient-to-r from-purple-400 via-pink-500 to-purple-600 bg-clip-text text-transparent">
          Discover Music From Around the World
        </h1>
        <p className="text-gray-300 text-lg sm:text-xl max-w-2xl mx-auto">
          Explore top artists and their most popular tracks from different cultures and genres
        </p>
      </div>
      
      <div className="space-y-12">
        {musicData.map((section) => (
          <MusicSection
            key={section.country}
            section={section}
            onTitleClick={() => handleSelectGenre(section.country)}
            onArtistClick={(artist) => handleSelectArtist(artist, section.country)}
          />
        ))}
      </div>
    </>
  );
};

export default HomePage;
