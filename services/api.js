const API_BASE_URL = 'http://localhost:8000';

export const api = {
  login: () => {
    window.location.href = `${API_BASE_URL}/login`;
  },

  getCurrentlyPlaying: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/currently-playing/${userId}`);
    if (!response.ok) {
      throw new Error('Failed to get currently playing track');
    }
    return response.json();
  },

  getLyrics: async (trackName, artistName) => {
    const encodedTrack = encodeURIComponent(trackName);
    const encodedArtist = encodeURIComponent(artistName);
    const response = await fetch(
      `${API_BASE_URL}/lyrics/${encodedTrack}/${encodedArtist}`
    );
    if (!response.ok) {
      throw new Error('Failed to get lyrics');
    }
    return response.json();
  },

  translateLyrics: async (lyrics, targetLang, sourceLang = null, lines = null) => {
    const response = await fetch(`${API_BASE_URL}/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        lyrics,
        target_lang: targetLang,
        source_lang: sourceLang,
        lines: lines,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to translate lyrics');
    }
    return response.json();
  },

  getSupportedLanguages: async () => {
    const response = await fetch(`${API_BASE_URL}/languages`);
    if (!response.ok) {
      throw new Error('Failed to get supported languages');
    }
    return response.json();
  },

  translateLinesOverlay: async (lyrics, targetLang, sourceLang = null, lines = null) => {
    const response = await fetch(`${API_BASE_URL}/translate-lines`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        lyrics,
        target_lang: targetLang,
        source_lang: sourceLang,
        lines: lines,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to translate lyrics line-by-line');
    }
    return response.json();
  },

  translateWord: async (word, targetLang, sourceLang = null) => {
    const response = await fetch(`${API_BASE_URL}/translate-word`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        word,
        target_lang: targetLang,
        source_lang: sourceLang,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to translate word');
    }
    return response.json();
  },

  analyzeLyrics: async (lyrics) => {
    const response = await fetch(`${API_BASE_URL}/analyze-lyrics`, {
  play: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/play/${userId}`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to resume playback');
    }
    return response.json();
  },

  pause: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/pause/${userId}`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to pause playback');
    }
    return response.json();
  },

  textToSpeech: async (text, language = 'en') => {
    const response = await fetch(`${API_BASE_URL}/text-to-speech`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        lyrics
        text,
        language,
        speed: 1.0,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze lyrics');
    }
    return response.json();
  },
};

