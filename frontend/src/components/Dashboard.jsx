import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, 
  MessageSquare, 
  Users, 
  Clock, 
  TrendingUp,
  Star,
  Zap,
  Target
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StatCard = ({ title, value, subtitle, icon: Icon, color = "#6893ff" }) => (
  <div className="stat-card" data-testid={`stat-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="stat-card-icon" style={{ backgroundColor: `${color}20`, color }}>
      <Icon size={24} />
    </div>
    <div className="stat-card-content">
      <p className="stat-card-title">{title}</p>
      <p className="stat-card-value">{value}</p>
      {subtitle && <p className="stat-card-subtitle">{subtitle}</p>}
    </div>
  </div>
);

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("usage");
  const [usageData, setUsageData] = useState(null);
  const [ragData, setRagData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [usageRes, ragRes] = await Promise.all([
          axios.get(`${API}/analytics/usage/`),
          axios.get(`${API}/analytics/rag/`),
        ]);
        setUsageData(usageRes.data);
        setRagData(ragRes.data);
      } catch (e) {
        console.error("Failed to fetch analytics:", e);
        setError("Failed to load analytics data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const COLORS = ["#6893ff", "#00AAAA", "#ff6b6b", "#ffd93d"];
  const SCORE_COLORS = {
    excellent: "#00AAAA",
    good: "#6893ff",
    fair: "#ffd93d",
    poor: "#ff6b6b",
  };
  
  const STAR_COLORS = {
    '5_stars': "#00AAAA",
    '4_stars': "#6893ff",
    '3_stars': "#ffd93d",
    '2_stars': "#ff9f43",
    '1_star': "#ff6b6b",
    'no_rating': "#4a5568",
  };

  const formatLatency = (ms) => {
    if (ms >= 60000) return `${(ms / 60000).toFixed(1)}m`;
    if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.round(ms)}ms`;
  };

  const renderUsageTab = () => {
    if (!usageData) return null;

    const { summary, messages_over_time, rating_distribution } = usageData;

    const ratingBarData = [
      { name: "5 Stars", value: rating_distribution['5_stars'], fill: STAR_COLORS['5_stars'] },
      { name: "4 Stars", value: rating_distribution['4_stars'], fill: STAR_COLORS['4_stars'] },
      { name: "3 Stars", value: rating_distribution['3_stars'], fill: STAR_COLORS['3_stars'] },
      { name: "2 Stars", value: rating_distribution['2_stars'], fill: STAR_COLORS['2_stars'] },
      { name: "1 Star", value: rating_distribution['1_star'], fill: STAR_COLORS['1_star'] },
    ];
    
    const totalRated = ratingBarData.reduce((sum, item) => sum + item.value, 0);

    return (
      <div className="dashboard-content" data-testid="usage-tab-content">
        {/* Summary Stats */}
        <div className="stats-grid">
          <StatCard
            title="Total Sessions"
            value={summary.total_sessions}
            icon={Users}
            color="#6893ff"
          />
          <StatCard
            title="Total Messages"
            value={summary.total_messages}
            subtitle={`${summary.total_user_messages} user / ${summary.total_bot_messages} bot`}
            icon={MessageSquare}
            color="#00AAAA"
          />
          <StatCard
            title="Avg Messages/Session"
            value={summary.avg_messages_per_session}
            icon={TrendingUp}
            color="#ffd93d"
          />
          <StatCard
            title="Avg Rating"
            value={summary.avg_rating ? `${summary.avg_rating.toFixed(1)}/5` : "N/A"}
            subtitle={`${summary.total_rated || 0} rated responses`}
            icon={Star}
            color="#ff9f43"
          />
        </div>

        {/* Messages Over Time Chart */}
        <div className="chart-container">
          <h3 className="chart-title">Messages Over Time</h3>
          {messages_over_time.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={messages_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3a5c" />
                <XAxis
                  dataKey="date"
                  stroke="#BCCBF2"
                  tick={{ fill: "#BCCBF2" }}
                  tickFormatter={(date) => new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                />
                <YAxis stroke="#BCCBF2" tick={{ fill: "#BCCBF2" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0a1628",
                    border: "1px solid #2a3a5c",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                />
                <Legend />
                <Bar dataKey="user_count" name="User Messages" fill="#6893ff" radius={[4, 4, 0, 0]} />
                <Bar dataKey="bot_count" name="Bot Messages" fill="#00AAAA" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">No message data available yet</div>
          )}
        </div>

        {/* Rating Distribution */}
        <div className="chart-container">
          <h3 className="chart-title">User Ratings Distribution</h3>
          {totalRated > 0 ? (
            <div className="rating-section">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ratingBarData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a3a5c" />
                  <XAxis type="number" stroke="#BCCBF2" tick={{ fill: "#BCCBF2" }} />
                  <YAxis dataKey="name" type="category" stroke="#BCCBF2" tick={{ fill: "#BCCBF2" }} width={70} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0a1628",
                      border: "1px solid #2a3a5c",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                  />
                  <Bar dataKey="value" name="Responses" radius={[0, 4, 4, 0]}>
                    {ratingBarData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="rating-legend">
                <div className="rating-summary">
                  <Star size={20} className="fill-yellow-400 text-yellow-400" />
                  <span className="text-white font-semibold">
                    {summary.avg_rating ? summary.avg_rating.toFixed(1) : "0"} average
                  </span>
                  <span className="text-gray-400">
                    ({totalRated} ratings, {rating_distribution.no_rating} unrated)
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="no-data">No ratings yet. Users can rate bot responses with 1-5 stars.</div>
          )}
        </div>
      </div>
    );
  };

  const renderRagTab = () => {
    if (!ragData) return null;

    const { summary, latency_over_time, score_distribution, latency_distribution } = ragData;

    const scoreData = Object.entries(score_distribution).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      value,
      color: SCORE_COLORS[key],
    }));

    const latencyData = [
      { name: "Fast (<5s)", value: latency_distribution.fast, color: "#00AAAA" },
      { name: "Normal (5-30s)", value: latency_distribution.normal, color: "#6893ff" },
      { name: "Slow (30-60s)", value: latency_distribution.slow, color: "#ffd93d" },
      { name: "Very Slow (>60s)", value: latency_distribution.very_slow, color: "#ff6b6b" },
    ].filter((d) => d.value > 0);

    return (
      <div className="dashboard-content" data-testid="rag-tab-content">
        {/* Summary Stats */}
        <div className="stats-grid">
          <StatCard
            title="Total Responses"
            value={summary.total_responses}
            icon={MessageSquare}
            color="#6893ff"
          />
          <StatCard
            title="Avg RAG Latency"
            value={formatLatency(summary.avg_rag_latency_ms)}
            subtitle={`Max: ${formatLatency(summary.max_rag_latency_ms)}`}
            icon={Zap}
            color="#00AAAA"
          />
          <StatCard
            title="Avg LLM Latency"
            value={formatLatency(summary.avg_llm_latency_ms)}
            subtitle={`Max: ${formatLatency(summary.max_llm_latency_ms)}`}
            icon={Clock}
            color="#ffd93d"
          />
          <StatCard
            title="Avg RAG Score"
            value={summary.avg_rag_score.toFixed(3)}
            subtitle={`Range: ${summary.min_rag_score.toFixed(2)} - ${summary.max_rag_score.toFixed(2)}`}
            icon={Target}
            color="#ff6b6b"
          />
        </div>

        {/* Latency Over Time */}
        <div className="chart-container">
          <h3 className="chart-title">Latency Over Time</h3>
          {latency_over_time.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={latency_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3a5c" />
                <XAxis
                  dataKey="date"
                  stroke="#BCCBF2"
                  tick={{ fill: "#BCCBF2" }}
                  tickFormatter={(date) => new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                />
                <YAxis
                  stroke="#BCCBF2"
                  tick={{ fill: "#BCCBF2" }}
                  tickFormatter={(val) => formatLatency(val)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0a1628",
                    border: "1px solid #2a3a5c",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                  formatter={(value) => formatLatency(value)}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="avg_rag_ms"
                  name="RAG Latency"
                  stroke="#00AAAA"
                  strokeWidth={2}
                  dot={{ fill: "#00AAAA" }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_llm_ms"
                  name="LLM Latency"
                  stroke="#6893ff"
                  strokeWidth={2}
                  dot={{ fill: "#6893ff" }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">No latency data available yet</div>
          )}
        </div>

        {/* Score & Latency Distribution */}
        <div className="charts-row">
          <div className="chart-container half">
            <h3 className="chart-title">RAG Score Quality</h3>
            {scoreData.some((d) => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={scoreData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ""}
                  >
                    {scoreData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0a1628",
                      border: "1px solid #2a3a5c",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="no-data">No score data available</div>
            )}
            <div className="score-legend">
              <div className="score-item">
                <span className="score-dot" style={{ backgroundColor: "#00AAAA" }} />
                <span>Excellent (≥0.7)</span>
              </div>
              <div className="score-item">
                <span className="score-dot" style={{ backgroundColor: "#6893ff" }} />
                <span>Good (0.5-0.7)</span>
              </div>
              <div className="score-item">
                <span className="score-dot" style={{ backgroundColor: "#ffd93d" }} />
                <span>Fair (0.3-0.5)</span>
              </div>
              <div className="score-item">
                <span className="score-dot" style={{ backgroundColor: "#ff6b6b" }} />
                <span>Poor (&lt;0.3)</span>
              </div>
            </div>
          </div>

          <div className="chart-container half">
            <h3 className="chart-title">Response Time Distribution</h3>
            {latencyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={latencyData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a3a5c" />
                  <XAxis type="number" stroke="#BCCBF2" tick={{ fill: "#BCCBF2" }} />
                  <YAxis dataKey="name" type="category" stroke="#BCCBF2" tick={{ fill: "#BCCBF2" }} width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0a1628",
                      border: "1px solid #2a3a5c",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                  />
                  <Bar dataKey="value" name="Responses" radius={[0, 4, 4, 0]}>
                    {latencyData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="no-data">No latency distribution data</div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-container" data-testid="dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <Link to="/" className="back-link" data-testid="back-to-chat-btn">
          <ArrowLeft size={20} />
          <span>Back to Chat</span>
        </Link>
        <h1 className="dashboard-title">Analytics Dashboard</h1>
      </header>

      {/* Tabs */}
      <div className="dashboard-tabs">
        <button
          className={`tab-button ${activeTab === "usage" ? "active" : ""}`}
          onClick={() => setActiveTab("usage")}
          data-testid="usage-tab-btn"
        >
          <MessageSquare size={18} />
          Usage Metrics
        </button>
        <button
          className={`tab-button ${activeTab === "rag" ? "active" : ""}`}
          onClick={() => setActiveTab("rag")}
          data-testid="rag-tab-btn"
        >
          <Zap size={18} />
          RAG Performance
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="dashboard-loading">
          <div className="spinner" />
          <p>Loading analytics...</p>
        </div>
      ) : error ? (
        <div className="dashboard-error">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      ) : (
        activeTab === "usage" ? renderUsageTab() : renderRagTab()
      )}
    </div>
  );
};

export default Dashboard;
