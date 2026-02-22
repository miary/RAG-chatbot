import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import {
  MessageSquare,
  Users,
  Clock,
  TrendingUp,
  ThumbsUp,
  ThumbsDown,
  ArrowLeft,
  Activity,
  Zap,
  Target,
  Loader2,
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Color palette matching the dark theme
const COLORS = {
  primary: '#6893ff',
  secondary: '#3b6fe0',
  accent: '#00AAAA',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  background: '#0a1628',
  card: '#111b2e',
  border: '#2a3a5c',
  text: '#ffffff',
  textMuted: '#BCCBF2',
};

const CHART_COLORS = ['#6893ff', '#00AAAA', '#22c55e', '#f59e0b', '#ef4444'];

// Stat Card Component
const StatCard = ({ icon: Icon, label, value, subValue, color = COLORS.primary }) => (
  <div
    className="rounded-xl p-4 border"
    style={{ backgroundColor: COLORS.card, borderColor: COLORS.border }}
    data-testid={`stat-card-${label.toLowerCase().replace(/\s/g, '-')}`}
  >
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm mb-1" style={{ color: COLORS.textMuted }}>{label}</p>
        <p className="text-2xl font-bold" style={{ color: COLORS.text }}>{value}</p>
        {subValue && (
          <p className="text-xs mt-1" style={{ color: COLORS.textMuted }}>{subValue}</p>
        )}
      </div>
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center"
        style={{ backgroundColor: `${color}20` }}
      >
        <Icon size={20} style={{ color }} />
      </div>
    </div>
  </div>
);

// Chart Card Wrapper
const ChartCard = ({ title, children, className = '' }) => (
  <div
    className={`rounded-xl p-4 border ${className}`}
    style={{ backgroundColor: COLORS.card, borderColor: COLORS.border }}
  >
    <h3 className="text-sm font-semibold mb-4" style={{ color: COLORS.text }}>{title}</h3>
    {children}
  </div>
);

// Custom Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div
        className="rounded-lg px-3 py-2 shadow-lg border"
        style={{ backgroundColor: COLORS.card, borderColor: COLORS.border }}
      >
        <p className="text-xs mb-1" style={{ color: COLORS.textMuted }}>{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Usage Tab Content
const UsageTab = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin" size={32} style={{ color: COLORS.primary }} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p style={{ color: COLORS.textMuted }}>No data available</p>
      </div>
    );
  }

  const { summary, feedback, messages_per_day, sessions_per_day } = data;

  const feedbackData = [
    { name: 'Helpful', value: feedback.helpful, color: COLORS.success },
    { name: 'Not Helpful', value: feedback.not_helpful, color: COLORS.danger },
    { name: 'No Feedback', value: feedback.no_feedback, color: COLORS.border },
  ].filter(d => d.value > 0);

  // Format dates for display
  const formattedMessagesPerDay = messages_per_day.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  const formattedSessionsPerDay = sessions_per_day.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={MessageSquare}
          label="Total Messages"
          value={summary.total_messages.toLocaleString()}
          subValue={`${summary.total_user_messages} user / ${summary.total_bot_messages} bot`}
          color={COLORS.primary}
        />
        <StatCard
          icon={Users}
          label="Total Sessions"
          value={summary.total_sessions.toLocaleString()}
          color={COLORS.accent}
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Messages/Session"
          value={summary.avg_messages_per_session}
          color={COLORS.success}
        />
        <StatCard
          icon={ThumbsUp}
          label="Helpful Rate"
          value={
            feedback.helpful + feedback.not_helpful > 0
              ? `${Math.round((feedback.helpful / (feedback.helpful + feedback.not_helpful)) * 100)}%`
              : 'N/A'
          }
          subValue={`${feedback.helpful} helpful / ${feedback.not_helpful} not helpful`}
          color={COLORS.warning}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Messages Per Day Chart */}
        <ChartCard title="Messages Over Time (Last 30 Days)">
          <div className="h-64">
            {formattedMessagesPerDay.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedMessagesPerDay}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                  <XAxis
                    dataKey="date"
                    stroke={COLORS.textMuted}
                    tick={{ fill: COLORS.textMuted, fontSize: 11 }}
                  />
                  <YAxis stroke={COLORS.textMuted} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="count"
                    name="Messages"
                    stroke={COLORS.primary}
                    strokeWidth={2}
                    dot={{ fill: COLORS.primary, strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p style={{ color: COLORS.textMuted }}>No message data yet</p>
              </div>
            )}
          </div>
        </ChartCard>

        {/* Sessions Per Day Chart */}
        <ChartCard title="Sessions Over Time (Last 30 Days)">
          <div className="h-64">
            {formattedSessionsPerDay.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={formattedSessionsPerDay}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                  <XAxis
                    dataKey="date"
                    stroke={COLORS.textMuted}
                    tick={{ fill: COLORS.textMuted, fontSize: 11 }}
                  />
                  <YAxis stroke={COLORS.textMuted} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Sessions" fill={COLORS.accent} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p style={{ color: COLORS.textMuted }}>No session data yet</p>
              </div>
            )}
          </div>
        </ChartCard>
      </div>

      {/* Feedback Distribution */}
      <ChartCard title="Feedback Distribution">
        <div className="h-64">
          {feedbackData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={feedbackData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {feedbackData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  formatter={(value) => <span style={{ color: COLORS.text }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p style={{ color: COLORS.textMuted }}>No feedback data yet</p>
            </div>
          )}
        </div>
      </ChartCard>
    </div>
  );
};

// RAG Performance Tab Content
const RagPerformanceTab = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin" size={32} style={{ color: COLORS.primary }} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p style={{ color: COLORS.textMuted }}>No data available</p>
      </div>
    );
  }

  const { summary, performance_per_day, score_distribution, latency_distribution, recent_responses } = data;

  // Format dates for display
  const formattedPerformancePerDay = performance_per_day.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  return (
    <div className="space-y-6">
      {/* Performance Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Clock}
          label="Avg Total Latency"
          value={`${Math.round(summary.avg_total_latency_ms)}ms`}
          subValue={`Min: ${summary.min_total_latency_ms}ms / Max: ${summary.max_total_latency_ms}ms`}
          color={COLORS.primary}
        />
        <StatCard
          icon={Zap}
          label="Avg RAG Query Time"
          value={`${Math.round(summary.avg_rag_latency_ms)}ms`}
          subValue={`Min: ${summary.min_rag_latency_ms}ms / Max: ${summary.max_rag_latency_ms}ms`}
          color={COLORS.accent}
        />
        <StatCard
          icon={Activity}
          label="Avg LLM Response Time"
          value={`${Math.round(summary.avg_llm_latency_ms)}ms`}
          subValue={`Min: ${summary.min_llm_latency_ms}ms / Max: ${summary.max_llm_latency_ms}ms`}
          color={COLORS.success}
        />
        <StatCard
          icon={Target}
          label="Avg RAG Score"
          value={summary.avg_rag_score.toFixed(3)}
          subValue="Similarity score (0-1)"
          color={COLORS.warning}
        />
      </div>

      {/* Performance Over Time */}
      <ChartCard title="Performance Over Time (Last 30 Days)">
        <div className="h-72">
          {formattedPerformancePerDay.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedPerformancePerDay}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                <XAxis
                  dataKey="date"
                  stroke={COLORS.textMuted}
                  tick={{ fill: COLORS.textMuted, fontSize: 11 }}
                />
                <YAxis stroke={COLORS.textMuted} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend formatter={(value) => <span style={{ color: COLORS.text }}>{value}</span>} />
                <Line
                  type="monotone"
                  dataKey="avg_total_latency"
                  name="Total Latency (ms)"
                  stroke={COLORS.primary}
                  strokeWidth={2}
                  dot={{ fill: COLORS.primary }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_rag_latency"
                  name="RAG Latency (ms)"
                  stroke={COLORS.accent}
                  strokeWidth={2}
                  dot={{ fill: COLORS.accent }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_llm_latency"
                  name="LLM Latency (ms)"
                  stroke={COLORS.success}
                  strokeWidth={2}
                  dot={{ fill: COLORS.success }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p style={{ color: COLORS.textMuted }}>No performance data yet</p>
            </div>
          )}
        </div>
      </ChartCard>

      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* RAG Score Distribution */}
        <ChartCard title="RAG Score Distribution">
          <div className="h-64">
            {score_distribution.some(d => d.count > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={score_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                  <XAxis
                    dataKey="range"
                    stroke={COLORS.textMuted}
                    tick={{ fill: COLORS.textMuted, fontSize: 11 }}
                  />
                  <YAxis stroke={COLORS.textMuted} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Responses" fill={COLORS.warning} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p style={{ color: COLORS.textMuted }}>No score data yet</p>
              </div>
            )}
          </div>
        </ChartCard>

        {/* Response Time Distribution */}
        <ChartCard title="Response Time Distribution">
          <div className="h-64">
            {latency_distribution.some(d => d.count > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={latency_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                  <XAxis
                    dataKey="range"
                    stroke={COLORS.textMuted}
                    tick={{ fill: COLORS.textMuted, fontSize: 11 }}
                  />
                  <YAxis stroke={COLORS.textMuted} tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="Responses" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p style={{ color: COLORS.textMuted }}>No latency data yet</p>
              </div>
            )}
          </div>
        </ChartCard>
      </div>

      {/* Recent Responses Table */}
      <ChartCard title="Recent Responses">
        <div className="overflow-x-auto">
          {recent_responses.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: `1px solid ${COLORS.border}` }}>
                  <th className="text-left py-2 px-3" style={{ color: COLORS.textMuted }}>Timestamp</th>
                  <th className="text-right py-2 px-3" style={{ color: COLORS.textMuted }}>RAG (ms)</th>
                  <th className="text-right py-2 px-3" style={{ color: COLORS.textMuted }}>LLM (ms)</th>
                  <th className="text-right py-2 px-3" style={{ color: COLORS.textMuted }}>Total (ms)</th>
                  <th className="text-right py-2 px-3" style={{ color: COLORS.textMuted }}>RAG Score</th>
                </tr>
              </thead>
              <tbody>
                {recent_responses.map((response) => (
                  <tr
                    key={response.id}
                    style={{ borderBottom: `1px solid ${COLORS.border}` }}
                    className="hover:bg-[#1c2e4c] transition-colors"
                  >
                    <td className="py-2 px-3" style={{ color: COLORS.text }}>
                      {new Date(response.timestamp).toLocaleString()}
                    </td>
                    <td className="text-right py-2 px-3" style={{ color: COLORS.accent }}>
                      {response.rag_latency_ms}
                    </td>
                    <td className="text-right py-2 px-3" style={{ color: COLORS.success }}>
                      {response.llm_latency_ms}
                    </td>
                    <td className="text-right py-2 px-3" style={{ color: COLORS.primary }}>
                      {response.total_latency_ms}
                    </td>
                    <td className="text-right py-2 px-3" style={{ color: COLORS.warning }}>
                      {response.top_rag_score.toFixed(3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="flex items-center justify-center h-32">
              <p style={{ color: COLORS.textMuted }}>No responses yet</p>
            </div>
          )}
        </div>
      </ChartCard>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('usage');
  const [usageData, setUsageData] = useState(null);
  const [ragData, setRagData] = useState(null);
  const [loadingUsage, setLoadingUsage] = useState(true);
  const [loadingRag, setLoadingRag] = useState(true);

  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        const res = await axios.get(`${API}/analytics/usage/`);
        setUsageData(res.data);
      } catch (e) {
        console.error('Failed to fetch usage data:', e);
      } finally {
        setLoadingUsage(false);
      }
    };

    const fetchRagData = async () => {
      try {
        const res = await axios.get(`${API}/analytics/rag-performance/`);
        setRagData(res.data);
      } catch (e) {
        console.error('Failed to fetch RAG data:', e);
      } finally {
        setLoadingRag(false);
      }
    };

    fetchUsageData();
    fetchRagData();
  }, []);

  return (
    <div className="min-h-screen" style={{ backgroundColor: COLORS.background }}>
      {/* Header */}
      <header
        className="border-b px-4 md:px-6 py-4"
        style={{ backgroundColor: COLORS.card, borderColor: COLORS.border }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-sm hover:opacity-80 transition-opacity"
              style={{ color: COLORS.textMuted }}
              data-testid="back-to-chat-btn"
            >
              <ArrowLeft size={18} />
              Back to Chat
            </button>
            <h1 className="text-xl font-semibold" style={{ color: COLORS.text }}>
              Analytics Dashboard
            </h1>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="px-4 md:px-6 pt-4" style={{ backgroundColor: COLORS.background }}>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('usage')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'usage'
                ? 'text-white'
                : 'hover:bg-[#1c2e4c]'
            }`}
            style={{
              backgroundColor: activeTab === 'usage' ? COLORS.primary : 'transparent',
              color: activeTab === 'usage' ? COLORS.text : COLORS.textMuted,
            }}
            data-testid="usage-tab-btn"
          >
            Usage Metrics
          </button>
          <button
            onClick={() => setActiveTab('rag')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'rag'
                ? 'text-white'
                : 'hover:bg-[#1c2e4c]'
            }`}
            style={{
              backgroundColor: activeTab === 'rag' ? COLORS.primary : 'transparent',
              color: activeTab === 'rag' ? COLORS.text : COLORS.textMuted,
            }}
            data-testid="rag-performance-tab-btn"
          >
            RAG Performance
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <main className="px-4 md:px-6 py-6">
        {activeTab === 'usage' ? (
          <UsageTab data={usageData} loading={loadingUsage} />
        ) : (
          <RagPerformanceTab data={ragData} loading={loadingRag} />
        )}
      </main>
    </div>
  );
};

export default Dashboard;
