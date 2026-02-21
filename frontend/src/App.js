import React, { useState, useCallback } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import TopHeader from "./components/TopHeader";
import SubHeader from "./components/SubHeader";
import ChatArea from "./components/ChatArea";
import {
  mockChatMessages,
  mockChatHistory,
  mockAgentStatus,
  mockConnectionStatus,
  mockServiceAuth,
} from "./data/mockData";

const ChatApp = () => {
  const [messages, setMessages] = useState(mockChatMessages);
  const [chatHistory, setChatHistory] = useState(mockChatHistory);
  const [inputValue, setInputValue] = useState("");
  const [showWelcome, setShowWelcome] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSendMessage = useCallback(() => {
    if (!inputValue.trim()) return;

    const newUserMsg = {
      id: Date.now(),
      type: "user",
      text: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      }),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue("");
    setShowWelcome(false);

    // Simulate bot response
    setTimeout(() => {
      const botReply = {
        id: Date.now() + 1,
        type: "bot",
        text: "Thank you for your question. I'm looking into Guardian incidents related to your query. Please allow me a moment to search our historical data for the best solution.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        }),
        showFeedback: true,
      };
      setMessages((prev) => [...prev, botReply]);
    }, 1200);
  }, [inputValue]);

  const handleClearChat = useCallback(() => {
    setMessages([]);
    setShowWelcome(true);
  }, []);

  const handleNewChat = useCallback(() => {
    if (messages.length > 0) {
      setChatHistory((prev) => [
        {
          title: messages[0]?.text || "New conversation",
          date: new Date().toLocaleDateString(),
        },
        ...prev,
      ]);
    }
    setMessages([]);
    setShowWelcome(true);
  }, [messages]);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  return (
    <div className="chat-app-container">
      <Sidebar
        chatHistory={chatHistory}
        agentStatus={mockAgentStatus}
        onNewChat={handleNewChat}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />

      <main className="chat-main-area">
        <TopHeader onToggleSidebar={toggleSidebar} />
        <SubHeader
          serviceAuth={mockServiceAuth}
          connectionStatus={mockConnectionStatus}
          onClearChat={handleClearChat}
        />
        <ChatArea
          messages={messages}
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSendMessage={handleSendMessage}
          showWelcome={showWelcome}
        />
      </main>

      {/* Floating chatbot icon */}
      <div className="chatbot-fab">
        <div className="chatbot-fab-inner">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <rect
              x="4"
              y="8"
              width="16"
              height="12"
              rx="3"
              stroke="white"
              strokeWidth="1.5"
            />
            <circle cx="9" cy="14" r="1.5" fill="white" />
            <circle cx="15" cy="14" r="1.5" fill="white" />
            <path
              d="M12 4V8"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <circle cx="12" cy="3" r="1.5" stroke="white" strokeWidth="1" />
            <path
              d="M2 13H4"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <path
              d="M20 13H22"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="chatbot-fab-dot" />
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChatApp />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
