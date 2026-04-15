import { useEffect, useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { analyticsApi } from '../services/api';
import type { DashboardKPIs, ConversationTrend } from '../types';

const PIE_COLORS = ['#3b82f6', '#8b5cf6', '#f97316', '#10b981', '#ef4444'];

export default function Analytics() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<ConversationTrend[]>([]);

  useEffect(() => {
    analyticsApi.kpis().then((res) => setKpis(res.data)).catch(() => {});
    analyticsApi.trends().then((res) => setTrends(res.data.trends || [])).catch(() => {});
  }, []);

  const handlerPie = kpis
    ? [
        { name: 'AI Handled', value: kpis.ai_handled_count },
        { name: 'Human Handled', value: kpis.human_handled_count },
        { name: 'Escalated', value: kpis.escalated_count },
      ]
    : [];

  const statusPie = kpis
    ? [
        { name: 'Active', value: kpis.active_conversations },
        { name: 'Resolved', value: kpis.resolved_conversations },
        { name: 'Leads', value: kpis.leads_captured },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-500 mt-1">In-depth performance metrics and trends</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total Inbound', value: kpis?.total_inbound_messages ?? 0 },
          { label: 'Total Outbound', value: kpis?.total_outbound_messages ?? 0 },
          { label: 'AI Resolution', value: `${kpis?.ai_resolution_rate ?? 0}%` },
          { label: 'Leads', value: kpis?.leads_captured ?? 0 },
          { label: 'Failed', value: kpis?.failed_messages ?? 0 },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="py-4 text-center">
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Message Volume Chart */}
      <Card>
        <CardHeader>
          <h3 className="text-sm font-semibold text-gray-900">Message Volume Over Time</h3>
        </CardHeader>
        <CardContent>
          <div className="h-80">
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI vs Human Bar */}
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-gray-900">AI vs Human Handling</h3>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="ai_handled" fill="#8b5cf6" name="AI" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="human_handled" fill="#f97316" name="Human" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Handler Distribution Pie */}
        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-gray-900">Handler Distribution</h3>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={handlerPie}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {handlerPie.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
