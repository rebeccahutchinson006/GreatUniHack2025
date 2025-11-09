import React, { useState } from 'react';
import { Artist, Track } from '../types';
import Breadcrumbs from './Breadcrumbs';

interface ArtistPageProps {
  artist: Artist;
  onBack: () => void;
  genreName?: string;
}

const ArrowLeftIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
  </svg>
);

const MusicIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
  </svg>
);

const ArtistPage: React.FC<ArtistPageProps> = ({ artist, onBack, genreName }) => {
  const [selectedTrack, setSelectedTrack] = useState<Track | null>(null);
  
  // Support both imageUrl and image properties
  const imageUrl = artist.imageUrl || artist.image || 'https://picsum.photos/400/400';
  // Support both topSongs and top_tracks properties
  const songs = artist.topSongs || artist.top_tracks || [];
  const trackDetails = artist.track_details || [];
  
  console.log('Artist data:', { artist, trackDetails, hasTrackDetails: trackDetails.length > 0 });
  
  const handleTrackClick = (track: Track) => {
    console.log('Track clicked:', track);
    setSelectedTrack(track);
  };
  
  const handleGoToLyrics = () => {
    window.location.href = 'http://localhost:3000/lyrics';
  };
  
  return (
    <div className="relative -mx-4 sm:-mx-6 lg:-mx-8 -my-8" style={{ width: '100vw', marginLeft: 'calc(-50vw + 50%)' }}>
      <div className="bg-slate-700 w-full py-12 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in">
          {genreName && (
            <Breadcrumbs
              items={[
                { label: 'Home', path: '/' },
                { label: genreName, path: `/genre/${genreName.toLowerCase()}` },
                { label: artist.name }
              ]}
            />
          )}
          
          <div className="flex gap-4 mb-6">
            <button
              onClick={onBack}
              className="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-700 focus:ring-purple-500"
            >
              <ArrowLeftIcon />
              Back
            </button>
            
            <button
              onClick={handleGoToLyrics}
              className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-full transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-700 focus:ring-purple-500"
            >
              <MusicIcon />
              View Live Lyrics
            </button>
          </div>
          
          <div className="flex items-center gap-6 mb-8">
            <div className="w-48 h-48 rounded-lg overflow-hidden shadow-2xl flex-shrink-0">
              <img src={imageUrl} alt={artist.name} className="w-full h-full object-cover" />
            </div>
            <div>
              <h1 className="text-5xl font-extrabold mb-2 tracking-tight text-gray-100">{artist.name}</h1>
              <p className="text-purple-300 text-xl">Top {songs.length} Songs</p>
              {artist.popularity && (
                <p className="text-gray-300 text-sm mt-1">Popularity: {artist.popularity}/100</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Track List */}
        <div className="max-w-3xl">
          <h2 className="text-2xl font-bold text-gray-100 mb-4">
            Track List
            {trackDetails.length > 0 && (
              <span className="ml-3 text-sm text-purple-300 font-normal">Click to play →</span>
            )}
          </h2>
          <ul className="space-y-3">
            {trackDetails.length > 0 ? (
              trackDetails.map((track, index) => (
                <li
                  key={track.id || index}
                  onClick={() => handleTrackClick(track)}
                  className={`flex items-center gap-4 p-4 rounded-lg cursor-pointer transition-all transform hover:scale-[1.02] ${
                    selectedTrack?.id === track.id
                      ? 'bg-purple-600/30 ring-2 ring-purple-500 shadow-lg shadow-purple-500/20'
                      : 'bg-gray-800/50 hover:bg-gray-800 hover:shadow-md'
                  } group`}
                >
                  <span className={`font-bold text-2xl w-12 text-center transition-colors ${
                    selectedTrack?.id === track.id
                      ? 'text-purple-300'
                      : 'text-purple-400 group-hover:text-purple-300'
                  }`}>{index + 1}</span>
                  <div className="flex-grow">
                    <span className={`text-lg block transition-colors ${
                      selectedTrack?.id === track.id
                        ? 'text-purple-100 font-semibold'
                        : 'text-gray-100 group-hover:text-purple-100'
                    }`}>{track.name}</span>
                    {selectedTrack?.id === track.id && (
                      <span className="text-xs text-purple-300 mt-1 flex items-center gap-1">
                        <svg className="w-3 h-3 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z"/>
                        </svg>
                        Now Playing
                      </span>
                    )}
                  </div>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className={`h-5 w-5 transition-all ${
                      selectedTrack?.id === track.id 
                        ? 'text-purple-300 opacity-100' 
                        : 'text-gray-500 opacity-0 group-hover:opacity-100'
                    }`}
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </li>
              ))
            ) : (
              songs.map((song, index) => (
                <li
                  key={index}
                  className="flex items-center gap-4 p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors group"
                >
                  <span className="text-purple-400 font-bold text-2xl w-12 text-center group-hover:text-purple-300 transition-colors">{index + 1}</span>
                  <span className="text-gray-100 text-lg flex-grow group-hover:text-purple-100 transition-colors">{song}</span>
                </li>
              ))
            )}
          </ul>
        </div>
        
        {/* Spotify Embed Player */}
        <div className="lg:sticky lg:top-6 h-fit">
          <h2 className="text-2xl font-bold text-gray-100 mb-4">Now Playing</h2>
          {selectedTrack ? (
            <div className="bg-gray-800/50 rounded-lg p-4 backdrop-blur-sm">
              <div className="mb-4">
                <h3 className="text-xl font-semibold text-purple-300 mb-1">{selectedTrack.name}</h3>
                <p className="text-gray-400 text-sm">by {artist.name}</p>
              </div>
              <iframe
                src={`https://open.spotify.com/embed/track/${selectedTrack.id}?utm_source=generator&theme=0`}
                width="100%"
                height="352"
                frameBorder="0"
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"
                className="rounded-lg"
              ></iframe>
            </div>
          ) : (
            <div className="bg-gray-800/50 rounded-lg p-8 backdrop-blur-sm text-center">
              <div className="text-gray-400 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p className="text-lg">Select a track to play</p>
                <p className="text-sm mt-2">Click on any song from the list to start listening</p>
              </div>
            </div>
          )}
        </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArtistPage;