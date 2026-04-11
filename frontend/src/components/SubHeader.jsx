import React from 'react';
import { CheckCircle, RotateCcw } from 'lucide-react';

const SubHeader = ({ serviceAuth, connectionStatus, onClearChat }) => {
  return (
    <div role="banner">
      {/* Service Account Authentication */}
      <div
        className="px-4 py-1.5 flex items-center gap-2 border-b border-[#d7d7d7]/10"
        style={{ backgroundColor: 'rgba(104, 147, 255, 0.08)' }}
        role="status"
        aria-label="Authentication status"
      >
        <div className="w-4 h-4 rounded flex items-center justify-center bg-[#00AAAA]/20" aria-hidden="true">
          <CheckCircle size={12} className="text-[#00AAAA]" />
        </div>
        <span className="text-[#6893ff] text-xs">{serviceAuth.label}</span>
      </div>

      {/* CBP Training Chat Bar */}
      <div
        className="px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#d7d7d7]/10"
        style={{ backgroundColor: '#0f1d35' }}
      >
        <div className="min-w-0">
          <h1 className="text-white text-base font-bold leading-tight">CBP Training Assistant</h1>
          <p className="text-white/60 text-xs mt-0.5">Your guide to CBP policies, procedures, and best practices</p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
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
      </div>
    </div>
  );
};

export default SubHeader;
