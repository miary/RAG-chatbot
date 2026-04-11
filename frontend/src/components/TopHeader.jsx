import React from 'react';
import { Settings, User, Menu, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

const TopHeader = ({ onToggleSidebar }) => {
  return (
    <header
      className="flex items-center justify-between px-4 h-[58px] min-h-[58px] border-b border-[#d7d7d7]/20"
      style={{
        background: 'linear-gradient(180deg, #0c1a32 0%, #0a387b 100%)',
      }}
      role="banner"
    >
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={onToggleSidebar}
          className="lg:hidden text-white hover:text-[#6893ff] transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0c1a32] rounded p-1"
          aria-label="Toggle navigation menu"
          aria-expanded="false"
        >
          <Menu size={22} aria-hidden="true" />
        </button>

        {/* Logo/Brand */}
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-[#6893ff]"
          style={{
            background: 'linear-gradient(180deg, #6893ff 0%, #0c1a32 100%)',
          }}
          role="img"
          aria-label="CBP Training Assistant logo"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="4" y="8" width="16" height="12" rx="3" stroke="white" strokeWidth="1.5" />
            <circle cx="9" cy="14" r="1.5" fill="white" />
            <circle cx="15" cy="14" r="1.5" fill="white" />
            <path d="M12 4V8" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            <circle cx="12" cy="3" r="1.5" stroke="white" strokeWidth="1" />
            <path d="M2 13H4" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            <path d="M20 13H22" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>

        <span className="text-white text-base font-semibold tracking-wide">
          CBP Training Assistant
        </span>
      </div>

      <nav className="flex items-center gap-3" aria-label="Main navigation">
        <Link 
          to="/dashboard" 
          className="text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0c1a32] rounded p-1"
          title="Analytics Dashboard"
          aria-label="Go to Analytics Dashboard"
          data-testid="dashboard-link"
        >
          <BarChart3 size={22} aria-hidden="true" />
        </Link>
        <button 
          className="text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0c1a32] rounded p-1"
          aria-label="Settings"
          title="Settings"
        >
          <Settings size={22} aria-hidden="true" />
        </button>
        <button 
          className="text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0c1a32] rounded p-1"
          aria-label="User profile"
          title="User profile"
        >
          <User size={22} aria-hidden="true" />
        </button>
      </nav>
    </header>
  );
};

export default TopHeader;
