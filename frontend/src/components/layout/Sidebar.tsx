import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  Users,
  Activity,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/live', label: 'Canlı Akış', icon: Radio },
  { path: '/alerts', label: 'Fraud Uyarıları', icon: ShieldAlert },
  { path: '/users', label: 'Kullanıcılar', icon: Users },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Activity size={24} />
        </div>
        <div>
          <h2>FDP</h2>
          <span>Fraud Detection</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={`sidebar-link ${
              location.pathname === item.path ? 'active' : ''
            }`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <div className="live-dot" />
          <span>Sistem Aktif</span>
        </div>
      </div>

      <style>{`
        .sidebar {
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
          width: var(--sidebar-width);
          background: var(--bg-secondary);
          border-right: 1px solid var(--border-color);
          display: flex;
          flex-direction: column;
          z-index: 100;
          padding: 0;
        }

        .sidebar-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 20px 24px;
          border-bottom: 1px solid var(--border-color);
        }

        .sidebar-logo {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .sidebar-brand h2 {
          font-size: 1.1rem;
          font-weight: 800;
          letter-spacing: -0.02em;
          line-height: 1.2;
        }

        .sidebar-brand span {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }

        .sidebar-nav {
          flex: 1;
          padding: 16px 12px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .sidebar-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 16px;
          border-radius: var(--radius-sm);
          color: var(--text-secondary);
          font-size: 0.875rem;
          font-weight: 500;
          transition: all var(--transition-fast);
          text-decoration: none;
        }

        .sidebar-link:hover {
          color: var(--text-primary);
          background: var(--bg-card-hover);
        }

        .sidebar-link.active {
          color: white;
          background: var(--accent-primary);
          box-shadow: 0 2px 8px var(--accent-primary-glow);
        }

        .sidebar-footer {
          padding: 16px 24px;
          border-top: 1px solid var(--border-color);
        }

        .sidebar-status {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.8rem;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .sidebar {
            display: none;
          }
        }
      `}</style>
    </aside>
  );
}
