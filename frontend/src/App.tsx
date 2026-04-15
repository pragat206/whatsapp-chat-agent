import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Conversations from './pages/Conversations';
import ConversationDetail from './pages/ConversationDetail';
import Products from './pages/Products';
import Knowledge from './pages/Knowledge';
import Analytics from './pages/Analytics';
import Team from './pages/Team';
import Settings from './pages/Settings';
import AuditLogs from './pages/AuditLogs';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
          <p className="text-sm text-gray-500 mt-3">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/conversations" element={<Conversations />} />
        <Route path="/conversations/:id" element={<ConversationDetail />} />
        <Route path="/products" element={<Products />} />
        <Route path="/knowledge" element={<Knowledge />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/team" element={<Team />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/audit-logs" element={<AuditLogs />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: { fontSize: '14px' },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}
