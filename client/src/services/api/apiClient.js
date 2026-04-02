const RAW_BASE = import.meta.env.VITE_API_URL || '/api/v1'
const API_BASE_URL = (() => {
  let u = (RAW_BASE || '').trim()
  if (!u) return '/api/v1'
  if (u.startsWith('/')) return u.replace(/\/+$/, '')
  if (u.startsWith(':')) u = 'http://localhost' + u
  if (!u.startsWith('http://') && !u.startsWith('https://')) u = 'http://' + u
  if (!/\/api\/v1\/?$/.test(u)) {
    if (u.endsWith('/')) u += 'api/v1'
    else if (!/\/api\/v1/.test(u)) u += '/api/v1'
  }
  return u.replace(/\/+$/, '')
})()

/**
 * Make an authenticated API request with cookie support
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<{ok: boolean, data: any, error?: string, status: number}>}
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`

  const defaultOptions = {
    credentials: 'include', // Send cookies with every request
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, defaultOptions)
    const contentType = response.headers.get('content-type')
    let data = null

    if (contentType?.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }

    // Handle 401 Unauthorized - Try to refresh token
    if (response.status === 401) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Retry the original request after refresh
        return apiRequest(endpoint, options)
      }
      // If refresh failed, return unauthorized error
      return {
        ok: false,
        status: 401,
        error: data?.error?.message || data?.detail || 'Unauthorized - please login again',
        data: null,
      }
    }

    // Handle other errors
    if (!response.ok) {
      // Check for database connection errors
      if (response.status === 503 && data?.error?.code === 'DATABASE_CONNECTION_ERROR') {
        return {
          ok: false,
          status: 503,
          error: 'Database connection failed. Please ensure the database is running and configured correctly.',
          data: null,
        }
      }
      
      return {
        ok: false,
        status: response.status,
        error: data?.error?.message || data?.message || data?.detail || `HTTP ${response.status}`,
        data: null,
      }
    }

    // Success response
    return {
      ok: true,
      status: response.status,
      data: data?.data || data, // Backend returns {data: ...}, fallback to response
      error: null,
    }
  } catch (error) {
    console.error(`API Request Error [${endpoint}]:`, error)
    return {
      ok: false,
      status: 0,
      error: error.message || 'Network error',
      data: null,
    }
  }
}

/**
 * Refresh access token using the refresh token cookie
 * @returns {Promise<boolean>} - true if refresh succeeded, false otherwise
 */
async function refreshAccessToken() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })

    const data = await response.json()
    return !!(response.ok && data.data)
  } catch (error) {
    console.error('Token refresh failed:', error)
    return false
  }
}

/**
 * Check if user is currently authenticated (has valid access token cookie)
 * @returns {Promise<boolean>}
 */
async function isAuthenticated() {
  const response = await apiRequest('/user/profile')
  return response.ok
}

/**
 * Logout - Clear cookies server-side
 * @returns {Promise<object>}
 */
async function logout() {
  return apiRequest('/auth/logout', { method: 'POST' })
}

// Generic API client with GET, POST, PUT, DELETE methods
export const api = {
  get: (endpoint) => apiRequest(endpoint),
  post: (endpoint, data) => apiRequest(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => apiRequest(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint) => apiRequest(endpoint, { method: 'DELETE' }),
}

// Export API methods grouped by feature
export const auth = {
  register: (data) => apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => logout(),
  refreshToken: () => refreshAccessToken(),
  sendOtp: (data) => apiRequest('/auth/otp/send', { method: 'POST', body: JSON.stringify(data) }),
  verifyOtp: (data) => apiRequest('/auth/otp/verify', { method: 'POST', body: JSON.stringify(data) }),
  sendPasswordResetOtp: (data) => apiRequest('/auth/password/send-otp', { method: 'POST', body: JSON.stringify(data) }),
  verifyPasswordResetOtp: (data) => apiRequest('/auth/password/verify-otp', { method: 'POST', body: JSON.stringify(data) }),
  resetPassword: (data) => apiRequest('/auth/password/reset', { method: 'POST', body: JSON.stringify(data) }),
  sendEmailLoginOtp: (data) => apiRequest('/auth/login/send-email-otp', { method: 'POST', body: JSON.stringify(data) }),
  verifyEmailLoginOtp: (data) => apiRequest('/auth/login/verify-email-otp', { method: 'POST', body: JSON.stringify(data) }),
}

export const user = {
  getProfile: () => apiRequest('/user/profile'),
  updateProfile: (data) => apiRequest('/user/profile', { method: 'PUT', body: JSON.stringify(data) }),
  getSubscription: () => apiRequest('/user/subscription'),
  sendPhoneChangeOtp: (data) => apiRequest('/user/phone-change/send-otp', { method: 'POST', body: JSON.stringify(data) }),
  verifyPhoneChangeOtp: (data) => apiRequest('/user/phone-change/verify-otp', { method: 'POST', body: JSON.stringify(data) }),
  sendEmailChangeOtp: (data) => apiRequest('/user/email-change/send-otp', { method: 'POST', body: JSON.stringify(data) }),
  verifyEmailChangeOtp: (data) => apiRequest('/user/email-change/verify-otp', { method: 'POST', body: JSON.stringify(data) }),
}

export const purchaseOrders = {
  create: (data) => apiRequest('/purchase-orders', { method: 'POST', body: JSON.stringify(data) }),
  list: (page = 1, pageSize = 20, includeArchived = false) => apiRequest(`/purchase-orders?page=${page}&page_size=${pageSize}&include_archived=${includeArchived}`),
  get: (id) => apiRequest(`/purchase-orders/${id}`),
  update: (id, data) => apiRequest(`/purchase-orders/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiRequest(`/purchase-orders/${id}`, { method: 'DELETE' }),
  archive: (id) => apiRequest(`/purchase-orders/${id}/archive`, { method: 'POST' }),
  markPaid: (id) => apiRequest(`/purchase-orders/${id}/mark-paid`, { method: 'POST' }),
  sendReminder: (id) => apiRequest(`/purchase-orders/${id}/send-reminder`, { method: 'POST' }),
  sendLegalNotice: (id, data) => apiRequest(`/purchase-orders/${id}/send-legal-notice`, { method: 'POST', body: JSON.stringify(data) }),
}

export const admin = {
  getSettings: () => apiRequest('/user/admin/settings'),
  updateSettings: (data) => apiRequest('/user/admin/settings', { method: 'POST', body: JSON.stringify(data) }),
}

// Manual reminder for PO (additive standalone function)
export const sendPOReminder = (poId, data = null) => apiRequest(`/purchase-orders/${poId}/send-reminder`, { method: 'POST', body: data ? JSON.stringify(data) : undefined })

export const getPOReminderConfig = () => apiRequest('/admin/po-reminders')

export const updatePOReminderConfig = (data) => apiRequest('/admin/po-reminders', { method: 'PUT', body: JSON.stringify(data) })

export const sendChatMessage = (message) => apiRequest('/chat', { method: 'POST', body: JSON.stringify({ message }) })

export const defaulters = {
  create: (data) => apiRequest('/defaulters', { method: 'POST', body: JSON.stringify(data) }),
  list: (page = 1, pageSize = 20) => apiRequest(`/defaulters?page=${page}&page_size=${pageSize}`),
  get: (id) => apiRequest(`/defaulters/${id}`),
  update: (id, data) => apiRequest(`/defaulters/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiRequest(`/defaulters/${id}`, { method: 'DELETE' }),
  uploadDocument: (id, data) => apiRequest(`/defaulters/${id}/upload-document`, { method: 'POST', body: JSON.stringify(data) }),
}

export const invoices = {
  create: (data) => apiRequest('/invoices', { method: 'POST', body: JSON.stringify(data) }),
  list: (params = {}) => {
    const queryParams = new URLSearchParams()
    if (params.skip !== undefined) queryParams.append('skip', params.skip)
    if (params.limit !== undefined) queryParams.append('limit', params.limit)
    if (params.status) queryParams.append('status', params.status)
    if (params.counterparty_gstin) queryParams.append('counterparty_gstin', params.counterparty_gstin)
    if (params.counterparty_pan) queryParams.append('counterparty_pan', params.counterparty_pan)
    if (params.search) queryParams.append('search', params.search)
    const query = queryParams.toString()
    return apiRequest(`/invoices${query ? '?' + query : ''}`)
  },
  get: (id) => apiRequest(`/invoices/${id}`),
  update: (id, data) => apiRequest(`/invoices/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiRequest(`/invoices/${id}`, { method: 'DELETE' }),
  toggleAcknowledgment: (id) => apiRequest(`/invoices/${id}/acknowledge`, { method: 'POST' }),
  addFollowUpNote: (id, note) => apiRequest(`/invoices/${id}/follow-up`, { method: 'POST', body: JSON.stringify({ note }) }),
  getDueReminders: () => apiRequest('/invoices/reminders/due'),
}

export const creditReports = {
  create: (data) => apiRequest('/credit-reports', { method: 'POST', body: JSON.stringify(data) }),
  list: (page = 1, pageSize = 20) => apiRequest(`/credit-reports?page=${page}&page_size=${pageSize}`),
  get: (id) => apiRequest(`/credit-reports/${id}`),
  update: (id, data) => apiRequest(`/credit-reports/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
}

export const settlements = {
  create: (data) => apiRequest('/settlements', { method: 'POST', body: JSON.stringify(data) }),
  list: (page = 1, pageSize = 20) => apiRequest(`/settlements?page=${page}&page_size=${pageSize}`),
  get: (id) => apiRequest(`/settlements/${id}`),
  update: (id, data) => apiRequest(`/settlements/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
}

export const appointments = {
  create: (data) => apiRequest('/appointments', { method: 'POST', body: JSON.stringify(data) }),
  list: (status = null) => {
    const query = status ? `?status=${status}` : ''
    return apiRequest(`/appointments${query}`)
  },
  get: (id) => apiRequest(`/appointments/${id}`),
  update: (id, data) => apiRequest(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiRequest(`/appointments/${id}`, { method: 'DELETE' }),
}

export const contact = {
  submit: (data) => apiRequest('/contact/public', { method: 'POST', body: JSON.stringify(data) }),
}

export const cms = {
  getPage: (slug) => apiRequest(`/cms/pages/${slug}`),
  listPages: () => apiRequest('/cms/admin/pages'),
  createPage: (data) => apiRequest('/cms/admin/pages', { method: 'POST', body: JSON.stringify(data) }),
  updatePage: (id, data) => apiRequest(`/cms/admin/pages/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePage: (id) => apiRequest(`/cms/admin/pages/${id}`, { method: 'DELETE' }),
  addSection: (pageId, data) => apiRequest(`/cms/admin/pages/${pageId}/sections`, { method: 'POST', body: JSON.stringify(data) }),
  updateSection: (id, data) => apiRequest(`/cms/admin/sections/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSection: (id) => apiRequest(`/cms/admin/sections/${id}`, { method: 'DELETE' }),
  reorderSections: (pageId, payload) => apiRequest(`/cms/admin/pages/${pageId}/reorder-sections`, { method: 'PUT', body: JSON.stringify(payload) }),
}

export const wallet = {
  getBalance: () => apiRequest('/wallet/balance'),
  getHistory: (page = 1, limit = 10) => apiRequest(`/wallet/history?page=${page}&limit=${limit}`),
  redeem: (amount, reference) => apiRequest('/wallet/redeem', { method: 'POST', body: JSON.stringify({ amount, reference }) }),
}

export const adminApi = {
  listInvitations: ({ skip = 0, limit = 50 } = {}) => apiRequest(`/admin/invitations?skip=${skip}&limit=${limit}`),
  createInvitation: (data) => apiRequest('/admin/invitations', { method: 'POST', body: JSON.stringify(data) }),
  updateInvitation: (id, data) => apiRequest(`/admin/invitations/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteInvitation: (id) => apiRequest(`/admin/invitations/${id}`, { method: 'DELETE' }),
}

export const adminConfig = {
  getPOReminders: () => apiRequest('/admin/po-reminders'),
  updatePOReminders: (data) => apiRequest('/admin/po-reminders', { method: 'PUT', body: JSON.stringify(data) }),
}

export const invitations = {
  verify: (token) => apiRequest(`/invitations/verify?token=${encodeURIComponent(token)}`),
  accept: (data) => apiRequest('/invitations/accept', { method: 'POST', body: JSON.stringify(data) }),
  acceptStrict: (data) => apiRequest('/invitations/accept-invitation', { method: 'POST', body: JSON.stringify(data) }),
}

export const drive = {
  getAuthUrl: () => apiRequest('/drive/auth-url'),
  callback: (code, state) => apiRequest('/drive/callback', { method: 'POST', body: JSON.stringify({ code, state }) }),
  listFiles: () => apiRequest('/drive/files'),
  upload: (formData) => apiRequest('/drive/upload', {
    method: 'POST',
    body: formData,
    // Do NOT set Content-Type header for FormData; fetch sets it with boundary automatically
    headers: {}
  }),
}

// Utility: Check authentication status
export const authUtils = {
  isAuthenticated,
  refreshToken: refreshAccessToken,
}

export default apiRequest
