import React, { useState, useCallback, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import Sidebar from "./components/Sidebar";
import TopHeader from "./components/TopHeader";
import SubHeader from "./components/SubHeader";
import ChatArea from "./components/ChatArea";
import Dashboard from "./components/Dashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [serviceStatus, setServiceStatus] = useState({
    connected: false,
    services: { ollama: false, qdrant: false, postgresql: false },
  });
  const [agentStatus, setAgentStatus] = useState({
    connected: false,
    label: "ADK Agent Status",
    detail: "Checking connection...",
  });

  // Fetch service status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${API}/status/`);
        setServiceStatus(res.data);
        setAgentStatus({
          connected: res.data.services.qdrant,
          label: "ADK Agent Status",
          detail: res.data.services.qdrant
            ? "Connected to Spanner Vector Search"
            : "Disconnected from Vector Search",
        });
      } catch (e) {
        console.error("Status check failed:", e);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Fetch chat sessions
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await axios.get(`${API}/sessions/`);
        setChatHistory(
          res.data.map((s) => ({
            id: s.id,
            title: s.title || "Untitled conversation",
            date: new Date(s.updated_at).toLocaleDateString(),
            messageCount: s.message_count,
          }))
        );
      } catch (e) {
        console.error("Failed to fetch sessions:", e);
      }
    };
    fetchSessions();
  }, [sessionId]);

  // Load a session
  const loadSession = useCallback(async (id) => {
    try {
      const res = await axios.get(`${API}/sessions/${id}/`);
      setSessionId(id);
      setMessages(
        res.data.messages.map((m) => ({
          id: m.id,
          type: m.message_type,
          text: m.text,
          timestamp: new Date(m.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            hour12: true,
          }),
          showFeedback: m.message_type === "bot",
          feedback: m.feedback,
          sources: m.sources || [],
          link: m.text.includes("pspd-guardian-help-dev.cbp.dhs.gov")
            ? "https://pspd-guardian-help-dev.cbp.dhs.gov"
            : null,
        }))
      );
      setShowWelcome(false);
      setSidebarOpen(false);
    } catch (e) {
      console.error("Failed to load session:", e);
    }
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue.trim();
    setInputValue("");
    setShowWelcome(false);
    setIsLoading(true);

    // Optimistic user message
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      type: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      }),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await axios.post(`${API}/chat/`, {
        message: userText,
        session_id: sessionId || null,
      });

      const { session_id: newSessionId, user_message, bot_message } = res.data;
      setSessionId(newSessionId);

      // Replace temp user msg and add bot msg
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [
          ...filtered,
          {
            id: user_message.id,
            type: "user",
            text: user_message.text,
            timestamp: new Date(user_message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              hour12: true,
            }),
          },
          {
            id: bot_message.id,
            type: "bot",
            text: bot_message.text,
            timestamp: new Date(bot_message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              hour12: true,
            }),
            showFeedback: true,
            feedback: "none",
            sources: bot_message.sources || [],
            link: bot_message.text.includes(
              "pspd-guardian-help-dev.cbp.dhs.gov"
            )
              ? "https://pspd-guardian-help-dev.cbp.dhs.gov"
              : null,
          },
        ];
      });
    } catch (e) {
      console.error("Chat error:", e);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          type: "bot",
          text: "Sorry, I encountered an error processing your request. Please try again.",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            hour12: true,
          }),
          showFeedback: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, sessionId, isLoading]);

  const handleFeedback = useCallback(async (messageId, feedback) => {
    try {
      await axios.patch(`${API}/messages/${messageId}/feedback/`, {
        feedback,
      });
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, feedback } : m))
      );
    } catch (e) {
      console.error("Feedback error:", e);
    }
  }, []);

  const handleClearChat = useCallback(async () => {
    if (sessionId) {
      try {
        await axios.delete(`${API}/sessions/${sessionId}/clear/`);
      } catch (e) {
        console.error("Clear chat error:", e);
      }
    }
    setMessages([]);
    setShowWelcome(true);
    setSessionId(null);
  }, [sessionId]);

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setShowWelcome(true);
    setSessionId(null);
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  return (
    <div className="chat-app-container">
      <Sidebar
        chatHistory={chatHistory}
        agentStatus={agentStatus}
        onNewChat={handleNewChat}
        onSelectChat={loadSession}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />

      <main className="chat-main-area">
        <TopHeader onToggleSidebar={toggleSidebar} />
        <SubHeader
          serviceAuth={{
            authenticated: true,
            label: "Service Account Authentication",
          }}
          connectionStatus={{
            connected: serviceStatus.connected,
            label: serviceStatus.connected ? "Connected" : "Disconnected",
          }}
          onClearChat={handleClearChat}
        />
        <ChatArea
          messages={messages}
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSendMessage={handleSendMessage}
          onFeedback={handleFeedback}
          showWelcome={showWelcome}
          isLoading={isLoading}
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
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
