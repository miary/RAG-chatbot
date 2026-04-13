import React, { useState } from 'react';
import { Plus, MessageSquare, Settings2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';
import { FormatText } from './ChatArea';

const LIMIT_OPTIONS = [10, 20, 30, 50, 100];

const Sidebar = ({
  chatHistory,
  connectionStatus,
  onNewChat,
  isOpen,
  onToggle,
  historyLimit,
  onHistoryLimitChange,
}) => {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewItem, setPreviewItem] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const handleChatClick = (item) => {
    setPreviewItem(item);
    setPreviewOpen(true);
  };

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
          h-full w-[240px] min-w-[240px]
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
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a3a5c]">
          <span className="text-white text-sm font-semibold tracking-wide" id="chat-history-label">
            Chat History
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowSettings((s) => !s)}
              className="text-white/60 hover:text-[#6893ff] transition-colors w-6 h-6 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0a1628] rounded"
              aria-label="Chat history settings"
              title="Settings"
              data-testid="history-settings-btn"
            >
              <Settings2 size={15} aria-hidden="true" />
            </button>
            <button
              onClick={onNewChat}
              className="text-white hover:text-[#6893ff] transition-colors w-6 h-6 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2 focus:ring-offset-[#0a1628] rounded"
              aria-label="Start new chat"
              title="Start new chat"
              data-testid="new-chat-btn"
            >
              <Plus size={18} aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* Settings dropdown */}
        {showSettings && (
          <div className="px-3 py-2 border-b border-[#2a3a5c] bg-[#0d1526]" data-testid="history-settings-panel">
            <label className="text-[#BCCBF2] text-[11px] block mb-1">
              Show last
            </label>
            <div className="flex items-center gap-2">
              <select
                value={historyLimit}
                onChange={(e) => onHistoryLimitChange(parseInt(e.target.value, 10))}
                className="flex-1 bg-[#1c2e4c] text-white text-xs rounded px-2 py-1.5 border border-[#2a3a5c] focus:outline-none focus:border-[#6893ff]"
                data-testid="history-limit-select"
                aria-label="Number of conversations to display"
              >
                {LIMIT_OPTIONS.map((n) => (
                  <option key={n} value={n}>
                    {n} conversations
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Chat History List */}
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
              {chatHistory.map((item, index) => (
                <li key={item.id || index}>
                  <button
                    onClick={() => handleChatClick(item)}
                    className="w-full text-left p-2.5 rounded-lg hover:bg-[#1c2e4c] cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-inset group"
                    aria-label={`View answer for: ${item.title}`}
                    data-testid={`chat-history-item-${index}`}
                  >
                    <p className="text-white text-xs truncate group-hover:text-[#6893ff] transition-colors">
                      {item.title}
                    </p>
                    <p className="text-[#BCCBF2] text-[10px] mt-0.5">{item.date}</p>
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
            data-testid="connection-status"
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

      {/* Q&A Preview Dialog */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent
          className="max-w-lg max-h-[80vh] flex flex-col"
          style={{ backgroundColor: '#0f1d35', border: '1px solid #2a3a5c', color: '#fff' }}
          data-testid="chat-preview-dialog"
        >
          <DialogHeader>
            <DialogTitle className="text-white text-base font-semibold pr-6">
              Conversation
            </DialogTitle>
            <DialogDescription className="text-[#BCCBF2] text-xs">
              {previewItem?.date || ''}
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto mt-3 space-y-4 pr-1" data-testid="chat-preview-messages">
            {previewItem && (
              <div className="space-y-3">
                {/* Question */}
                <div className="flex items-start gap-2">
                  <span className="text-[10px] font-bold text-[#6893ff] uppercase tracking-wider mt-0.5 flex-shrink-0">Q:</span>
                  <p className="text-white text-sm leading-relaxed">{previewItem.title}</p>
                </div>
                {/* Answer */}
                <div className="flex items-start gap-2 pl-1">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mt-0.5 flex-shrink-0">A:</span>
                  <div className="text-[#d0d8e8] text-sm leading-relaxed">
                    {previewItem.answer
                      ? <FormatText text={previewItem.answer} />
                      : '(No response yet)'}
                  </div>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default Sidebar;
