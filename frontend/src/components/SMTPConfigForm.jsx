import React, { useState, useEffect } from 'react';
import { Mail, Server, Lock, Send, ShieldAlert, Check, Loader2 } from 'lucide-react';

export default function SMTPConfigForm({ appSettings, onSaveSettings, onTestEmail }) {
  const [smtpHost, setSmtpHost] = useState(appSettings?.smtp_host || 'smtp.gmail.com');
  const [smtpPort, setSmtpPort] = useState(appSettings?.smtp_port || 587);
  const [smtpUsername, setSmtpUsername] = useState(appSettings?.smtp_username || '');
  const [smtpPassword, setSmtpPassword] = useState(appSettings?.smtp_password || '');
  const [senderEmail, setSenderEmail] = useState(appSettings?.sender_email || '');
  const [autoSend, setAutoSend] = useState(appSettings?.auto_send || false);

  const [testRecipient, setTestRecipient] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testStatusMsg, setTestStatusMsg] = useState(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (appSettings) {
      setSmtpHost(appSettings.smtp_host || 'smtp.gmail.com');
      setSmtpPort(appSettings.smtp_port || 587);
      setSmtpUsername(appSettings.smtp_username || '');
      setSmtpPassword(appSettings.smtp_password || '');
      setSenderEmail(appSettings.sender_email || '');
      setAutoSend(appSettings.auto_send || false);
    }
  }, [appSettings]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings({
      smtp_host: smtpHost,
      smtp_port: parseInt(smtpPort, 10),
      smtp_username: smtpUsername,
      smtp_password: smtpPassword,
      sender_email: senderEmail || smtpUsername,
      auto_send: autoSend,
      active_resume: appSettings?.active_resume
    });
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleRunTest = async () => {
    if (!testRecipient) return;
    setIsTesting(true);
    setTestStatusMsg(null);
    try {
      const res = await onTestEmail(testRecipient);
      setTestStatusMsg({ type: 'success', text: res.message });
    } catch (err) {
      setTestStatusMsg({ type: 'error', text: err.message });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Server size={18} color="#6366f1" /> SMTP Email Credentials & Delivery Settings
        </h3>
        {savedSuccess && (
          <span style={{ fontSize: '0.82rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
            <Check size={14} /> Settings Saved!
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
          <div className="form-group">
            <label className="form-label">SMTP Host Server</label>
            <input
              type="text"
              className="form-input"
              value={smtpHost}
              onChange={(e) => setSmtpHost(e.target.value)}
              placeholder="smtp.gmail.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">SMTP Port</label>
            <input
              type="number"
              className="form-input"
              value={smtpPort}
              onChange={(e) => setSmtpPort(e.target.value)}
              placeholder="587"
              required
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="form-group">
            <label className="form-label">SMTP Username / Email</label>
            <input
              type="email"
              className="form-input"
              value={smtpUsername}
              onChange={(e) => setSmtpUsername(e.target.value)}
              placeholder="yourname@gmail.com"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Lock size={13} style={{ display: 'inline', marginRight: '4px' }} /> SMTP Password / App Password
            </label>
            <input
              type="password"
              className="form-input"
              value={smtpPassword}
              onChange={(e) => setSmtpPassword(e.target.value)}
              placeholder="••••••••••••••••"
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Sender Email Address</label>
          <input
            type="email"
            className="form-input"
            value={senderEmail}
            onChange={(e) => setSenderEmail(e.target.value)}
            placeholder="yourname@gmail.com (defaults to SMTP username if empty)"
          />
        </div>

        {/* Auto Send Toggle Section (Rule 12) */}
        <div style={{
          padding: '16px',
          backgroundColor: autoSend ? 'rgba(234, 179, 8, 0.1)' : 'var(--bg-app)',
          border: autoSend ? '1px solid rgba(234, 179, 8, 0.4)' : '1px solid var(--border-color)',
          borderRadius: '10px',
          marginBottom: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldAlert size={20} color={autoSend ? '#facc15' : '#94a3b8'} />
              <div>
                <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>Automatic Application Send</strong>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  Default is OFF. Requires manual user review before sending each email.
                </p>
              </div>
            </div>

            <label style={{ position: 'relative', display: 'inline-block', width: '48px', height: '24px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={autoSend}
                onChange={(e) => setAutoSend(e.target.checked)}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: autoSend ? 'var(--accent-primary)' : '#475569',
                borderRadius: '24px',
                transition: '0.2s'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '""',
                  height: '18px',
                  width: '18px',
                  left: autoSend ? '26px' : '3px',
                  bottom: '3px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  transition: '0.2s'
                }} />
              </span>
            </label>
          </div>

          {autoSend && (
            <div style={{ fontSize: '0.8rem', color: '#facc15', backgroundColor: 'rgba(234, 179, 8, 0.15)', padding: '8px 12px', borderRadius: '6px' }}>
              <strong>⚠️ Warning:</strong> With Auto Send enabled, the system will automatically transmit personalized application emails after successful job parsing without holding for manual approval.
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '24px' }}>
          <button type="submit" className="btn btn-primary">
            <Save size={16} /> Save SMTP Credentials
          </button>
        </div>
      </form>

      {/* Test Email Utility */}
      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: '10px' }}>Test SMTP Connection</h4>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="email"
            className="form-input"
            placeholder="Enter test recipient email..."
            value={testRecipient}
            onChange={(e) => setTestRecipient(e.target.value)}
            style={{ flex: 1 }}
          />
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleRunTest}
            disabled={!testRecipient || isTesting}
          >
            {isTesting ? <Loader2 size={16} className="animate-pulse" /> : <Send size={16} />}
            Send Test Email
          </button>
        </div>

        {testStatusMsg && (
          <div style={{
            marginTop: '12px',
            padding: '10px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            backgroundColor: testStatusMsg.type === 'success' ? 'var(--status-sent-bg)' : 'var(--status-failed-bg)',
            color: testStatusMsg.type === 'success' ? 'var(--status-sent-text)' : 'var(--status-failed-text)',
            border: testStatusMsg.type === 'success' ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)'
          }}>
            {testStatusMsg.text}
          </div>
        )}
      </div>
    </div>
  );
}
