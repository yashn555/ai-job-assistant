import React from 'react';
import { 
  LayoutDashboard, 
  FilePlus, 
  Briefcase, 
  Send, 
  AlertCircle, 
  Settings, 
  Sparkles,
  Bot
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, counts }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, count: null },
    { id: 'new', label: 'New Applications', icon: FilePlus, count: null },
    { id: 'parsed', label: 'Parsed Jobs', icon: Briefcase, count: counts.parsed || 0 },
    { id: 'sent', label: 'Sent Applications', icon: Send, count: counts.sent || 0, badgeColor: 'badge-sent' },
    { id: 'failed', label: 'Failed Applications', icon: AlertCircle, count: counts.failed || 0, badgeColor: 'badge-failed' },
    { id: 'settings', label: 'Settings', icon: Settings, count: null },
  ];

  return (
    <aside style={{
      width: '260px',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh'
    }}>
      {/* Brand Logo Header */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          backgroundColor: 'var(--accent-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
        }}>
          <Bot size={22} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: '700', lineHeight: 1.2 }}>AI Job Assistant</h2>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Sparkles size={12} color="#6366f1" /> Nemotron Engine
          </span>
        </div>
      </div>

      {/* Nav Menu Items */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <ul style={{ listStyle: 'none' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id} style={{ marginBottom: '4px' }}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: isActive ? 'var(--accent-light)' : 'transparent',
                    color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    fontWeight: isActive ? '600' : '500',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </div>

                  {item.count !== null && item.count > 0 && (
                    <span className={`badge ${item.badgeColor || 'badge-draft'}`} style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                      {item.count}
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Candidate Footer Badge */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border-color)',
        backgroundColor: 'rgba(15, 23, 42, 0.4)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: '#334155',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.85rem',
          fontWeight: '700',
          color: 'var(--text-primary)'
        }}>
          YN
        </div>
        <div style={{ overflow: 'hidden' }}>
          <p style={{ fontSize: '0.82rem', fontWeight: '600', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            Yash Nagapure
          </p>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            B.Tech CSE '27
          </p>
        </div>
      </div>
    </aside>
  );
}
