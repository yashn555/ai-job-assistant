import React, { useState, useEffect } from 'react';
import { 
  X, 
  Paperclip, 
  Send, 
  RefreshCw, 
  Save, 
  Building2, 
  Briefcase, 
  Mail, 
  FileText,
  Loader2,
  Sparkles
} from 'lucide-react';

export default function EmailPreviewModal({ 
  isOpen, 
  app, 
  onClose, 
  onSave, 
  onRegenerate, 
  onSend, 
  isRegenerating,
  isSending,
  sendingIds
}) {
  if (!isOpen || !app) return null;

  const isCurrentlySending = isSending || (Array.isArray(sendingIds) && app ? sendingIds.includes(app.id) : false);

  const defaultTemplateBody = `Dear Hiring Team,\n\nI am writing to apply for the position of ${app?.role || 'Software Engineer'} at ${app?.company_name || 'your company'}.\n\nI bring a strong background in software development and technical problem solving. I am eager to contribute my technical capabilities and dedication to your engineering team.\n\nPlease find my resume attached for your consideration. I would welcome the opportunity to discuss how my background aligns with your team's goals.\n\nThank you for your time and consideration.\n\nBest regards,\nCandidate`;


  const [companyName, setCompanyName] = useState(app.company_name || '');
  const [role, setRole] = useState(app.role || '');
  const [recipientEmail, setRecipientEmail] = useState(app.recipient_email || '');
  const [subject, setSubject] = useState(app.generated_subject || app.explicit_subject || `Application for ${app.role || 'Software Engineer'}`);
  const [body, setBody] = useState(app.generated_email || defaultTemplateBody);

  useEffect(() => {
    setCompanyName(app.company_name || '');
    setRole(app.role || '');
    setRecipientEmail(app.recipient_email || '');
    setSubject(app.generated_subject || app.explicit_subject || `Application for ${app.role || 'Software Engineer'}`);
    setBody(app.generated_email || defaultTemplateBody);
  }, [app]);

  const handleSave = () => {
    onSave(app.id, {
      company_name: companyName,
      role,
      recipient_email: recipientEmail,
      generated_subject: subject,
      generated_email: body,
      status: 'REVIEWED'
    });
  };

  const handleSendSubmit = () => {
    const payload = {
      company_name: companyName,
      role,
      recipient_email: recipientEmail,
      generated_subject: subject,
      generated_email: body,
      status: 'REVIEWED'
    };
    onSave(app.id, payload);
    onSend(app.id, payload);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ position: 'relative' }}>
        {/* Loading Spinner Overlay when AI is Generating */}
        {isRegenerating && (
          <div style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.85)',
            zIndex: 100,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            borderRadius: '16px'
          }}>
            <Loader2 size={36} color="var(--accent-primary)" className="animate-spin" />
            <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="#f59e0b" /> AI is Crafting Personalized Email...
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Analyzing job requirements and matching skills...
            </p>
          </div>
        )}

        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={22} color="#6366f1" />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>Review & Edit Email Application</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {companyName} — {role}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Metadata Form Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label className="form-label">
                <Building2 size={13} style={{ display: 'inline', marginRight: '4px' }} /> Company Name
              </label>
              <input
                type="text"
                className="form-input"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </div>

            <div>
              <label className="form-label">
                <Briefcase size={13} style={{ display: 'inline', marginRight: '4px' }} /> Target Role
              </label>
              <input
                type="text"
                className="form-input"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              />
            </div>
          </div>

          {/* Recipient Email & Attachment Indicator */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label className="form-label">
                <Mail size={13} style={{ display: 'inline', marginRight: '4px' }} /> Recipient Email
              </label>
              <input
                type="email"
                className="form-input"
                placeholder="hr@company.com"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                style={{ borderColor: !recipientEmail ? '#f87171' : 'var(--border-color)' }}
              />
            </div>

            <div>
              <label className="form-label">
                <Paperclip size={13} style={{ display: 'inline', marginRight: '4px' }} /> Attached Resume
              </label>
              <div style={{
                padding: '10px 12px',
                backgroundColor: 'var(--bg-app)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                fontSize: '0.82rem',
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                <Paperclip size={14} color="#6366f1" />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {app.resume_filename || 'Active Resume Attached'}
                </span>
              </div>
            </div>
          </div>

          {/* Email Subject Input */}
          <div className="form-group">
            <label className="form-label">
              Email Subject Line {app.explicit_subject && <span style={{ color: '#60a5fa', fontWeight: '400' }}>(Explicit from job post)</span>}
            </label>
            <input
              type="text"
              className="form-input"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              style={{ fontWeight: '600', color: '#60a5fa' }}
            />
          </div>

          {/* Editable Email Body */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              Personalized Email Body
            </label>
            <textarea
              className="form-textarea"
              rows={12}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              style={{ fontFamily: 'inherit', fontSize: '0.9rem', lineHeight: '1.6' }}
            />
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button 
            type="button" 
            className="btn btn-outline" 
            onClick={onClose}
          >
            Cancel
          </button>

          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() => onRegenerate(app.id)}
            disabled={isRegenerating}
          >
            {isRegenerating ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
            Regenerate Email
          </button>

          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={handleSave}
          >
            <Save size={14} /> Save Draft
          </button>

          <button 
            type="button" 
            className="btn btn-primary" 
            onClick={handleSendSubmit} 
            disabled={!recipientEmail || isCurrentlySending}
          >
            {isCurrentlySending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            Send Application
          </button>

        </div>
      </div>
    </div>
  );
}
