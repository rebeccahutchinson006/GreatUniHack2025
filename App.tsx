import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MusicDataProvider } from './context/MusicDataContext';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import GenrePage from './pages/GenrePage';
import ArtistDetailPage from './pages/ArtistDetailPage';
import LyricsShow from './pages/LyricsShow';

function App() {
  return (
    <BrowserRouter>
      <MusicDataProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="genre/:country" element={<GenrePage />} />
            <Route path="genre/:country/artist/:artistId" element={<ArtistDetailPage />} />
            <Route path="lyrics" element={<LyricsShow />} />
          </Route>
        </Routes>
      </MusicDataProvider>
    </BrowserRouter>
  );
}

export default App;
