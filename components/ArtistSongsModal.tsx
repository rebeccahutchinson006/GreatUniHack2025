import React from 'react';
import { Artist } from '../types';

interface ArtistPageProps {
  artist: Artist;
  onBack: () => void;
}

const ArrowLeftIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
  </svg>
);

const ArtistPage: React.FC<ArtistPageProps> = ({ artist, onBack }) => {
  return (
    <div className="animate-fade-in">
      <button
        onClick={onBack}
        className="mb-6 inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-purple-500"
      >
        <ArrowLeftIcon />
        Back
      </button>
      
      <div className="flex items-center gap-6 mb-8">
        <div className="w-48 h-48 rounded-lg overflow-hidden shadow-2xl flex-shrink-0">
          <img src={artist.imageUrl} alt={artist.name} className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="text-5xl font-extrabold mb-2 tracking-tight text-white">{artist.name}</h1>
          <p className="text-purple-400 text-xl">Top 10 Songs</p>
        </div>
      </div>

      <div className="max-w-3xl">
        <ul className="space-y-3">
          {artist.topSongs.map((song, index) => (
            <li
              key={index}
              className="flex items-center gap-4 p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors group"
            >
              <span className="text-purple-400 font-bold text-2xl w-12 text-center group-hover:text-purple-300 transition-colors">{index + 1}</span>
              <span className="text-white text-lg flex-grow group-hover:text-purple-100 transition-colors">{song}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ArtistPage;