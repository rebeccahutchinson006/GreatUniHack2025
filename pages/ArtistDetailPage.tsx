import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMusicData } from '../context/MusicDataContext';
import ArtistPage from '../components/ArtistSongsModal';

const ArtistDetailPage: React.FC = () => {
  const { country, artistId } = useParams<{ country: string; artistId: string }>();
  const navigate = useNavigate();
  const { getArtistById } = useMusicData();

  const artistData = artistId ? getArtistById(decodeURIComponent(artistId)) : undefined;

  const handleBack = () => {
    if (country) {
      navigate(`/genre/${country}`);
    } else {
      navigate('/');
    }
  };

  if (!artistData) {
    return (
      <div className="relative -mx-4 sm:-mx-6 lg:-mx-8 -my-8" style={{ width: '100vw', marginLeft: 'calc(-50vw + 50%)' }}>
        <div className="bg-slate-700 w-full py-12 min-h-screen">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">Artist Not Found</h2>
            <button
              onClick={handleBack}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors"
            >
              Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ArtistPage
      artist={artistData.artist}
      onBack={handleBack}
      genreName={artistData.genre.country}
    />
  );
};

export default ArtistDetailPage;
