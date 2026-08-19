import React from 'react';
import { Paperclip, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function Header({ title, activeResume, autoSend }) {
  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-color)',
      backgroundColor: 'var(--bg-sidebar)',
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <div>
        <h1 style={{ fontSize: '1.2rem', fontWeight: '700' }}>{title}</h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
          <span>Resume:</span>
          <strong style={{ color: 'var(--text-primary)' }}>{activeResume || 'Yash_Nagapure_Resume.pdf'}</strong>
        </div>

        {/* Auto Send Status */}
        {autoSend ? (
          <div className="badge badge-skipped" style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
            <ShieldCheck size={14} /> Auto-Send ON
          </div>
        ) : (
          <div className="badge badge-draft" style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
            <CheckCircle2 size={14} /> Review Mode (Safe)
          </div>
        )}
      </div>
    </header>
  );
}
