const BASE = ''  // Vite proxy handles /api -> localhost:5001 in dev; same origin in prod

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  const ct = res.headers.get('content-type') || ''
  if (!ct.includes('application/json')) {
    throw new Error(`Backend unreachable or misconfigured (HTTP ${res.status}). Is the server running?`)
  }
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
  return data
}

export const api = {
  // Auth
  login: (username, password) =>
    request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  register: (username, email, password, signupCode) =>
    request('/api/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password, signup_code: signupCode }) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  checkAuth: () => request('/api/auth/check'),
  getProfile: () => request('/api/auth/profile'),
  changePassword: (currentPassword, newPassword) =>
    request('/api/auth/change-password', { method: 'POST', body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }) }),

  // Models
  getModels: () => request('/api/models'),

  // Image generation (non-streaming)
  generateImage: (prompt) =>
    request('/api/generate-image', { method: 'POST', body: JSON.stringify({ prompt }) }),

  // Image analysis (multipart)
  analyzeImage: (file) => {
    const form = new FormData()
    form.append('file', file)
    return fetch('/api/analyze-image', { method: 'POST', credentials: 'include', body: form }).then(r => r.json())
  },

  // Document analysis (multipart)
  analyzeDocument: (file) => {
    const form = new FormData()
    form.append('file', file)
    return fetch('/api/document-analyze', { method: 'POST', credentials: 'include', body: form }).then(r => r.json())
  },

  // Logs
  getSearchLogs: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/api/logs/searches${q ? '?' + q : ''}`)
  },
  getUserActions: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/api/logs/actions${q ? '?' + q : ''}`)
  },
  getLoginLogs: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/api/logs/logins${q ? '?' + q : ''}`)
  },
  getStats: (days = 30) => request(`/api/logs/stats?days=${days}`),
  exportData: (type = 'all') => request(`/api/logs/export?type=${type}`),

  // Admin
  getAdminUsers: () => request('/api/admin/users'),
  updateUser: (userId, data) =>
    request(`/api/admin/users/${userId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (userId) => request(`/api/admin/users/${userId}`, { method: 'DELETE' }),
  getSignupCodes: () => request('/api/admin/signup-codes'),
  createSignupCode: (expiresInDays) =>
    request('/api/admin/signup-codes', { method: 'POST', body: JSON.stringify({ expires_in_days: expiresInDays }) }),
  deleteSignupCode: (codeId) => request(`/api/admin/signup-codes/${codeId}`, { method: 'DELETE' }),

  // Health
  health: () => request('/api/health'),
}
