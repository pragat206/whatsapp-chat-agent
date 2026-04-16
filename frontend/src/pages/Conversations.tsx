import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Bot, UserCheck, Search, Filter } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { conversationsApi } from '../services/api';
import { formatRelativeTime } from '../lib/utils';
import type { Conversation } from '../types';

export default function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const params: Record<string, string | number> = { limit: 50 };
    if (statusFilter) params.status = statusFilter;
    conversationsApi
      .list(params)
      .then((res) => {
        setConversations(res.data.conversations || []);
        setTotal(res.data.total || 0);
      })
      .catch(() => {});
  }, [statusFilter]);

  const filtered = search
    ? conversations.filter(
        (c) =>
          c.contact.display_name?.toLowerCase().includes(search.toLowerCase()) ||
          c.contact.phone_number.includes(search)
      )
    : conversations;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Conversations</h1>
          <p className="text-gray-500 mt-1">{total} total conversations</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or phone..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex gap-2">
          {['', 'active', 'handoff', 'resolved', 'closed'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-brand-50 text-brand-700 border border-brand-200'
                  : 'text-gray-600 hover:bg-gray-100 border border-transparent'
              }`}
            >
              {status || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Conversation List */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Contact</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">State</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Handler</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Tags</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Messages</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Last Activity</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((conv) => (
                <tr
                  key={conv.id}
                  className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/conversations/${conv.id}`)}
                >
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {conv.contact.display_name || 'Unknown'}
                      </p>
                      <p className="text-xs text-gray-500">{conv.contact.phone_number}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={conv.status}>{conv.status}</Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{conv.state}</td>
                  <td className="px-6 py-4">
                    {conv.is_ai_active ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-purple-600">
                        <Bot className="w-3.5 h-3.5" /> AI
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-orange-600">
                        <UserCheck className="w-3.5 h-3.5" /> Human
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1 flex-wrap">
                      {conv.tags.map((tag) => (
                        <span
                          key={tag.id}
                          className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                          style={{ backgroundColor: tag.color + '20', color: tag.color }}
                        >
                          {tag.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{conv.message_count}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {conv.last_message_at ? formatRelativeTime(conv.last_message_at) : '—'}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-16 text-center">
                    <MessageSquare className="w-8 h-8 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-400">No conversations found</p>
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
