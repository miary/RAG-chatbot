import React from 'react';
import { Settings, User, Menu } from 'lucide-react';

const TopHeader = ({ onToggleSidebar }) => {
  return (
    <header
      className="flex items-center justify-between px-4 h-[58px] min-h-[58px] border-b border-[#d7d7d7]/20"
      style={{
        background: 'linear-gradient(180deg, #0c1a32 0%, #0a387b 100%)',
      }}
    >
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={onToggleSidebar}
          className="lg:hidden text-white hover:text-[#6893ff] transition-colors"
        >
          <Menu size={22} />
        </button>

        {/* Robot Icon */}
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-[#6893ff]"
          style={{
            background: 'linear-gradient(180deg, #6893ff 0%, #0c1a32 100%)',
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
          PSPD Guardian
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button className="text-white/80 hover:text-white transition-colors">
          <Settings size={22} />
        </button>
        <button className="text-white/80 hover:text-white transition-colors">
          <User size={22} />
        </button>
      </div>
    </header>
  );
};

export default TopHeader;
