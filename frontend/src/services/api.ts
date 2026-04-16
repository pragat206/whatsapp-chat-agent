import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const res = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', res.data.access_token);
          localStorage.setItem('refresh_token', res.data.refresh_token);
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api(error.config);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  refresh: (refresh_token: string) =>
    api.post('/auth/refresh', { refresh_token }),
};

// Users
export const usersApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    api.get('/users', { params }),
  create: (data: { email: string; password: string; full_name: string; role_names: string[] }) =>
    api.post('/users', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/users/${id}`, data),
  roles: () => api.get('/users/roles'),
};

// Conversations
export const conversationsApi = {
  list: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get('/conversations', { params }),
  get: (id: string) => api.get(`/conversations/${id}`),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/conversations/${id}`, data),
  handoff: (id: string, reason?: string) =>
    api.post(`/conversations/${id}/handoff`, { reason }),
  resumeAi: (id: string) =>
    api.post(`/conversations/${id}/resume-ai`),
  addNote: (id: string, content: string) =>
    api.post(`/conversations/${id}/notes`, { content }),
  send: (id: string, content: string) =>
    api.post(`/conversations/${id}/send`, { content }),
};

// Products
export const productsApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    api.get('/products', { params }),
  get: (id: string) => api.get(`/products/${id}`),
  create: (data: Record<string, unknown>) => api.post('/products', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/products/${id}`, data),
  categories: () => api.get('/products/categories/list'),
  createCategory: (data: { name: string; description?: string }) =>
    api.post('/products/categories', data),
};

// Knowledge
export const knowledgeApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    api.get('/knowledge', { params }),
  upload: (formData: FormData) =>
    api.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  manual: (data: { title: string; content: string; product_id?: string }) =>
    api.post('/knowledge/manual', data),
  reindex: (id: string) => api.post(`/knowledge/${id}/reindex`),
  toggle: (id: string) => api.patch(`/knowledge/${id}/toggle`),
};

// Analytics
export const analyticsApi = {
  kpis: (params?: { date_from?: string; date_to?: string }) =>
    api.get('/analytics/kpis', { params }),
  overview: (params?: { date_from?: string; date_to?: string }) =>
    api.get('/analytics/overview', { params }),
  trends: (params?: { date_from?: string; date_to?: string }) =>
    api.get('/analytics/trends', { params }),
};

// Settings
export const settingsApi = {
  list: (category?: string) =>
    api.get('/settings', { params: { category } }),
  update: (key: string, data: { value?: string; value_json?: Record<string, unknown> }) =>
    api.put(`/settings/${key}`, data),
};

// Audit Logs
export const auditApi = {
  list: (params?: { action?: string; limit?: number; offset?: number }) =>
    api.get('/audit-logs', { params }),
};

export default api;
