
import React, { useState } from 'react';
import Header from './components/Header';
import MusicSection from './components/MusicSection';
import Footer from './components/Footer';
import CountryPage from './components/CountryPage';
import { MUSIC_SECTIONS } from './constants';
import { MusicSectionData } from './types';

function App() {
  const [activeCountry, setActiveCountry] = useState<string | null>(null);

  const handleSelectCountry = (country: string) => {
    setActiveCountry(country);
  };

  const handleGoBack = () => {
    setActiveCountry(null);
  };

  const activeSectionData = MUSIC_SECTIONS.find(section => section.country === activeCountry);

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-900 via-purple-900/20 to-gray-900">
      <Header />
      <div className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeCountry && activeSectionData ? (
          <CountryPage section={activeSectionData} onBack={handleGoBack} />
        ) : (
          <div className="space-y-12">
            {MUSIC_SECTIONS.map((section) => (
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
