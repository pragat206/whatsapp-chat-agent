import { useEffect, useState, FormEvent } from 'react';
import { Users, Plus, X, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { usersApi } from '../services/api';
import { formatDate } from '../lib/utils';
import type { User } from '../types';
import toast from 'react-hot-toast';

export default function Team() {
  const [users, setUsers] = useState<User[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('operator');

  const load = () => {
    usersApi.list().then((res) => setUsers(res.data.users || [])).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await usersApi.create({ email, password, full_name: fullName, role_names: [role] });
      toast.success('User created');
      setShowForm(false);
      setEmail(''); setPassword(''); setFullName(''); setRole('operator');
      load();
    } catch {
      toast.error('Failed to create user');
    }
  };

  const toggleActive = async (user: User) => {
    try {
      await usersApi.update(user.id, { is_active: !user.is_active });
      load();
    } catch {
      toast.error('Failed to update user');
    }
  };

  const roleColor: Record<string, string> = {
    super_admin: 'bg-red-100 text-red-700',
    admin: 'bg-purple-100 text-purple-700',
    analyst: 'bg-blue-100 text-blue-700',
    operator: 'bg-green-100 text-green-700',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team Management</h1>
          <p className="text-gray-500 mt-1">Manage users and roles</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4 mr-2" /> Add User
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Add Team Member</h3>
              <button onClick={() => setShowForm(false)}><X className="w-4 h-4 text-gray-400" /></button>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-gray-700">Role</label>
                <select
                  className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="operator">Operator</option>
                  <option value="analyst">Analyst</option>
                  <option value="admin">Admin</option>
                  <option value="super_admin">Super Admin</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <Button type="submit">Create User</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">User</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Roles</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Joined</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-brand-100 flex items-center justify-center">
                        <span className="text-sm font-medium text-brand-700">{user.full_name.charAt(0)}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1.5">
                      {user.roles.map((r) => (
                        <span key={r.id} className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${roleColor[r.name] || 'bg-gray-100 text-gray-600'}`}>
                          <Shield className="w-3 h-3" />
                          {r.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={user.is_active ? 'active' : 'closed'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(user.created_at)}</td>
                  <td className="px-6 py-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleActive(user)}
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
