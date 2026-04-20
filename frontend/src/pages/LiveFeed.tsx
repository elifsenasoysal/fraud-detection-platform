import { useEffect, useState } from 'react';
import { Radio } from 'lucide-react';
import { transactionService } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import StatusBadge from '../components/common/StatusBadge';
import type { Transaction } from '../types/transaction';

export default function LiveFeed() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const { messages, isConnected } = useWebSocket();

  useEffect(() => {
    transactionService.list(1, 50).then((res) => {
      setTransactions(res.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  // Merge WebSocket messages into feed
  useEffect(() => {
    if (messages.length > 0) {
      const latest = messages[0];
      if (latest?.data) {
        const tx = latest.data as unknown as Transaction;
        setTransactions((prev) => [tx, ...prev].slice(0, 100));
      }
    }
  }, [messages]);

  const formatTime = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleTimeString('tr-TR', {
        hour: '2-digit', minute: '2-digit', second: '2-digit',
      });
    } catch {
      return '--:--:--';
    }
  };

  const formatAmount = (amount: number) =>
    new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount);

  return (
    <>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1>Canlı Akış</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 12px', borderRadius: 20, background: isConnected ? 'var(--success-bg)' : 'var(--danger-bg)' }}>
            <div className="live-dot" style={{ background: isConnected ? 'var(--success)' : 'var(--danger)' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: isConnected ? 'var(--success)' : 'var(--danger)' }}>
              {isConnected ? 'CANLI' : 'BAĞLANTI KESİLDİ'}
            </span>
          </div>
        </div>
        <p>Gelen işlemlerin durumlarına göre canlı veri akışı</p>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Yükleniyor...</div>
        ) : transactions.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            <Radio size={48} style={{ marginBottom: 12, opacity: 0.3 }} />
            <p>Henüz işlem yok. Script'lerle veri gönderebilirsiniz.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Zaman</th>
                <th>Kullanıcı</th>
                <th>Tutar</th>
                <th>Konum</th>
                <th>Durum</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx, idx) => (
                <tr
                  key={tx.id || idx}
                  className="slide-in"
                  style={{
                    animationDelay: `${idx * 0.02}s`,
                    background: tx.status === 'suspicious' ? 'var(--danger-bg)' : 'transparent',
                  }}
                >
                  <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                    {formatTime(tx.created_at)}
                  </td>
                  <td style={{ fontWeight: 600 }}>{tx.user_external_id || tx.user_id?.slice(0, 8)}</td>
                  <td className="amount" style={{ color: tx.status === 'suspicious' ? 'var(--danger)' : 'var(--text-primary)' }}>
                    {formatAmount(tx.amount)}
                  </td>
                  <td>{tx.location}</td>
                  <td><StatusBadge status={tx.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
