
import React, { useState } from 'react';
import { MusicSectionData, Artist } from '../types';
import ArtistCard from './ArtistCard';
import ArtistPage from './ArtistSongsModal';

interface MusicSectionProps {
  section: MusicSectionData;
  onTitleClick: () => void;
  onArtistClick?: (artist: Artist) => void;
}

const ArrowRightIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
  </svg>
);

const MusicSection: React.FC<MusicSectionProps> = ({ section, onTitleClick, onArtistClick }) => {
  const handleArtistClick = (artist: Artist) => {
    if (onArtistClick) {
      onArtistClick(artist);
    }
  };

  return (
    <section>
      <div
        className="flex items-center justify-between mb-4 cursor-pointer group"
        onClick={onTitleClick}
      >
        <h2 className="text-3xl font-bold text-gray-100 group-hover:text-purple-300 transition-colors">{section.title}</h2>
        <div className="flex items-center text-purple-300 group-hover:text-gray-100 transition-colors">
          <span className="hidden sm:inline mr-2 font-semibold">See All</span>
          <ArrowRightIcon />
        </div>
      </div>
      <div className="flex overflow-x-auto space-x-4 lg:space-x-6 pb-4 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
        {section.artists.map((artist) => (
          <ArtistCard
            key={artist.id || artist.name}
            artist={artist}
            onClick={() => handleArtistClick(artist)}
          />
        ))}
      </div>
    </section>
  );
};

export default MusicSection;
