import React, { useRef, useEffect, useState } from 'react';
import { Star, Send, Loader2 } from 'lucide-react';

/* --- Robot Icon (used for bot avatar) --- */
const BotAvatar = ({ size = 43 }) => (
  <div
    className="rounded-full flex items-center justify-center border-2 border-[#6893ff] flex-shrink-0"
    style={{
      width: size,
      height: size,
      background: 'linear-gradient(180deg, #6893ff 0%, #0c1a32 100%)',
    }}
    role="img"
    aria-label="CBP Training Assistant"
  >
    <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 24 24" fill="none" aria-hidden="true">
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
    role="img"
    aria-label="You"
  >
    <svg width={size * 0.45} height={size * 0.45} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="white" strokeWidth="1.5" />
      <path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  </div>
);

/* --- Star Rating Component --- */
const StarRating = ({ rating, onRate, messageId }) => {
  const [hoverRating, setHoverRating] = useState(0);
  
  return (
    <div className="flex items-center gap-1" role="group" aria-label="Rate this response from 1 to 5 stars">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => onRate && onRate(messageId, star)}
          onMouseEnter={() => setHoverRating(star)}
          onMouseLeave={() => setHoverRating(0)}
          className="transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-offset-1 rounded"
          data-testid={`star-${star}`}
          aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
          aria-pressed={rating >= star}
        >
          <Star
            size={18}
            className={`transition-colors ${
              (hoverRating || rating) >= star
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 hover:text-yellow-300'
            }`}
            aria-hidden="true"
          />
        </button>
      ))}
    </div>
  );
};

/* --- Welcome State --- */
const WelcomeState = () => (
  <div className="flex-1 flex flex-col items-center justify-center px-4" role="status">
    <BotAvatar size={78} />
    <h2 className="text-white text-lg font-semibold mt-4">Welcome to CBP Training Assistant</h2>
    <p className="text-white/70 text-sm mt-2 text-center max-w-md leading-relaxed">
      I'm here to help you learn about CBP policies, procedures, and best practices.&nbsp;
      Ask me about border security, customs regulations, immigration law, or inspection procedures.
    </p>
  </div>
);

/* --- Format bot text with markdown-like bold --- */
const FormatText = ({ text }) => {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        // Handle newlines
        return part.split('\n').map((line, j) => (
          <React.Fragment key={`${i}-${j}`}>
            {j > 0 && <br />}
            {line}
          </React.Fragment>
        ));
      })}
    </>
  );
};

/* --- Bot Message --- */
const BotMessage = ({ message, onFeedback }) => (
  <article className="flex items-start gap-3 max-w-[85%]" aria-label="Assistant response">
    <BotAvatar size={43} />
    <div className="flex-1">
      <div className="rounded-xl px-4 py-3 bg-white text-[#1a1a2e] text-sm leading-relaxed">
        {message.text ? (
          <FormatText text={message.text} />
        ) : message.isStreaming ? (
          <span className="text-gray-400 italic" role="status" aria-live="polite">Generating response...</span>
        ) : null}
        
        {message.isStreaming && (
          <span className="inline-block w-2 h-4 bg-[#6893ff] ml-1 animate-pulse" aria-hidden="true" />
        )}

        {message.showFeedback && !message.isStreaming && (
          <div className="border-t border-gray-200 mt-3 pt-2 flex items-center gap-3">
            <span className="text-xs text-gray-500" id={`rating-label-${message.id}`}>Rate this response:</span>
            <StarRating 
              rating={message.rating} 
              onRate={onFeedback}
              messageId={message.id}
            />
            {message.rating && (
              <span className="text-xs text-gray-400 ml-1" aria-live="polite">
                ({message.rating}/5)
              </span>
            )}
          </div>
        )}
      </div>
      <span className="text-white/40 text-[11px] mt-1 block" aria-label={`Sent at ${message.timestamp}`}>
        {message.timestamp}
      </span>
    </div>
  </article>
);

/* --- User Message --- */
const UserMessage = ({ message }) => (
  <article className="flex items-start gap-3 justify-end" aria-label="Your message">
    <div className="text-right">
      <div
        className="inline-block rounded-xl px-4 py-3 text-white text-sm leading-relaxed"
        style={{ backgroundColor: '#3b6fe0' }}
      >
        {message.text}
      </div>
      <span className="text-white/40 text-[11px] mt-1 block" aria-label={`Sent at ${message.timestamp}`}>
        {message.timestamp}
      </span>
    </div>
    <UserAvatar size={43} />
  </article>
);

/* --- Typing indicator --- */
const TypingIndicator = ({ status }) => (
  <div className="flex items-start gap-3 max-w-[85%]" role="status" aria-live="polite">
    <BotAvatar size={43} />
    <div className="rounded-xl px-4 py-3 bg-white/90 flex items-center gap-2">
      <Loader2 size={16} className="animate-spin text-[#6893ff]" aria-hidden="true" />
      <span className="text-sm text-gray-500">
        {status || "Processing your request..."}
      </span>
    </div>
  </div>
);

/* --- Main Chat Area --- */
const ChatArea = ({
  messages,
  inputValue,
  onInputChange,
  onSendMessage,
  onFeedback,
  showWelcome,
  isLoading,
  isStreaming,
  streamStatus,
}) => {
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, isStreaming]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  // Check if there's already a streaming message in the list
  const hasStreamingMessage = messages.some(m => m.isStreaming);

  return (
    <div className="flex-1 flex flex-col min-h-0" style={{ backgroundColor: '#111b2e' }}>
      {/* Messages or Welcome */}
      {showWelcome ? (
        <WelcomeState />
      ) : (
        <div 
          className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6"
          role="log"
          aria-label="Chat messages"
          aria-live="polite"
        >
          {messages.map((msg) =>
            msg.type === 'bot' ? (
              <BotMessage key={msg.id} message={msg} onFeedback={onFeedback} />
            ) : (
              <UserMessage key={msg.id} message={msg} />
            )
          )}
          {isLoading && !hasStreamingMessage && <TypingIndicator status={streamStatus} />}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Message Input Bar */}
      <div className="px-4 md:px-8 py-4" style={{ backgroundColor: '#0a1628' }}>
        <div className="relative flex items-center">
          <label htmlFor="chat-input" className="sr-only">
            Type your message
          </label>
          <input
            id="chat-input"
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about CBP training, policies, or procedures..."
            disabled={isLoading}
            aria-describedby="input-help"
            className="w-full rounded-xl py-3 pl-4 pr-14 text-sm text-[#333] placeholder-gray-400 outline-none border-2 border-transparent focus:border-[#6893ff] transition-colors disabled:opacity-60"
            style={{
              backgroundColor: '#ffffff',
            }}
          />
          <span id="input-help" className="sr-only">
            Press Enter to send your message
          </span>
          <button
            onClick={onSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="absolute right-2 w-[42px] h-[42px] rounded-xl flex items-center justify-center transition-all hover:opacity-90 active:scale-95 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-[#6893ff] focus:ring-offset-2"
            style={{
              background: 'linear-gradient(180deg, #8080ff 0%, #00429d 100%)',
            }}
            aria-label={isLoading ? "Sending message" : "Send message"}
            title="Send message"
          >
            {isLoading ? (
              <Loader2 size={18} className="text-white animate-spin" aria-hidden="true" />
            ) : (
              <Send size={18} className="text-white" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;
