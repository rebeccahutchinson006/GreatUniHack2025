
import React from 'react';
import { Artist } from '../types';

interface ArtistCardProps {
  artist: Artist;
  onClick?: () => void;
}

const ArtistCard: React.FC<ArtistCardProps> = ({ artist, onClick }) => {
  // Support both imageUrl and image properties
  const imageUrl = artist.imageUrl || artist.image || 'https://picsum.photos/400/400';
  
  return (
    <div className="flex-shrink-0 w-40 sm:w-48 group cursor-pointer" onClick={onClick}>
      <div className="aspect-square rounded-lg overflow-hidden shadow-lg transform group-hover:scale-105 transition-transform duration-300 ease-in-out">
        <img src={imageUrl} alt={artist.name} className="w-full h-full object-cover" />
      </div>
      <p className="mt-2 text-center text-sm sm:text-base font-semibold truncate text-gray-200 group-hover:text-white transition-colors">{artist.name}</p>
    </div>
  );
};

export default ArtistCard;
