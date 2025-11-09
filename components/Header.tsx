
import React from 'react';

interface HeaderProps {
  onLogoClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogoClick }) => {
  return (
    <header className="bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <h1 
            className="text-2xl font-bold tracking-tighter text-white cursor-pointer hover:text-purple-400 transition-colors"
            onClick={onLogoClick}
          >
            <span role="img" aria-label="music notes">🎶</span> Boots and Cats
          </h1>
        </div>
      </div>
    </header>
  );
};

export default Header;
