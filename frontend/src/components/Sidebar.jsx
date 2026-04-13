import React, { useState, useCallback } from 'react';
import { Plus, MessageSquare, X, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Sidebar = ({ chatHistory, connectionStatus, onNewChat, onSelectChat, isOpen, onToggle }) => {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const handleChatClick = useCallback(async (chat) => {
    setPreviewLoading(true);
    setPreviewOpen(true);
    setPreviewData(null);

    try {
      const res = await fetch(`${API}/sessions/${chat.id}/`);
      const session = await res.json();

      // Pair user questions with bot responses
      const pairs = [];
      const msgs = session.messages || [];
      for (let i = 0; i < msgs.length; i++) {
        if (msgs[i].message_type === 'user') {
          const botMsg = msgs[i + 1]?.message_type === 'bot' ? msgs[i + 1] : null;
          pairs.push({ question: msgs[i].text, answer: botMsg?.text || '(No response yet)' });
        }
      }

      setPreviewData({
        title: chat.title,
        date: chat.date,
        pairs,
        sessionId: chat.id,
      });
    } catch (e) {
      console.error('Failed to load session preview:', e);
      setPreviewData({ title: chat.title, date: chat.date, pairs: [], error: true });
    } finally {
      setPreviewLoading(false);
    }
  }, []);

  const handleOpenFullChat = useCallback(() => {
    if (previewData?.sessionId && onSelectChat) {
      setPreviewOpen(false);
      onSelectChat(previewData.sessionId);
    }
  }, [previewData, onSelectChat]);

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
            data-testid="new-chat-btn"
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
                    onClick={() => handleChatClick(chat)}
                    className="w-full text-left p-2.5 rounded-lg hover:bg-[#1c2e4c] cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-inset"
                    aria-label={`Preview chat: ${chat.title}, from ${chat.date}`}
                    data-testid={`chat-history-item-${index}`}
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

      {/* Chat Preview Dialog */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent
          className="max-w-lg max-h-[80vh] flex flex-col"
          style={{ backgroundColor: '#0f1d35', border: '1px solid #2a3a5c', color: '#fff' }}
          data-testid="chat-preview-dialog"
        >
          <DialogHeader>
            <DialogTitle className="text-white text-base font-semibold pr-6">
              {previewData?.title || 'Chat Preview'}
            </DialogTitle>
            <DialogDescription className="text-[#BCCBF2] text-xs">
              {previewData?.date || ''}
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto mt-3 space-y-4 pr-1" data-testid="chat-preview-messages">
            {previewLoading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 size={24} className="animate-spin text-[#6893ff]" />
                <span className="ml-2 text-[#BCCBF2] text-sm">Loading messages...</span>
              </div>
            ) : previewData?.error ? (
              <p className="text-red-400 text-sm text-center py-6">Failed to load chat messages.</p>
            ) : previewData?.pairs?.length === 0 ? (
              <p className="text-[#BCCBF2] text-sm text-center py-6">No messages in this chat.</p>
            ) : (
              previewData?.pairs?.map((pair, i) => (
                <div key={i} className="space-y-2">
                  {/* Question */}
                  <div className="flex items-start gap-2">
                    <span className="text-[10px] font-bold text-[#6893ff] uppercase tracking-wider mt-0.5 flex-shrink-0">Q:</span>
                    <p className="text-white text-sm leading-relaxed">{pair.question}</p>
                  </div>
                  {/* Answer */}
                  <div className="flex items-start gap-2 pl-1">
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mt-0.5 flex-shrink-0">A:</span>
                    <p className="text-[#d0d8e8] text-sm leading-relaxed whitespace-pre-wrap">{pair.answer}</p>
                  </div>
                  {i < previewData.pairs.length - 1 && (
                    <hr className="border-[#2a3a5c] mt-2" />
                  )}
                </div>
              ))
            )}
          </div>

          {/* Open full chat button */}
          {previewData?.sessionId && !previewLoading && (
            <div className="pt-3 border-t border-[#2a3a5c] mt-2">
              <button
                onClick={handleOpenFullChat}
                className="w-full py-2 rounded-lg text-sm font-medium text-white transition-colors hover:opacity-90"
                style={{ background: 'linear-gradient(180deg, #3b6fe0 0%, #0a387b 100%)' }}
                data-testid="open-full-chat-btn"
              >
                Open Full Chat
              </button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default Sidebar;
