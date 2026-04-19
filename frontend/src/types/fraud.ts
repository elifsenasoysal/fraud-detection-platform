export interface FraudAlert {
  id: string;
  transaction_id: string;
  user_id: string;
  user_external_id: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  violated_rules: string[];
  details: Record<string, unknown>;
  amount: number;
  location: string;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface FraudStats {
  total_alerts: number;
  active_alerts: number;
  resolved_alerts: number;
  fraud_rate: number;
  alerts_by_risk: Record<string, number>;
  alerts_by_rule: Record<string, number>;
  top_flagged_users: Array<{
    external_id: string;
    fraud_flags: number;
    risk_level: string;
  }>;
}
