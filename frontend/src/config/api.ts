export const API_BASE_URL = import.meta.env.VITE_API_URL || '';
export const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000/ws/live`;

export const API_ENDPOINTS = {
  transactions: `${API_BASE_URL}/api/v1/transactions`,
  users: `${API_BASE_URL}/api/v1/users`,
  frauds: `${API_BASE_URL}/api/v1/frauds`,
  fraudStats: `${API_BASE_URL}/api/v1/frauds/stats`,
  health: `${API_BASE_URL}/api/v1/health`,
} as const;
