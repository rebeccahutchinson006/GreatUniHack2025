import React from 'react';
import './TrackInfo.css';

const TrackInfo = ({ track, playbackButton }) => {
  if (!track) {
    return (
      <div className="track-info">
        <div className="no-track">
          <p>No track is currently playing</p>
          <p className="hint">Start playing a song on Spotify to see lyrics!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="track-info">
      {playbackButton && <div className="playback-control-overlay">{playbackButton}</div>}
      {track.album_art && (
        <img src={track.album_art} alt={track.album_name} className="album-art" />
      )}
      <div className="track-details">
        <h2 className="track-name">{track.track_name}</h2>
        <p className="artist-name">{track.artist_name}</p>
        {track.album_name && (
          <p className="album-name">{track.album_name}</p>
        )}
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${(track.progress_ms / track.duration_ms) * 100}%`,
            }}
          />
        </div>
        <div className="time-info">
          <span>{formatTime(track.progress_ms)}</span>
          <span>{formatTime(track.duration_ms)}</span>
        </div>
      </div>
    </div>
  );
};

const formatTime = (ms) => {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

export default TrackInfo;

