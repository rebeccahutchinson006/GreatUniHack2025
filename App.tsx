
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MusicSection from './components/MusicSection';
import Footer from './components/Footer';
import CountryPage from './components/CountryPage';
import { MUSIC_SECTIONS } from './constants';
import { MusicSectionData } from './types';

function App() {
  const [activeCountry, setActiveCountry] = useState<string | null>(null);
  const [musicData, setMusicData] = useState<MusicSectionData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMusicData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/music');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setMusicData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching music data:', err);
        setError('Failed to load music data. Using fallback data.');
        // Use hardcoded data as fallback
        setMusicData(MUSIC_SECTIONS);
      } finally {
        setLoading(false);
      }
    };

    fetchMusicData();
  }, []);

  const handleSelectCountry = (country: string) => {
    setActiveCountry(country);
  };

  const handleGoBack = () => {
    setActiveCountry(null);
  };

  const activeSectionData = musicData.find(section => section.country === activeCountry);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-900 via-purple-900/20 to-gray-900">
        <Header />
        <div className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p className="text-white text-xl">Loading music data...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-900 via-purple-900/20 to-gray-900">
      <Header />
      <div className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-yellow-500/20 border border-yellow-500 rounded-lg text-yellow-200">
            {error}
          </div>
        )}
        {activeCountry && activeSectionData ? (
          <CountryPage section={activeSectionData} onBack={handleGoBack} />
        ) : (
          <div className="space-y-12">
            {musicData.map((section) => (
              <MusicSection
                key={section.country}
                section={section}
                onTitleClick={() => handleSelectCountry(section.country)}
              />
            ))}
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}

export default App;
