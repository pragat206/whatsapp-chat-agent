import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Package,
  BookOpen,
  BarChart3,
  Users,
  Settings,
  ScrollText,
  LogOut,
  Bot,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { cn } from '../../lib/utils';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/conversations', icon: MessageSquare, label: 'Conversations' },
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/knowledge', icon: BookOpen, label: 'Knowledge Base' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/team', icon: Users, label: 'Team' },
  { to: '/settings', icon: Settings, label: 'Settings' },
  { to: '/audit-logs', icon: ScrollText, label: 'Audit Logs' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col z-30">
      {/* Brand */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-gray-100">
        <div className="w-9 h-9 rounded-lg bg-brand-600 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-gray-900">WhatsApp Agent</h1>
          <p className="text-xs text-gray-500">AI Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* User footer */}
      <div className="border-t border-gray-100 p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center">
            <span className="text-sm font-medium text-brand-700">
              {user?.full_name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.full_name}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
