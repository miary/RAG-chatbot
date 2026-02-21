import React, { useRef, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, Send } from 'lucide-react';

/* ── Robot Icon (used for bot avatar) ── */
const BotAvatar = ({ size = 43 }) => (
  <div
    className="rounded-full flex items-center justify-center border-2 border-[#6893ff] flex-shrink-0"
    style={{
      width: size,
      height: size,
      background: 'linear-gradient(180deg, #6893ff 0%, #0c1a32 100%)',
    }}
  >
    <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 24 24" fill="none">
      <rect x="4" y="8" width="16" height="12" rx="3" stroke="white" strokeWidth="1.5" />
      <circle cx="9" cy="14" r="1.5" fill="white" />
      <circle cx="15" cy="14" r="1.5" fill="white" />
      <path d="M12 4V8" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="12" cy="3" r="1.5" stroke="white" strokeWidth="1" />
      <path d="M2 13H4" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M20 13H22" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  </div>
);

const UserAvatar = ({ size = 43 }) => (
  <div
    className="rounded-full flex items-center justify-center flex-shrink-0"
    style={{
      width: size,
      height: size,
      background: 'linear-gradient(180deg, #6893ff 0%, #0c1a32 100%)',
      border: '2px solid #6893ff',
    }}
  >
    <svg width={size * 0.45} height={size * 0.45} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="8" r="4" stroke="white" strokeWidth="1.5" />
      <path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  </div>
);

/* ── Welcome State ── */
const WelcomeState = () => (
  <div className="flex-1 flex flex-col items-center justify-center px-4">
    <BotAvatar size={78} />
    <h2 className="text-white text-lg font-semibold mt-4">Welcome to PSPD Guardian</h2>
    <p className="text-white/70 text-sm mt-2 text-center max-w-md leading-relaxed">
      I can help you find solutions to Guardian incidents based on historical data.&nbsp;
      Ask me about technical issues, error messages, or troubleshooting steps.
    </p>
  </div>
);

/* ── Bot Message ── */
const BotMessage = ({ message }) => (
  <div className="flex items-start gap-3 max-w-[85%]">
    <BotAvatar size={43} />
    <div>
      <div className="rounded-xl px-4 py-3 bg-white text-[#1a1a2e] text-sm leading-relaxed">
        {message.link ? (
          <>
            <span>User guides can be found at </span>
            <a
              href={message.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#0a387b] underline hover:text-[#6893ff] transition-colors"
            >
              {message.link.replace('https://', '')}
            </a>
          </>
        ) : (
          message.text
        )}

        {message.showFeedback && (
          <>
            <div className="border-t border-gray-200 mt-3 pt-2 flex items-center gap-3">
              <span className="text-xs text-gray-500">Was this helpful?</span>
              <button className="text-[#1c2e4c] hover:text-[#6893ff] transition-colors">
                <ThumbsUp size={16} />
              </button>
              <button className="text-[#1c2e4c] hover:text-[#6893ff] transition-colors">
                <ThumbsDown size={16} />
              </button>
            </div>
          </>
        )}
      </div>
      <span className="text-white/40 text-[11px] mt-1 block">{message.timestamp}</span>
    </div>
  </div>
);

/* ── User Message ── */
const UserMessage = ({ message }) => (
  <div className="flex items-start gap-3 justify-end">
    <div className="text-right">
      <div
        className="inline-block rounded-xl px-4 py-3 text-white text-sm leading-relaxed"
        style={{ backgroundColor: '#3b6fe0' }}
      >
        {message.text}
      </div>
      <span className="text-white/40 text-[11px] mt-1 block">{message.timestamp}</span>
    </div>
    <UserAvatar size={43} />
  </div>
);

/* ── Main Chat Area ── */
const ChatArea = ({ messages, inputValue, onInputChange, onSendMessage, showWelcome }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div className="flex-1 flex flex-col" style={{ backgroundColor: '#111b2e' }}>
      {/* Messages or Welcome */}
      {showWelcome ? (
        <WelcomeState />
      ) : (
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
          {messages.map((msg) =>
            msg.type === 'bot' ? (
              <BotMessage key={msg.id} message={msg} />
            ) : (
              <UserMessage key={msg.id} message={msg} />
            )
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Message Input Bar */}
      <div className="px-4 md:px-8 py-4" style={{ backgroundColor: '#0a1628' }}>
        <div className="relative flex items-center">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What Guardian issue can I help with today?"
            className="w-full rounded-xl py-3 pl-4 pr-14 text-sm text-[#333] placeholder-gray-400 outline-none border-2 border-transparent focus:border-[#6893ff] transition-colors"
            style={{
              backgroundColor: '#ffffff',
            }}
          />
          <button
            onClick={onSendMessage}
            className="absolute right-2 w-[42px] h-[42px] rounded-xl flex items-center justify-center transition-all hover:opacity-90 active:scale-95"
            style={{
              background: 'linear-gradient(180deg, #8080ff 0%, #00429d 100%)',
            }}
          >
            <Send size={18} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;
