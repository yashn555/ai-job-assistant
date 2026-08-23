import React, { useState } from 'react';
import { LogIn, UserPlus, KeyRound, Mail, Lock, User as UserIcon, HelpCircle, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function AuthModal({ isOpen, onAuthSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    app_password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAppPasswordHelp, setShowAppPasswordHelp] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'login') {
        const data = await window.api.login(formData.email, formData.password);
        onAuthSuccess(data.user);
      } else {
        if (!formData.name.trim()) {
          throw new Error('Full Name is required for registration.');
        }
        if (!formData.email.trim() || !formData.email.includes('@')) {
          throw new Error('Valid email address is required.');
        }
        if (formData.password.length < 4) {
          throw new Error('Password must be at least 4 characters long.');
        }

        const data = await window.api.signup({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          app_password: formData.app_password
        });
        onAuthSuccess(data.user);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 9999 }}>
      <div className="modal-content" style={{ maxWidth: '440px', padding: '0', borderRadius: '16px', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
        
        {/* Header Banner */}
        <div style={{
          backgroundColor: 'var(--bg-sidebar)',
          padding: '24px',
          borderBottom: '1px solid var(--border-color)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            backgroundColor: 'var(--accent-primary)',
            color: 'white',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
          }}>
            {mode === 'login' ? <LogIn size={26} /> : <UserPlus size={26} />}
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {mode === 'login'
              ? 'Log in to manage your AI job applications'
              : 'Sign up to automate job applications with personalized AI'}
          </p>
        </div>

        {/* Tab Selector */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-app)'
        }}>
          <button
            type="button"
            onClick={() => { setMode('login'); setError(''); }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              backgroundColor: mode === 'login' ? 'var(--bg-card)' : 'transparent',
              color: mode === 'login' ? 'var(--accent-primary)' : 'var(--text-muted)',
              fontWeight: '600',
              cursor: 'pointer',
              borderBottom: mode === 'login' ? '2px solid var(--accent-primary)' : 'none',
              fontSize: '0.9rem'
            }}
          >
            Log In
          </button>
          <button
            type="button"
            onClick={() => { setMode('signup'); setError(''); }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              backgroundColor: mode === 'signup' ? 'var(--bg-card)' : 'transparent',
              color: mode === 'signup' ? 'var(--accent-primary)' : 'var(--text-muted)',
              fontWeight: '600',
              cursor: 'pointer',
              borderBottom: mode === 'signup' ? '2px solid var(--accent-primary)' : 'none',
              fontSize: '0.9rem'
            }}
          >
            Sign Up
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: '24px', backgroundColor: 'var(--bg-card)' }}>
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              marginBottom: '16px'
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {mode === 'signup' && (
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <UserIcon size={14} color="var(--accent-primary)" /> Full Name *
              </label>
              <input
                type="text"
                name="name"
                required
                placeholder="e.g. Yash Nagapure"
                value={formData.name}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Mail size={14} color="var(--accent-primary)" /> Email Address *
            </label>
            <input
              type="email"
              name="email"
              required
              placeholder="e.g. yashnagapure25@gmail.com"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lock size={14} color="var(--accent-primary)" /> Password *
            </label>
            <input
              type="password"
              name="password"
              required
              placeholder="Enter account password"
              value={formData.password}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          {mode === 'signup' && (
            <div className="form-group" style={{ marginTop: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', margin: 0 }}>
                  <KeyRound size={14} color="#f59e0b" /> Gmail App Password (Optional)
                </label>
                <button
                  type="button"
                  onClick={() => setShowAppPasswordHelp(!showAppPasswordHelp)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--accent-primary)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <HelpCircle size={14} /> What is this?
                </button>
              </div>
              <input
                type="password"
                name="app_password"
                placeholder="16-character Gmail App Password (e.g. awmtyyfozljwmbvu)"
                value={formData.app_password}
                onChange={handleChange}
                className="form-input"
              />

              {showAppPasswordHelp && (
                <div style={{
                  marginTop: '8px',
                  padding: '10px 12px',
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '8px',
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                  lineHeight: '1.4'
                }}>
                  <strong style={{ color: 'var(--text-primary)' }}>How to get Gmail App Password:</strong>
                  <ol style={{ paddingLeft: '16px', marginTop: '4px' }}>
                    <li>Enable 2-Step Verification on your Google Account.</li>
                    <li>Go to Google Account &gt; Security &gt; App Passwords.</li>
                    <li>Generate a password for "Mail" and paste the 16 letters here.</li>
                  </ol>
                </div>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '0.95rem',
              fontWeight: '600',
              marginTop: '12px',
              borderRadius: '8px'
            }}
          >
            {loading ? 'Processing...' : (mode === 'login' ? 'Log In' : 'Sign Up')}
          </button>
        </form>

      </div>
    </div>
  );
}
