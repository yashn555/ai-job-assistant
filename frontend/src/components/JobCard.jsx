import React from 'react';
import { 
  Building2, 
  Briefcase, 
  Mail, 
  Clock, 
  Sparkles, 
  Edit3, 
  Send, 
  FastForward, 
  MapPin, 
  Code2,
  AlertTriangle,
  Loader2
} from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function JobCard({ 
  app, 
  onReviewEdit, 
  onSend, 
  onSkip, 
  isSending
}) {
  const isMissingEmail = !app.recipient_email;
  const isSent = app.status === 'SENT';
  const isSkipped = app.status === 'SKIPPED';

  return (
    <div className="card" style={{
      backgroundColor: 'var(--bg-card)',
      border: isMissingEmail ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid var(--border-color)',
      borderRadius: '12px',
      marginBottom: '16px',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      boxShadow: 'var(--shadow-sm)'
    }}>
      {/* Header Row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Building2 size={18} color="#6366f1" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: 'var(--text-primary)' }}>
              {app.company_name}
            </h3>
            {app.location && (
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <MapPin size={12} /> {app.location}
              </span>
            )}
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Briefcase size={14} color="#94a3b8" /> <strong>Role:</strong> {app.role}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={14} color="#94a3b8" /> <strong>Exp:</strong> {app.experience || 'Fresher'}
            </span>
          </div>
        </div>

        <div>
          <StatusBadge status={app.status} />
        </div>
      </div>

      {/* Email & Details */}
      <div style={{
        padding: '12px 14px',
        backgroundColor: 'var(--bg-app)',
        borderRadius: '8px',
        border: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        fontSize: '0.88rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: isMissingEmail ? '#f87171' : 'var(--text-primary)' }}>
            <Mail size={15} color={isMissingEmail ? '#f87171' : '#60a5fa'} />
            <strong>Recipient Email:</strong> {app.recipient_email || '(No email detected - edit required)'}
          </span>
          {isMissingEmail && (
            <span style={{ fontSize: '0.75rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertTriangle size={12} /> Missing Recipient
            </span>
          )}
        </div>

        {app.skills && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            <Code2 size={13} />
            <span>Skills: {app.skills}</span>
          </div>
        )}

        {app.error_message && (
          <div style={{ color: '#f87171', fontSize: '0.82rem', marginTop: '4px', fontWeight: '500' }}>
            Error: {app.error_message}
          </div>
        )}
      </div>

      {/* Direct Actions */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '8px',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="btn btn-outline"
            onClick={() => onReviewEdit(app)}
            style={{ fontSize: '0.85rem' }}
          >
            <Edit3 size={14} /> Review & Edit Email
          </button>

          {!isSent && !isSkipped && (
            <button
              className="btn btn-outline"
              onClick={() => onSkip(app)}
              style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}
            >
              <FastForward size={14} /> Skip
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {!isSent ? (
            <button
              className="btn btn-primary"
              onClick={() => onSend(app)}
              disabled={isMissingEmail || isSending}
              style={{ fontSize: '0.88rem' }}
            >
              {isSending ? (
                <>
                  <Loader2 size={14} className="animate-pulse" /> Sending...
                </>
              ) : (
                <>
                  <Send size={14} /> Send Application
                </>
              )}
            </button>
          ) : (
            <button
              className="btn btn-success"
              disabled
              style={{ fontSize: '0.88rem' }}
            >
              Application Sent ✓
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
