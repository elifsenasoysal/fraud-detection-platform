import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Users, Search } from 'lucide-react';
import { userService } from '../services/api';
import RiskIndicator from '../components/common/RiskIndicator';
import type { UserSummary } from '../types/user';
import type { UserRisk } from '../types/user';

export default function UserDetail() {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserRisk | null>(null);
  const [searchId, setSearchId] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    userService.list(1, 50).then((res) => {
      setUsers(res.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const loadUserDetail = async (externalId: string) => {
    setDetailLoading(true);
    try {
      const res = await userService.risk(externalId);
      if (res.data) setSelectedUser(res.data);
    } catch {
      setSelectedUser(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchId.trim()) loadUserDetail(searchId.trim());
  };

  const formatAmount = (amount: number | null) =>
    amount != null
      ? new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount)
      : '—';

  return (
    <>
      <div className="page-header">
        <h1>Kullanıcı Analizi</h1>
        <p>Kullanıcı seçerek detaylı risk analizi ve işlem geçmişi görüntüleyin</p>
      </div>

      {/* Search */}
      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Kullanıcı ID ara (örn: user_1)"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 40px',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-family)',
                fontSize: '0.875rem',
                outline: 'none',
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary">Ara</button>
        </form>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selectedUser ? '1fr 1fr' : '1fr', gap: 20 }}>
        {/* User List */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Kullanıcılar</h3>
          </div>
          {loading ? (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Yükleniyor...</div>
          ) : users.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
              <Users size={48} style={{ marginBottom: 12, opacity: 0.3 }} />
              <p>Henüz kullanıcı yok.</p>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Risk</th>
                  <th>İşlem</th>
                  <th>Bayrak</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr
                    key={user.id}
                    onClick={() => loadUserDetail(user.external_id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ fontWeight: 600 }}>{user.external_id}</td>
                    <td><RiskIndicator level={user.risk_level} /></td>
                    <td>{user.total_transactions}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: user.total_fraud_flags > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                      {user.total_fraud_flags}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* User Detail Panel */}
        {selectedUser && (
          <div className="card fade-in">
            <div className="card-header">
              <h3 className="card-title">Kullanıcı Detayı: {selectedUser.external_id}</h3>
              <RiskIndicator level={selectedUser.risk_level} />
            </div>

            {detailLoading ? (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Yükleniyor...</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                  <div style={{ background: 'var(--bg-elevated)', padding: 16, borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Toplam İşlem</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{selectedUser.total_transactions}</div>
                  </div>
                  <div style={{ background: 'var(--bg-elevated)', padding: 16, borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Fraud Bayrak</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: selectedUser.total_fraud_flags > 0 ? 'var(--danger)' : 'var(--success)' }}>
                      {selectedUser.total_fraud_flags}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-elevated)', padding: 16, borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Fraud Oranı</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>%{selectedUser.fraud_rate}</div>
                  </div>
                  <div style={{ background: 'var(--bg-elevated)', padding: 16, borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Ort. Tutar (24s)</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                      {formatAmount(selectedUser.average_amount_24h)}
                    </div>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-elevated)', padding: 16, borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Son Konum</div>
                  <div style={{ fontWeight: 600 }}>📍 {selectedUser.last_location || '—'}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
