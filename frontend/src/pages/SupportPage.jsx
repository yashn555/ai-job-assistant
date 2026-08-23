import React, { useState, useEffect } from 'react';
import { HelpCircle, Send, Key, Sparkles, CheckCircle2, MessageSquare, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';

export default function SupportPage({ user }) {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [openFaq, setOpenFaq] = useState(0);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      const data = await api.getMySupportTickets();
      setTickets(data || []);
    } catch (err) {
      console.error('Failed to fetch support tickets:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) {
      setErrorMsg('Please enter both subject and message.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await api.submitSupportTicket(subject, message);
      setSuccessMsg('Your support request has been submitted successfully! Our team will respond shortly.');
      setSubject('');
      setMessage('');
      await loadTickets();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit support request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const faqs = [
    {
      q: 'How do I generate a 16-character Gmail App Password?',
      a: '1. Log into your Google Account.\n2. Go to Security > 2-Step Verification and turn it ON if not enabled.\n3. Search for "App Passwords" in your Google Account search bar.\n4. Create a new App Password named "AI Job Assistant".\n5. Copy the generated 16-character code (without spaces) and paste it into Settings > SMTP Settings.'
    },
    {
      q: 'How does Nemotron AI Email Generation work?',
      a: 'When you paste a job posting or upload job files, Nemotron AI automatically extracts company details, role requirements, and hiring email addresses. It then writes a customized, highly compelling job application email using your uploaded Candidate Profile and technical skills.'
    },
    {
      q: 'Is my personal information secure after deployment?',
      a: 'Yes! Authentication protects your candidate profile, resume files, app settings, and job application history. Other users cannot view or access your personal data.'
    },
    {
      q: 'Can I send job applications in bulk?',
      a: 'Yes! Navigate to the Dashboard or Parsed Jobs tab and click "1-Click Batch Send". All generated job emails will be sent concurrently via your configured Gmail SMTP.'
    }
  ];

  return (
    <div className="page-container">
      <div style={{ marginBottom: '24px' }}>
        <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <HelpCircle color="var(--accent-primary)" size={28} />
          User Support & Help Center
        </h1>
        <p className="page-subtitle">
          Find answers to common questions or submit a support ticket to get help with your account.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '24px'
      }}>
        {/* Support Ticket Submission Form */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageSquare size={20} color="var(--accent-primary)" />
            Contact User Support
          </h2>

          {successMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'rgba(34, 197, 94, 0.15)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              color: '#4ade80',
              padding: '12px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              marginBottom: '16px'
            }}>
              <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '12px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              marginBottom: '16px'
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Subject / Issue Title *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Need help with Gmail SMTP sending"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Message Details *</label>
              <textarea
                className="form-textarea"
                rows={5}
                placeholder="Describe your issue or feedback in detail..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
              style={{ width: '100%', padding: '10px 16px', fontWeight: '600' }}
            >
              <Send size={16} />
              {isSubmitting ? 'Submitting...' : 'Submit Support Ticket'}
            </button>
          </form>

          {/* Past Tickets Section */}
          {tickets.length > 0 && (
            <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: '12px' }}>Your Recent Tickets</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {tickets.map((t) => (
                  <div key={t.id} style={{
                    padding: '10px 12px',
                    backgroundColor: 'var(--bg-app)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.82rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '600' }}>
                      <span>{t.subject}</span>
                      <span className="badge badge-generated">{t.status}</span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>{t.message}</p>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      Submitted: {new Date(t.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* FAQs Accordion */}
        <div className="card">
          <h2 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={20} color="#6366f1" />
            Frequently Asked Questions
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {faqs.map((faq, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div key={idx} style={{
                  backgroundColor: 'var(--bg-app)',
                  borderRadius: '10px',
                  border: '1px solid var(--border-color)',
                  overflow: 'hidden'
                }}>
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    style={{
                      width: '100%',
                      padding: '14px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      backgroundColor: 'transparent',
                      border: 'none',
                      color: 'var(--text-primary)',
                      fontWeight: '600',
                      fontSize: '0.9rem',
                      textAlign: 'left',
                      cursor: 'pointer'
                    }}
                  >
                    <span>{faq.q}</span>
                    {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>

                  {isOpen && (
                    <div style={{
                      padding: '0 16px 14px 16px',
                      color: 'var(--text-secondary)',
                      fontSize: '0.85rem',
                      whiteSpace: 'pre-line',
                      borderTop: '1px solid var(--border-color)',
                      paddingTop: '10px',
                      lineHeight: '1.6'
                    }}>
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
