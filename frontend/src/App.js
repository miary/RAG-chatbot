import React, { useState, useCallback, useEffect, useRef } from "react";
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
const WS_URL = BACKEND_URL.replace(/^http/, 'ws');

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const [streamStatus, setStreamStatus] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
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

  // WebSocket connection management
  const connectWebSocket = useCallback((sid) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }

    const wsUrl = `${WS_URL}/ws/chat/${sid || 'new'}/`;
    console.log('Connecting WebSocket to:', wsUrl);
    
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code);
      setWsConnected(false);
      wsRef.current = null;
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    wsRef.current = ws;
  }, []);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'connection_established':
        console.log('WS connection established, session:', data.session_id);
        if (data.session_id && data.session_id !== 'new') {
          setSessionId(data.session_id);
        }
        break;

      case 'user_message_saved':
        // Update temp user message with real ID
        setMessages((prev) => prev.map((m) => 
          m.id.startsWith('temp-') && m.type === 'user'
            ? { ...m, id: data.message.id }
            : m
        ));
        break;

      case 'status':
        setStreamStatus(data.message);
        break;

      case 'rag_complete':
        console.log('RAG complete, sources:', data.sources?.length);
        break;

      case 'stream_start':
        setStreamingMessageId(data.message_id);
        setIsStreaming(true);
        // Add streaming bot message placeholder
        setMessages((prev) => [
          ...prev,
          {
            id: data.message_id,
            type: 'bot',
            text: '',
            timestamp: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              hour12: true,
            }),
            showFeedback: false,
            isStreaming: true,
          },
        ]);
        break;

      case 'stream_chunk':
        // Append chunk to streaming message
        setMessages((prev) => prev.map((m) =>
          m.id === data.message_id
            ? { ...m, text: m.text + data.chunk }
            : m
        ));
        break;

      case 'stream_complete':
        setIsStreaming(false);
        setIsLoading(false);
        setStreamingMessageId(null);
        setStreamStatus(null);
        // Update message with final data
        setMessages((prev) => prev.map((m) =>
          m.id === streamingMessageId || m.id === data.message_id
            ? {
                ...m,
                id: data.message.id,
                text: data.message.text,
                timestamp: new Date(data.message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: true,
                }),
                sources: data.message.sources || [],
                showFeedback: true,
                isStreaming: false,
                rating: null,
              }
            : m
        ));
        // Refresh session list
        break;

      case 'error':
        console.error('WebSocket error:', data.message);
        setIsLoading(false);
        setIsStreaming(false);
        setStreamStatus(null);
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            type: 'bot',
            text: `Error: ${data.message}. Please try again.`,
            timestamp: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              hour12: true,
            }),
            showFeedback: false,
          },
        ]);
        break;

      default:
        console.log('Unknown WS message type:', data.type);
    }
  }, [streamingMessageId]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

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
          rating: m.rating,
          sources: m.sources || [],
          link: m.text.includes("pspd-guardian-help-dev.cbp.dhs.gov")
            ? "https://pspd-guardian-help-dev.cbp.dhs.gov"
            : null,
        }))
      );
      setShowWelcome(false);
      setSidebarOpen(false);
      // Connect WebSocket for this session
      connectWebSocket(id);
    } catch (e) {
      console.error("Failed to load session:", e);
    }
  }, [connectWebSocket]);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || isLoading || isStreaming) return;

    const userText = inputValue.trim();
    setInputValue("");
    setShowWelcome(false);
    setIsLoading(true);
    setStreamStatus("Connecting...");

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

    // Try WebSocket streaming first
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        message: userText,
      }));
      return;
    }

    // Connect WebSocket if not connected
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      const wsUrl = `${WS_URL}/ws/chat/${sessionId || 'new'}/`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setWsConnected(true);
        ws.send(JSON.stringify({
          type: 'chat_message',
          message: userText,
        }));
      };

      ws.onclose = () => {
        setWsConnected(false);
        wsRef.current = null;
      };

      ws.onerror = async () => {
        // Fallback to REST API if WebSocket fails
        console.log('WebSocket failed, falling back to REST API');
        try {
          const res = await axios.post(`${API}/chat/`, {
            message: userText,
            session_id: sessionId || null,
          });

          const { session_id: newSessionId, user_message, bot_message } = res.data;
          setSessionId(newSessionId);

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
                rating: null,
                sources: bot_message.sources || [],
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
              text: "Sorry, I encountered an error. Please try again.",
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
          setStreamStatus(null);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      };

      wsRef.current = ws;
    }
  }, [inputValue, sessionId, isLoading, isStreaming, handleWebSocketMessage]);

  const handleFeedback = useCallback(async (messageId, rating) => {
    try {
      await axios.patch(`${API}/messages/${messageId}/feedback/`, {
        rating,
      });
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, rating } : m))
      );
    } catch (e) {
      console.error("Rating error:", e);
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
          isStreaming={isStreaming}
          streamStatus={streamStatus}
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
