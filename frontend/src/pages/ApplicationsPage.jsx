import React, { useState } from 'react';
import { Search, Trash2, Edit3, Send, AlertTriangle } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function ApplicationsPage({ 
  applications, 
  activeFilter, 
  onReviewEdit, 
  onSend, 
  onDelete 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(activeFilter || 'ALL');

  const filteredApps = applications.filter((app) => {
    const matchesSearch = 
      (app.company_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.role || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.recipient_email || '').toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'ALL' || app.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="page-container">
      <div style={{ marginBottom: '24px' }}>
        <h1 className="page-title">Application Tracking & History</h1>
        <p className="page-subtitle">View and manage all parsed, generated, sent, and failed job applications.</p>
      </div>

      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px'
      }}>
        {/* Status Filter Tabs */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {['ALL', 'DRAFT', 'GENERATED', 'SENT', 'FAILED', 'SKIPPED'].map((st) => (
            <button
              key={st}
              className={`btn ${statusFilter === st ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setStatusFilter(st)}
              style={{ fontSize: '0.8rem', padding: '6px 14px' }}
            >
              {st === 'ALL' ? 'All Applications' : st}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', width: '280px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search company, role, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '36px', fontSize: '0.85rem' }}
          />
        </div>
      </div>

      {/* Applications Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--bg-sidebar)', borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '14px 18px' }}>Company & Role</th>
              <th style={{ padding: '14px 18px' }}>Recipient Email</th>
              <th style={{ padding: '14px 18px' }}>Status</th>
              <th style={{ padding: '14px 18px' }}>Date</th>
              <th style={{ padding: '14px 18px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredApps.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No applications match the selected filter.
                </td>
              </tr>
            ) : (
              filteredApps.map((app) => (
                <tr key={app.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.15s' }}>
                  <td style={{ padding: '14px 18px' }}>
                    <strong style={{ display: 'block', color: 'var(--text-primary)', fontSize: '0.95rem' }}>{app.company_name}</strong>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{app.role} ({app.experience || 'Fresher'})</span>
                  </td>

                  <td style={{ padding: '14px 18px' }}>
                    <span style={{ color: app.recipient_email ? 'var(--text-primary)' : '#f87171', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                      {app.recipient_email || '(Missing Email)'}
                    </span>
                  </td>

                  <td style={{ padding: '14px 18px' }}>
                    <StatusBadge status={app.status} />
                  </td>

                  <td style={{ padding: '14px 18px', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                    {app.sent_at ? new Date(app.sent_at).toLocaleDateString() : new Date(app.created_at).toLocaleDateString()}
                  </td>

                  <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                      <button
                        className="btn btn-outline"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={() => onReviewEdit(app)}
                      >
                        <Edit3 size={12} /> Review
                      </button>

                      {app.status !== 'SENT' && (
                        <button
                          className="btn btn-primary"
                          style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                          onClick={() => onSend(app)}
                          disabled={!app.recipient_email}
                        >
                          <Send size={12} /> Send
                        </button>
                      )}

                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={() => onDelete(app.id)}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
