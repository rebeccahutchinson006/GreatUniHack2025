import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMusicData } from '../context/MusicDataContext';
import CountryPage from '../components/CountryPage';
import { Artist } from '../types';

const GenrePage: React.FC = () => {
  const { country } = useParams<{ country: string }>();
  const navigate = useNavigate();
  const { getGenreByCountry } = useMusicData();

  const genreData = getGenreByCountry(
    country ? country.charAt(0).toUpperCase() + country.slice(1) : ''
  );

  const handleBack = () => {
    navigate('/');
  };

  const handleArtistClick = (artist: Artist) => {
    navigate(`/genre/${country}/artist/${encodeURIComponent(artist.id || artist.name)}`);
  };

  if (!genreData) {
    return (
      <div className="text-center py-12">
        <h2 className="text-3xl font-bold text-white mb-4">Genre Not Found</h2>
        <button
          onClick={handleBack}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors"
        >
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <CountryPage 
      section={genreData} 
      onBack={handleBack}
      onArtistClick={handleArtistClick}
    />
  );
};

export default GenrePage;
