import { useEffect, useState } from 'react';
import { ScrollText } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { auditApi } from '../services/api';
import { formatDateTime } from '../lib/utils';
import type { AuditLog } from '../types';

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    auditApi.list({ limit: 100 }).then((res) => {
      setLogs(res.data.logs || []);
      setTotal(res.data.total || 0);
    }).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <p className="text-gray-500 mt-1">{total} audit events recorded</p>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Time</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Action</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Resource</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Resource ID</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">IP</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm text-gray-500 whitespace-nowrap">
                    {formatDateTime(log.created_at)}
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-sm font-medium text-gray-900">{log.action}</span>
                  </td>
                  <td className="px-6 py-3">
                    <Badge>{log.resource_type}</Badge>
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-500 font-mono">
                    {log.resource_id ? log.resource_id.slice(0, 8) + '...' : '—'}
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-500">{log.ip_address || '—'}</td>
                  <td className="px-6 py-3 text-sm text-gray-500">
                    {log.details ? (
                      <span className="text-xs font-mono bg-gray-50 px-2 py-1 rounded">
                        {JSON.stringify(log.details).slice(0, 60)}
                      </span>
                    ) : '—'}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <ScrollText className="w-8 h-8 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-400">No audit logs yet</p>
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
