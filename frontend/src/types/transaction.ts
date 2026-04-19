export interface Transaction {
  id: string;
  user_id: string;
  user_external_id?: string;
  amount: number;
  currency: string;
  location: string;
  status: 'approved' | 'suspicious' | 'rejected';
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface TransactionCreate {
  user_id: string;
  amount: number;
  currency?: string;
  location: string;
  metadata?: Record<string, unknown>;
}
