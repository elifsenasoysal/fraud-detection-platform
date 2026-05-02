import { useEffect, useState } from 'react';
import {
  BarChart3,
  ShieldAlert,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  BarChart, Bar,
} from 'recharts';
import { fraudService, transactionService } from '../services/api';
import type { FraudStats, FraudTrendPoint } from '../types/fraud';

const PIE_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444'];

const CHART_TOOLTIP_STYLE = {
  background: 'var(--bg-card)',
  border: '1px solid var(--border-color)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text-primary)',
};

export default function Dashboard() {
  const [stats, setStats] = useState<FraudStats | null>(null);
  const [totalTx, setTotalTx] = useState(0);
  const [trendData, setTrendData] = useState<FraudTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, txRes, trendRes] = await Promise.all([
          fraudService.stats(),
          transactionService.list(1, 1),
          fraudService.trend(14),
        ]);
        if (statsRes.data) setStats(statsRes.data);
        setTotalTx(txRes.pagination?.total_items || 0);
        if (trendRes.data) setTrendData(trendRes.data);
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

  // Format date labels for chart (e.g., "02 May")
  const formattedTrendData = trendData.map((point) => ({
    ...point,
    label: new Date(point.date).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: 'short',
    }),
  }));

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

      {/* Fraud Trend Chart — Full Width */}
      <div className="card fade-in" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <h3 className="card-title">📈 Fraud Oranı Trendi (Son 14 Gün)</h3>
        </div>
        <div style={{ height: 300 }}>
          {formattedTrendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={formattedTrendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradientFraudRate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis
                  dataKey="label"
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tickLine={false}
                  unit="%"
                />
                <Tooltip
                  contentStyle={CHART_TOOLTIP_STYLE}
                  formatter={(value: number) => [`%${value.toFixed(2)}`, 'Fraud Oranı']}
                  labelFormatter={(label) => `Tarih: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="fraud_rate"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#gradientFraudRate)"
                  dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
              Henüz trend verisi yok
            </div>
          )}
        </div>
      </div>

      {/* Fraud Count & Transaction Count Bar Chart — Full Width */}
      <div className="card fade-in" style={{ animationDelay: '0.1s', marginBottom: 20 }}>
        <div className="card-header">
          <h3 className="card-title">📊 Günlük İşlem ve Fraud Sayısı (Son 14 Gün)</h3>
        </div>
        <div style={{ height: 280 }}>
          {formattedTrendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={formattedTrendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis
                  dataKey="label"
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={CHART_TOOLTIP_STYLE}
                  formatter={(value: number, name: string) => [
                    value,
                    name === 'transaction_count' ? 'İşlem Sayısı' : 'Fraud Sayısı',
                  ]}
                  labelFormatter={(label) => `Tarih: ${label}`}
                />
                <Legend
                  formatter={(value) =>
                    value === 'transaction_count' ? 'İşlem Sayısı' : 'Fraud Sayısı'
                  }
                  wrapperStyle={{ color: 'var(--text-secondary)' }}
                />
                <Bar dataKey="transaction_count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fraud_count" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
              Henüz veri yok
            </div>
          )}
        </div>
      </div>

      {/* Charts Row — Pie + Top Users */}
      <div className="chart-grid">
        {/* Risk Distribution Pie */}
        <div className="card fade-in" style={{ animationDelay: '0.2s' }}>
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
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
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
        <div className="card fade-in" style={{ animationDelay: '0.3s' }}>
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
