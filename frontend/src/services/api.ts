import { API_ENDPOINTS } from '../config/api';
import type { APIResponse, PaginatedResponse } from '../types/api';
import type { Transaction } from '../types/transaction';
import type { FraudAlert, FraudStats } from '../types/fraud';
import type { UserRisk, UserHistory, UserSummary } from '../types/user';

async function fetchJSON<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export const transactionService = {
  list: (page = 1, pageSize = 20) =>
    fetchJSON<PaginatedResponse<Transaction>>(`${API_ENDPOINTS.transactions}?page=${page}&page_size=${pageSize}`),

  create: async (data: { user_id: string; amount: number; location: string }) => {
    const res = await fetch(API_ENDPOINTS.transactions, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
};

export const fraudService = {
  list: (page = 1, pageSize = 20) =>
    fetchJSON<PaginatedResponse<FraudAlert>>(`${API_ENDPOINTS.frauds}?page=${page}&page_size=${pageSize}`),

  stats: () =>
    fetchJSON<APIResponse<FraudStats>>(API_ENDPOINTS.fraudStats),
};

export const userService = {
  list: (page = 1, pageSize = 20) =>
    fetchJSON<PaginatedResponse<UserSummary>>(`${API_ENDPOINTS.users}?page=${page}&page_size=${pageSize}`),

  risk: (userId: string) =>
    fetchJSON<APIResponse<UserRisk>>(`${API_ENDPOINTS.users}/${userId}/risk`),

  history: (userId: string, page = 1) =>
    fetchJSON<APIResponse<UserHistory>>(`${API_ENDPOINTS.users}/${userId}/history?page=${page}`),
};
