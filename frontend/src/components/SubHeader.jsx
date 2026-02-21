import React from 'react';
import { CheckCircle, RotateCcw } from 'lucide-react';

const SubHeader = ({ serviceAuth, connectionStatus, onClearChat }) => {
  return (
    <div>
      {/* Service Account Authentication */}
      <div
        className="px-4 py-1.5 flex items-center gap-2 border-b border-[#d7d7d7]/10"
        style={{ backgroundColor: 'rgba(104, 147, 255, 0.08)' }}
      >
        <div className="w-4 h-4 rounded flex items-center justify-center bg-[#00AAAA]/20">
          <CheckCircle size={12} className="text-[#00AAAA]" />
        </div>
        <span className="text-[#6893ff] text-xs">{serviceAuth.label}</span>
      </div>

      {/* Guardian Support Chat Bar */}
      <div
        className="px-4 py-3 flex items-center justify-between border-b border-[#d7d7d7]/10"
        style={{ backgroundColor: '#0f1d35' }}
      >
        <div>
          <h2 className="text-white text-base font-bold leading-tight">Guardian Support Chat</h2>
          <p className="text-white/60 text-xs mt-0.5">Ask questions about Guardian incidents and solutions</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Clear Chat Button */}
          <button
            onClick={onClearChat}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-white text-xs font-medium transition-all hover:opacity-90 active:scale-95"
            style={{
              background: 'linear-gradient(180deg, #1d2d49 0%, #0a387b 100%)',
            }}
          >
            <RotateCcw size={14} />
            Clear Chat
          </button>

          {/* Connected Badge */}
          <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-xs font-medium">
            <div className="w-3.5 h-3.5 rounded-full border-2 border-[#00AAAA] flex items-center justify-center">
              <CheckCircle size={10} className="text-[#00AAAA]" />
            </div>
            <span className="text-[#0a387b]">Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubHeader;
