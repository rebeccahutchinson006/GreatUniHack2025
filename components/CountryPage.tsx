
import React, { useState } from 'react';
import { MusicSectionData, Artist } from '../types';
import ArtistCard from './ArtistCard';
import ArtistPage from './ArtistSongsModal';
import Breadcrumbs from './Breadcrumbs';

interface CountryPageProps {
  section: MusicSectionData;
  onBack: () => void;
  onArtistClick?: (artist: Artist) => void;
}

const ArrowLeftIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
);

const CountryPage: React.FC<CountryPageProps> = ({ section, onBack, onArtistClick }) => {
  const handleArtistClick = (artist: Artist) => {
    if (onArtistClick) {
      onArtistClick(artist);
    }
  };

  return (
    <div className="relative -mx-4 sm:-mx-6 lg:-mx-8 -my-8" style={{ width: '100vw', marginLeft: 'calc(-50vw + 50%)' }}>
      <div className="bg-slate-700 w-full py-12 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in">
          <Breadcrumbs
            items={[
              { label: 'Home', path: '/' },
              { label: section.country }
            ]}
          />
          
          <button
            onClick={onBack}
            className="mb-6 inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-700 focus:ring-purple-500"
          >
            <ArrowLeftIcon />
            Back to Discover
          </button>
          
          <div className="mb-8">
            <h1 className="text-4xl sm:text-5xl font-extrabold mb-2 tracking-tight text-gray-100">{section.title}</h1>
            <p className="text-gray-300 text-lg">
              Explore {section.artists.length} top artists from {section.country}
            </p>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 sm:gap-6">
            {section.artists.map((artist) => (
              <ArtistCard
                key={artist.id || artist.name}
                artist={artist}
                onClick={() => handleArtistClick(artist)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CountryPage;
