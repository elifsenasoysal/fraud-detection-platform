import { useEffect, useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import { fraudService } from '../services/api';
import RiskIndicator from '../components/common/RiskIndicator';
import type { FraudAlert } from '../types/fraud';

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

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
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, []);

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
        <h1>Fraud Uyarıları</h1>
        <p>Tespit edilen şüpheli işlemler ve anomali detayları — Toplam: {total}</p>
      </div>

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
            {alerts.map((alert, idx) => (
              <div
                key={alert.id || idx}
                className="fade-in"
                style={{
                  animationDelay: `${idx * 0.05}s`,
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-color)',
                  borderLeft: `4px solid ${
                    alert.risk_level === 'critical' ? 'var(--danger)' :
                    alert.risk_level === 'high' ? '#f97316' :
                    alert.risk_level === 'medium' ? 'var(--warning)' : 'var(--success)'
                  }`,
                  borderRadius: 'var(--radius-md)',
                  padding: '16px 20px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
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
            ))}
          </div>
        )}
      </div>
    </>
  );
}
