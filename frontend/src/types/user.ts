export interface UserRisk {
  user_id: string;
  external_id: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  total_transactions: number;
  total_fraud_flags: number;
  fraud_rate: number;
  recent_transactions_count: number;
  average_amount_24h: number | null;
  last_transaction_at: string | null;
  last_location: string | null;
}

export interface UserHistory {
  user_id: string;
  external_id: string;
  total_transactions: number;
  total_amount: number;
  average_amount: number;
  risk_level: string;
  transactions: Array<{
    id: string;
    amount: number;
    currency: string;
    location: string;
    status: string;
    created_at: string;
  }>;
  fraud_alerts: Array<{
    id: string;
    transaction_id: string;
    risk_level: string;
    violated_rules: string[];
    is_resolved: boolean;
    created_at: string;
  }>;
}

export interface UserSummary {
  id: string;
  external_id: string;
  risk_level: string;
  total_transactions: number;
  total_fraud_flags: number;
  created_at: string;
}
