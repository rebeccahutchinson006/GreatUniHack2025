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
  const [showLyricsPrompt, setShowLyricsPrompt] = useState(false);
  const [lastClickedTrack, setLastClickedTrack] = useState<Track | null>(null);
  
  // Support both imageUrl and image properties
  const imageUrl = artist.imageUrl || artist.image || 'https://picsum.photos/400/400';
  // Support both topSongs and top_tracks properties
  const songs = artist.topSongs || artist.top_tracks || [];
  const trackDetails = artist.track_details || [];
  
  console.log('Artist data:', { artist, trackDetails, hasTrackDetails: trackDetails.length > 0 });
  
  // Detect when user returns to the tab
  React.useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && lastClickedTrack) {
        // User returned to the tab after clicking a track
        setTimeout(() => {
          setShowLyricsPrompt(true);
        }, 500); // Small delay for better UX
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [lastClickedTrack]);
  
  const handleTrackClick = (track: Track) => {
    console.log('Track clicked:', track);
    setSelectedTrack(track);
    setLastClickedTrack(track);
    
    // Open in Spotify desktop app using spotify: URI
    if (track.uri) {
      window.open(track.uri, '_blank');
    }
  };
  
  const handleGoToLyrics = () => {
    window.location.href = 'http://localhost:3000/lyrics';
  };
  
  const handleViewLyricsFromPrompt = () => {
    setShowLyricsPrompt(false);
    window.location.href = 'http://localhost:3000/lyrics';
  };
  
  const handleDismissPrompt = () => {
    setShowLyricsPrompt(false);
    setLastClickedTrack(null);
  };
  
  return (
    <div className="animate-fade-in">
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
          className="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-purple-500"
        >
          <ArrowLeftIcon />
          Back
        </button>
        
        <button
          onClick={handleGoToLyrics}
          className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-full transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-purple-500"
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
          <h1 className="text-5xl font-extrabold mb-2 tracking-tight text-white">{artist.name}</h1>
          <p className="text-purple-400 text-xl">Top {songs.length} Songs</p>
          {artist.popularity && (
            <p className="text-gray-400 text-sm mt-1">Popularity: {artist.popularity}/100</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Track List */}
        <div className="max-w-3xl">
          <h2 className="text-2xl font-bold text-white mb-4">
            Track List
            {trackDetails.length > 0 && (
              <span className="ml-3 text-sm text-purple-400 font-normal">Click to play in Spotify →</span>
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
                        : 'text-white group-hover:text-purple-100'
                    }`}>{track.name}</span>
                    {selectedTrack?.id === track.id && (
                      <span className="text-xs text-purple-300 mt-1 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                        </svg>
                        Opening in Spotify
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <svg 
                      className={`w-4 h-4 transition-all ${
                        selectedTrack?.id === track.id 
                          ? 'text-green-400 opacity-100' 
                          : 'text-gray-500 opacity-0 group-hover:opacity-100 group-hover:text-green-400'
                      }`}
                      fill="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                    </svg>
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
                  </div>
                </li>
              ))
            ) : (
              songs.map((song, index) => (
                <li
                  key={index}
                  className="flex items-center gap-4 p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors group"
                >
                  <span className="text-purple-400 font-bold text-2xl w-12 text-center group-hover:text-purple-300 transition-colors">{index + 1}</span>
                  <span className="text-white text-lg flex-grow group-hover:text-purple-100 transition-colors">{song}</span>
                </li>
              ))
            )}
          </ul>
        </div>
        
        {/* Spotify Embed Player */}
        <div className="lg:sticky lg:top-6 h-fit">
          <h2 className="text-2xl font-bold text-white mb-4">Now Playing</h2>
          {selectedTrack ? (
            <div className="bg-gray-800/50 rounded-lg p-4 backdrop-blur-sm">
              <div className="mb-4">
                <h3 className="text-xl font-semibold text-purple-300 mb-1">{selectedTrack.name}</h3>
                <p className="text-gray-400 text-sm mb-3">by {artist.name}</p>
                
                {/* Play in Spotify App Button */}
                <button
                  onClick={() => selectedTrack.uri && window.open(selectedTrack.uri, '_blank')}
                  className="w-full mb-3 inline-flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-full transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-green-500"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                  </svg>
                  Play in Spotify App
                </button>
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
      
      {/* Modal for Lyrics Prompt - Appears when user returns from Spotify */}
      {showLyricsPrompt && lastClickedTrack && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={handleDismissPrompt}
        >
          <div 
            className="relative bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-8 border border-purple-500/30 animate-fade-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={handleDismissPrompt}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            {/* Track Info */}
            <div className="mb-6 text-center">
              <div className="mb-4">
                <svg className="w-16 h-16 mx-auto text-green-400 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Now Playing</h3>
              <p className="text-xl font-semibold text-purple-300 mb-1">{lastClickedTrack.name}</p>
              <p className="text-gray-400 text-lg mb-4">{artist.name}</p>
              <p className="text-green-400 text-sm font-medium">🎵 Playing in Spotify</p>
            </div>
            
            {/* Prompt Text */}
            <div className="mb-6 text-center">
              <p className="text-white text-lg font-semibold mb-2">Want to follow along?</p>
              <p className="text-gray-300 text-sm">View live lyrics with real-time translation</p>
            </div>
            
            {/* Action Buttons */}
            <div className="space-y-3">
              {/* View Live Lyrics */}
              <button
                onClick={handleViewLyricsFromPrompt}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold rounded-xl transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 shadow-lg"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                <span>View Live Lyrics</span>
              </button>
              
              {/* Maybe Later */}
              <button
                onClick={handleDismissPrompt}
                className="w-full px-6 py-3 bg-gray-700/50 hover:bg-gray-700 text-gray-300 font-semibold rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-900"
              >
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArtistPage;