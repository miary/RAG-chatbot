import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';

const Sidebar = ({ chatHistory, agentStatus, onNewChat, isOpen, onToggle }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      <aside
        className={`
          fixed lg:relative z-50 lg:z-auto
          h-full w-[220px] min-w-[220px]
          flex flex-col
          border-r border-[#2a3a5c]
          transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        style={{ backgroundColor: '#0a1628' }}
      >
        {/* Chat History Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a3a5c]">
          <span className="text-white text-sm font-semibold tracking-wide">Chat History</span>
          <button
            onClick={onNewChat}
            className="text-white hover:text-[#6893ff] transition-colors w-6 h-6 flex items-center justify-center"
          >
            <Plus size={18} />
          </button>
        </div>

        {/* Chat History List / Empty State */}
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          {chatHistory.length === 0 ? (
            <div className="text-center">
              <MessageSquare size={48} className="text-[#2a3a5c] mx-auto mb-3" />
              <p className="text-[#BCCBF2] text-sm font-bold mb-1">No chat history yet</p>
              <p className="text-white text-xs opacity-80">Start a new conversation</p>
            </div>
          ) : (
            <div className="w-full space-y-2 overflow-y-auto">
              {chatHistory.map((chat, index) => (
                <div
                  key={index}
                  className="p-2 rounded-lg hover:bg-[#1c2e4c] cursor-pointer transition-colors"
                >
                  <p className="text-white text-xs truncate">{chat.title}</p>
                  <p className="text-[#BCCBF2] text-[10px] mt-0.5">{chat.date}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ADK Agent Status */}
        <div className="px-4 py-3 border-t border-[#2a3a5c]">
          <div className="flex items-start gap-2">
            <div className="mt-1">
              <div
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: agentStatus.connected ? '#00AAAA' : '#ff4444' }}
              />
            </div>
            <div>
              <p className="text-white text-xs font-bold">{agentStatus.label}</p>
              <p className="text-white text-[10px] opacity-70">{agentStatus.detail}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
