import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';

const Sidebar = ({ chatHistory, connectionStatus, onNewChat, onSelectChat, isOpen, onToggle }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onToggle}
          role="presentation"
          aria-hidden="true"
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
        role="complementary"
        aria-label="Chat history sidebar"
      >
        {/* Chat History Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a3a5c]">
          <span className="text-white text-sm font-semibold tracking-wide" id="chat-history-label">
            Chat History
          </span>
          <button
            onClick={onNewChat}
            className="text-white hover:text-[#6893ff] transition-colors w-6 h-6 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0a1628] rounded"
            aria-label="Start new chat"
            title="Start new chat"
          >
            <Plus size={18} aria-hidden="true" />
          </button>
        </div>

        {/* Chat History List / Empty State */}
        <nav 
          className="flex-1 flex flex-col px-2 py-2 overflow-y-auto"
          aria-labelledby="chat-history-label"
          role="navigation"
        >
          {chatHistory.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center px-2" role="status">
              <MessageSquare size={48} className="text-[#2a3a5c] mx-auto mb-3" aria-hidden="true" />
              <p className="text-[#BCCBF2] text-sm font-bold mb-1">No chat history yet</p>
              <p className="text-white text-xs opacity-80">Start a new conversation</p>
            </div>
          ) : (
            <ul className="w-full space-y-1 list-none p-0 m-0" role="list">
              {chatHistory.map((chat, index) => (
                <li key={chat.id || index}>
                  <button
                    onClick={() => onSelectChat && onSelectChat(chat.id)}
                    className="w-full text-left p-2.5 rounded-lg hover:bg-[#1c2e4c] cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-inset"
                    aria-label={`Open chat: ${chat.title}, from ${chat.date}`}
                  >
                    <p className="text-white text-xs truncate">{chat.title}</p>
                    <p className="text-[#BCCBF2] text-[10px] mt-0.5">{chat.date}</p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </nav>

        {/* Connection Status */}
        <div className="px-4 py-3 pb-6 border-t border-[#2a3a5c]">
          <div 
            className="flex items-center gap-2 px-3 py-2 rounded-full border border-[#2a3a5c] bg-[#0f1d35] w-fit" 
            role="status" 
            aria-live="polite"
          >
            <div
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: connectionStatus?.connected ? '#00AAAA' : '#ff4444' }}
              aria-hidden="true"
            />
            <span className="text-white text-xs font-medium">
              {connectionStatus?.connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
