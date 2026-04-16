import { useEffect, useState } from 'react';
import {
  MessageSquare,
  Bot,
  UserCheck,
  TrendingUp,
  AlertTriangle,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Users,
  CheckCircle2,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { analyticsApi, conversationsApi } from '../services/api';
import type { DashboardKPIs, ConversationTrend, Conversation } from '../types';
import { Badge } from '../components/ui/Badge';
import { formatRelativeTime } from '../lib/utils';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  trend?: number;
  color: string;
}

function KPICard({ title, value, subtitle, icon: Icon, trend, color }: KPICardProps) {
  return (
    <Card>
      <CardContent className="py-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
          </div>
          <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        </div>
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-3">
            {trend >= 0 ? (
              <ArrowUpRight className="w-4 h-4 text-green-500" />
            ) : (
              <ArrowDownRight className="w-4 h-4 text-red-500" />
            )}
            <span className={`text-sm font-medium ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {Math.abs(trend)}%
            </span>
            <span className="text-xs text-gray-400">vs last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<ConversationTrend[]>([]);
  const [recentConversations, setRecentConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    analyticsApi.kpis().then((res) => setKpis(res.data)).catch(() => {});
    analyticsApi.trends().then((res) => setTrends(res.data.trends || [])).catch(() => {});
    conversationsApi
      .list({ limit: 5 })
      .then((res) => setRecentConversations(res.data.conversations || []))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your WhatsApp AI agent performance</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Total Conversations"
          value={kpis?.total_conversations ?? 0}
          icon={MessageSquare}
          color="bg-brand-500"
        />
        <KPICard
          title="AI Resolution Rate"
          value={`${kpis?.ai_resolution_rate ?? 0}%`}
          subtitle={`${kpis?.ai_handled_count ?? 0} AI handled`}
          icon={Bot}
          color="bg-emerald-500"
        />
        <KPICard
          title="Active Conversations"
          value={kpis?.active_conversations ?? 0}
          icon={Users}
          color="bg-amber-500"
        />
        <KPICard
          title="Leads Captured"
          value={kpis?.leads_captured ?? 0}
          icon={Target}
          color="bg-purple-500"
        />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        <Card>
          <CardContent className="py-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{kpis?.resolved_conversations ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Resolved</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{kpis?.escalated_count ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Escalated</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{kpis?.human_handled_count ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Human Handled</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4 text-center">
            <p className="text-2xl font-bold text-red-600">{kpis?.failed_messages ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Failed Messages</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-gray-900">Conversation Trends</h3>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="inbound" stackId="1" stroke="#3b82f6" fill="#dbeafe" name="Inbound" />
                  <Area type="monotone" dataKey="outbound" stackId="1" stroke="#10b981" fill="#d1fae5" name="Outbound" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-gray-900">AI vs Human</h3>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="ai_handled" fill="#8b5cf6" name="AI Handled" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="human_handled" fill="#f97316" name="Human Handled" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Conversations */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-semibold text-gray-900">Recent Conversations</h3>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Contact</th>
                <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Handler</th>
                <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Messages</th>
                <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Last Activity</th>
              </tr>
            </thead>
            <tbody>
              {recentConversations.map((conv) => (
                <tr key={conv.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {conv.contact.display_name || conv.contact.phone_number}
                      </p>
                      <p className="text-xs text-gray-500">{conv.contact.phone_number}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={conv.status}>{conv.status}</Badge>
                  </td>
                  <td className="px-6 py-4">
                    {conv.is_ai_active ? (
                      <span className="inline-flex items-center gap-1 text-xs text-purple-600">
                        <Bot className="w-3.5 h-3.5" /> AI
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-orange-600">
                        <UserCheck className="w-3.5 h-3.5" /> Human
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{conv.message_count}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {conv.last_message_at ? formatRelativeTime(conv.last_message_at) : '—'}
                  </td>
                </tr>
              ))}
              {recentConversations.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-sm text-gray-400">
                    No conversations yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
