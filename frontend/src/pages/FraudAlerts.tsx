import { useEffect, useState } from 'react';
import { ShieldAlert, Bell } from 'lucide-react';
import { fraudService } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import RiskIndicator from '../components/common/RiskIndicator';
import type { FraudAlert } from '../types/fraud';

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [newAlertFlash, setNewAlertFlash] = useState<string | null>(null);

  // WebSocket: listen only for fraud_alert messages
  const { messages: wsAlerts, isConnected } = useWebSocket('fraud_alert');

  // Initial load from API
  useEffect(() => {
    const load = async () => {
      try {
        const res = await fraudService.list(1, 50);
        setAlerts(res.data || []);
        setTotal(res.pagination?.total_items || 0);
      } catch (err) {
        console.error('Failed to load alerts:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Merge WebSocket fraud alerts into list in real-time
  useEffect(() => {
    if (wsAlerts.length > 0) {
      const latest = wsAlerts[0];
      if (latest?.data) {
        const raw = latest.data as Record<string, unknown>;

        setAlerts((prev) => {
          // Prevent duplicates
          const alertId = (raw.alert_id || raw.id) as string;
          const exists = prev.some((a) => a.id === alertId);
          if (exists) return prev;

          // Map WebSocket alert data to FraudAlert shape
          const mapped: FraudAlert = {
            id: alertId,
            transaction_id: (raw.transaction_id as string) || '',
            user_id: (raw.user_id as string) || '',
            user_external_id: (raw.user_external_id as string) || '',
            risk_level: (raw.risk_level as FraudAlert['risk_level']) || 'high',
            violated_rules: (raw.violated_rules as string[]) || [],
            details: (raw.details as Record<string, unknown>) || {},
            amount: (raw.amount as number) || 0,
            location: (raw.location as string) || '',
            is_resolved: false,
            resolved_at: null,
            created_at: (raw.created_at as string) || new Date().toISOString(),
          };

          return [mapped, ...prev].slice(0, 100);
        });

        setTotal((prev) => prev + 1);

        // Flash effect for new alert
        const alertId = (raw.alert_id || raw.id) as string;
        setNewAlertFlash(alertId);
        setTimeout(() => setNewAlertFlash(null), 3000);
      }
    }
  }, [wsAlerts]);

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString('tr-TR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const formatAmount = (amount: number) =>
    new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount);

  const ruleLabels: Record<string, string> = {
    velocity: '⚡ Hız Aşımı',
    amount: '💰 Tutar Anomalisi',
    location: '🌍 İmkansız Seyahat',
  };

  return (
    <>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1>Fraud Uyarıları</h1>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', borderRadius: 20,
            background: isConnected ? 'var(--success-bg)' : 'var(--danger-bg)',
          }}>
            <div className="live-dot" style={{
              background: isConnected ? 'var(--success)' : 'var(--danger)',
            }} />
            <span style={{
              fontSize: '0.75rem', fontWeight: 600,
              color: isConnected ? 'var(--success)' : 'var(--danger)',
            }}>
              {isConnected ? 'CANLI' : 'BAĞLANTI KESİLDİ'}
            </span>
          </div>
        </div>
        <p>Tespit edilen şüpheli işlemler ve anomali detayları — Toplam: {total}</p>
      </div>

      {/* Real-time alert toast */}
      {newAlertFlash && (
        <div
          className="slide-in"
          style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '12px 20px', marginBottom: 16,
            background: 'linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05))',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: 'var(--radius-md)',
            animation: 'slideIn 0.3s ease-out, pulse 1s ease-in-out 0.3s 2',
          }}
        >
          <Bell size={20} style={{ color: 'var(--danger)', flexShrink: 0 }} />
          <span style={{ fontWeight: 600, color: 'var(--danger)' }}>
            🚨 Yeni fraud uyarısı tespit edildi!
          </span>
        </div>
      )}

      <div className="card">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Yükleniyor...</div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            <ShieldAlert size={48} style={{ marginBottom: 12, opacity: 0.3 }} />
            <p>Henüz fraud uyarısı tespit edilmedi.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {alerts.map((alert, idx) => {
              const alertId = alert.id || String(idx);
              const isNew = alertId === newAlertFlash;

              return (
                <div
                  key={alertId}
                  className={isNew ? 'slide-in' : 'fade-in'}
                  style={{
                    animationDelay: isNew ? '0s' : `${idx * 0.05}s`,
                    background: isNew
                      ? 'linear-gradient(135deg, rgba(239,68,68,0.1), var(--bg-elevated))'
                      : 'var(--bg-elevated)',
                    border: `1px solid ${isNew ? 'rgba(239,68,68,0.4)' : 'var(--border-color)'}`,
                    borderLeft: `4px solid ${
                      alert.risk_level === 'critical' ? 'var(--danger)' :
                      alert.risk_level === 'high' ? '#f97316' :
                      alert.risk_level === 'medium' ? 'var(--warning)' : 'var(--success)'
                    }`,
                    borderRadius: 'var(--radius-md)',
                    padding: '16px 20px',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      {isNew && <Bell size={16} style={{ color: 'var(--danger)', animation: 'pulse 1s ease-in-out 3' }} />}
                      <span style={{ fontWeight: 700 }}>{alert.user_external_id}</span>
                      <RiskIndicator level={alert.risk_level} />
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{formatDate(alert.created_at)}</span>
                  </div>

                  <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 8 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--danger)' }}>
                      {formatAmount(alert.amount)}
                    </span>
                    <span style={{ color: 'var(--text-secondary)' }}>📍 {alert.location}</span>
                  </div>

                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {alert.violated_rules.map((rule) => (
                      <span
                        key={rule}
                        style={{
                          padding: '2px 8px',
                          background: 'var(--bg-card)',
                          borderRadius: 4,
                          fontSize: '0.75rem',
                          color: 'var(--text-secondary)',
                        }}
                      >
                        {ruleLabels[rule] || rule}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
