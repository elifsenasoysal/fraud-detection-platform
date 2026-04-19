import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  ShieldAlert,
  TrendingUp,
  Users,
  Activity,
  AlertTriangle,
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { fraudService, transactionService } from '../services/api';
import type { FraudStats } from '../types/fraud';

const PIE_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444'];

export default function Dashboard() {
  const [stats, setStats] = useState<FraudStats | null>(null);
  const [totalTx, setTotalTx] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, txRes] = await Promise.all([
          fraudService.stats(),
          transactionService.list(1, 1),
        ]);
        if (statsRes.data) setStats(statsRes.data);
        setTotalTx(txRes.pagination?.total_items || 0);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Dashboard</h1>
          <p>Yükleniyor...</p>
        </div>
      </div>
    );
  }

  const riskPieData = stats ? [
    { name: 'Düşük', value: stats.alerts_by_risk['low'] || 0 },
    { name: 'Orta', value: stats.alerts_by_risk['medium'] || 0 },
    { name: 'Yüksek', value: stats.alerts_by_risk['high'] || 0 },
    { name: 'Kritik', value: stats.alerts_by_risk['critical'] || 0 },
  ].filter(d => d.value > 0) : [];

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Gerçek zamanlı fraud tespit platformu genel görünümü</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card fade-in">
          <div className="stat-icon purple"><BarChart3 size={24} /></div>
          <div>
            <div className="stat-value">{totalTx.toLocaleString('tr-TR')}</div>
            <div className="stat-label">Toplam İşlem</div>
          </div>
        </div>
        <div className="stat-card fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="stat-icon red"><ShieldAlert size={24} /></div>
          <div>
            <div className="stat-value">{stats?.total_alerts || 0}</div>
            <div className="stat-label">Fraud Uyarısı</div>
          </div>
        </div>
        <div className="stat-card fade-in" style={{ animationDelay: '0.2s' }}>
          <div className="stat-icon yellow"><AlertTriangle size={24} /></div>
          <div>
            <div className="stat-value">{stats?.active_alerts || 0}</div>
            <div className="stat-label">Aktif Uyarı</div>
          </div>
        </div>
        <div className="stat-card fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="stat-icon green"><TrendingUp size={24} /></div>
          <div>
            <div className="stat-value">%{stats?.fraud_rate?.toFixed(1) || '0.0'}</div>
            <div className="stat-label">Fraud Oranı</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        {/* Risk Distribution Pie */}
        <div className="card fade-in">
          <div className="card-header">
            <h3 className="card-title">Risk Seviyesi Dağılımı</h3>
          </div>
          <div style={{ height: 280 }}>
            {riskPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {riskPieData.map((_entry, idx) => (
                      <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--text-primary)',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                Henüz veri yok
              </div>
            )}
          </div>
        </div>

        {/* Top Flagged Users */}
        <div className="card fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="card-header">
            <h3 className="card-title">En Çok İşaretlenen Kullanıcılar</h3>
          </div>
          {stats?.top_flagged_users && stats.top_flagged_users.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Kullanıcı</th>
                  <th>Risk</th>
                  <th>Bayrak</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_flagged_users.map((user, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>{user.external_id}</td>
                    <td><span className={`badge badge-${user.risk_level}`}>{user.risk_level}</span></td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{user.fraud_flags}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              Henüz işaretlenen kullanıcı yok
            </div>
          )}
        </div>
      </div>
    </>
  );
}
