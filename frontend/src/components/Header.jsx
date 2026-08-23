import React from 'react';
import { Paperclip, CheckCircle2, ShieldCheck, Menu, LogOut, User as UserIcon } from 'lucide-react';

export default function Header({ title, activeResume, autoSend, user, onLogout, onToggleMobileMenu }) {
  return (
    <header className="app-header" style={{
      minHeight: '64px',
      borderBottom: '1px solid var(--border-color)',
      backgroundColor: 'var(--bg-sidebar)',
      padding: '0 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Mobile Hamburger Toggle */}
        <button
          className="mobile-menu-btn"
          onClick={onToggleMobileMenu}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '6px',
            display: 'none' // Controlled by CSS media query
          }}
          title="Toggle Navigation Menu"
        >
          <Menu size={24} />
        </button>

        <h1 style={{ fontSize: '1.15rem', fontWeight: '700' }}>{title}</h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* Active Resume Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          backgroundColor: 'var(--bg-app)',
          border: '1px solid var(--border-color)',
          borderRadius: '20px',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)'
        }}>
          <Paperclip size={14} color="#6366f1" />
          <span className="hide-on-mobile">Resume:</span>
          <strong style={{ color: 'var(--text-primary)', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeResume || 'Default Resume'}
          </strong>
        </div>

        {/* User Account / Logout */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '0.8rem',
              color: 'var(--accent-primary)',
              fontWeight: '600'
            }}>
              <UserIcon size={14} />
              <span className="hide-on-mobile">{user.name}</span>
            </div>

            <button
              onClick={onLogout}
              className="btn btn-outline"
              style={{ padding: '6px 10px', fontSize: '0.8rem' }}
              title="Log Out"
            >
              <LogOut size={14} />
              <span className="hide-on-mobile">Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

