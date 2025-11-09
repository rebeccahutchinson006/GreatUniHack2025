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
    <div className="relative -mx-4 sm:-mx-6 lg:-mx-8 -my-8" style={{ width: '100vw', marginLeft: 'calc(-50vw + 50%)' }}>
      {/* Top section with dark blue background */}
      <div className="bg-gradient-to-b from-gray-900 to-gray-800 w-full py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 text-white">
            Colliding cultures, unifying music
          </h1>
          <p className="text-gray-300 text-lg sm:text-xl max-w-2xl mx-auto">
            Explore top artists and learn languages with tracks from your dream destinations.
          </p>
        </div>
      </div>
      
      {/* Bottom section with darker blueish grey background - full width */}
      <div className="bg-slate-700 w-full py-12 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          {musicData.map((section) => (
            <MusicSection
              key={section.country}
              section={section}
              onTitleClick={() => handleSelectGenre(section.country)}
              onArtistClick={(artist) => handleSelectArtist(artist, section.country)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
