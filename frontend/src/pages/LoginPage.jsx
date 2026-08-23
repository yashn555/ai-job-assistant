import React, { useState } from 'react';
import { LogIn, UserPlus, KeyRound, Mail, Lock, User as UserIcon, HelpCircle, AlertCircle, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';

export default function LoginPage({ onAuthSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    app_password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [showAppPasswordHelp, setShowAppPasswordHelp] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
    setSuccessMsg('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      if (mode === 'login') {
        if (!formData.email.trim() || !formData.password) {
          throw new Error('Please enter both email and password.');
        }
        const data = await window.api.login(formData.email, formData.password);
        setSuccessMsg('Login successful! Redirecting...');
        setTimeout(() => {
          onAuthSuccess(data.user);
        }, 400);
      } else {
        if (!formData.name.trim()) {
          throw new Error('Full Name is required for registration.');
        }
        if (!formData.email.trim() || !formData.email.includes('@')) {
          throw new Error('Please enter a valid email address.');
        }
        if (!formData.password || formData.password.length < 4) {
          throw new Error('Password must be at least 4 characters long.');
        }

        const data = await window.api.signup({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          app_password: formData.app_password
        });
        setSuccessMsg('Account created successfully! Redirecting...');
        setTimeout(() => {
          onAuthSuccess(data.user);
        }, 400);
      }
    } catch (err) {
      const msg = err.message || 'Authentication failed.';
      if (msg.includes('already exists')) {
        setError('An account with this email already exists. Please switch to the Log In tab.');
      } else if (msg.includes('Invalid email or password')) {
        setError('Invalid email or password. If you are new, please switch to the Sign Up tab.');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--bg-app)',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Subtle Background Glows */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        left: '20%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-10%',
        right: '20%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none'
      }} />

      <div style={{
        width: '100%',
        maxWidth: '460px',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '20px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
        overflow: 'hidden',
        zIndex: 10
      }}>
        {/* Top Branding Banner */}
        <div style={{
          padding: '32px 28px 24px 28px',
          textAlign: 'center',
          backgroundColor: 'var(--bg-sidebar)',
          borderBottom: '1px solid var(--border-color)'
        }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            backgroundColor: 'var(--accent-primary)',
            color: 'white',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
          }}>
            <Sparkles size={30} />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
            AI Job Assistant
          </h1>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            {mode === 'login'
              ? 'Log in to manage & automate your job applications'
              : 'Create your account to start automated AI job applications'}
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
            onClick={() => { setMode('login'); setError(''); setSuccessMsg(''); }}
            style={{
              flex: 1,
              padding: '14px',
              border: 'none',
              backgroundColor: mode === 'login' ? 'var(--bg-card)' : 'transparent',
              color: mode === 'login' ? 'var(--accent-primary)' : 'var(--text-muted)',
              fontWeight: '700',
              cursor: 'pointer',
              borderBottom: mode === 'login' ? '3px solid var(--accent-primary)' : 'none',
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <LogIn size={18} /> Log In
          </button>
          <button
            type="button"
            onClick={() => { setMode('signup'); setError(''); setSuccessMsg(''); }}
            style={{
              flex: 1,
              padding: '14px',
              border: 'none',
              backgroundColor: mode === 'signup' ? 'var(--bg-card)' : 'transparent',
              color: mode === 'signup' ? 'var(--accent-primary)' : 'var(--text-muted)',
              fontWeight: '700',
              cursor: 'pointer',
              borderBottom: mode === 'signup' ? '3px solid var(--accent-primary)' : 'none',
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <UserPlus size={18} /> Sign Up
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: '28px 28px 32px 28px' }}>
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '12px 14px',
              borderRadius: '10px',
              fontSize: '0.88rem',
              marginBottom: '20px',
              lineHeight: '1.4'
            }}>
              <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>{error}</div>
            </div>
          )}

          {successMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              backgroundColor: 'rgba(34, 197, 94, 0.15)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              color: '#4ade80',
              padding: '12px 14px',
              borderRadius: '10px',
              fontSize: '0.88rem',
              marginBottom: '20px'
            }}>
              <CheckCircle2 size={20} style={{ flexShrink: 0 }} />
              <div>{successMsg}</div>
            </div>
          )}

          {mode === 'signup' && (
            <div className="form-group" style={{ marginBottom: '18px' }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <UserIcon size={15} color="var(--accent-primary)" /> Full Name *
              </label>
              <input
                type="text"
                name="name"
                required
                placeholder="e.g. Yash Nagapure"
                value={formData.name}
                onChange={handleChange}
                className="form-input"
                style={{ padding: '12px 14px', fontSize: '0.95rem' }}
              />
            </div>
          )}

          <div className="form-group" style={{ marginBottom: '18px' }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Mail size={15} color="var(--accent-primary)" /> Email Address *
            </label>
            <input
              type="email"
              name="email"
              required
              placeholder="e.g. yashnagapure25@gmail.com"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              style={{ padding: '12px 14px', fontSize: '0.95rem' }}
            />
          </div>

          <div className="form-group" style={{ marginBottom: mode === 'signup' ? '18px' : '24px' }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lock size={15} color="var(--accent-primary)" /> Account Password *
            </label>
            <input
              type="password"
              name="password"
              required
              placeholder="Enter password"
              value={formData.password}
              onChange={handleChange}
              className="form-input"
              style={{ padding: '12px 14px', fontSize: '0.95rem' }}
            />
          </div>

          {mode === 'signup' && (
            <div className="form-group" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', margin: 0 }}>
                  <KeyRound size={15} color="#f59e0b" /> Gmail App Password (Optional)
                </label>
                <button
                  type="button"
                  onClick={() => setShowAppPasswordHelp(!showAppPasswordHelp)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--accent-primary)',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <HelpCircle size={14} /> Help
                </button>
              </div>
              <input
                type="password"
                name="app_password"
                placeholder="16-character Gmail App Password (e.g. awmtyyfozljwmbvu)"
                value={formData.app_password}
                onChange={handleChange}
                className="form-input"
                style={{ padding: '12px 14px', fontSize: '0.95rem' }}
              />

              {showAppPasswordHelp && (
                <div style={{
                  marginTop: '10px',
                  padding: '12px 14px',
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '10px',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  lineHeight: '1.5'
                }}>
                  <strong style={{ color: 'var(--text-primary)' }}>How to get a Gmail App Password:</strong>
                  <ol style={{ paddingLeft: '18px', marginTop: '4px', marginBottom: 0 }}>
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
              padding: '14px',
              fontSize: '1rem',
              fontWeight: '700',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            {loading ? 'Processing...' : (
              mode === 'login' ? (
                <>Log In to Account <ArrowRight size={18} /></>
              ) : (
                <>Create Account & Start <ArrowRight size={18} /></>
              )
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
