import React from 'react';
import { RotateCcw } from 'lucide-react';

const SubHeader = ({ onClearChat }) => {
  return (
    <div 
      className="px-4 py-2 flex items-center justify-end border-b border-[#d7d7d7]/10"
      style={{ backgroundColor: '#0f1d35' }}
      role="toolbar"
      aria-label="Chat controls"
    >
      {/* Clear Chat Button */}
      <button
        onClick={onClearChat}
        className="flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-white text-xs font-medium transition-all hover:opacity-90 active:scale-95 whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0f1d35]"
        style={{
          background: 'linear-gradient(180deg, #1d2d49 0%, #0a387b 100%)',
        }}
        aria-label="Clear current chat"
        title="Clear current chat"
      >
        <RotateCcw size={14} aria-hidden="true" />
        <span>Clear Chat</span>
      </button>
    </div>
  );
};

export default SubHeader;
