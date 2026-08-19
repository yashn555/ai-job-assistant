import React from 'react';
import { Briefcase, Sparkles, Send, AlertTriangle, Layers, Rocket, Loader2 } from 'lucide-react';
import ChatInput from '../components/ChatInput';
import JobCard from '../components/JobCard';

export default function Dashboard({ 
  applications, 
  onParseText, 
  onUploadFile, 
  onResumeUpload, 
  onReviewEdit, 
  onSend, 
  onBatchSend,
  onSkip, 
  isParsing,
  isBatchSending,
  sendingIds
}) {
  const totalCount = applications.length;
  const generatedCount = applications.filter(a => a.status === 'GENERATED' || a.status === 'REVIEWED').length;
  const sentCount = applications.filter(a => a.status === 'SENT').length;
  const failedCount = applications.filter(a => a.status === 'FAILED').length;

  const activeParsedJobs = applications.filter(a => a.status !== 'SENT' && a.status !== 'SKIPPED');
  const readyToSendCount = activeParsedJobs.filter(a => a.recipient_email).length;

  return (
    <div className="page-container">
      <div style={{ marginBottom: '24px' }}>
        <h1 className="page-title">AI Job Application Assistant</h1>
        <p className="page-subtitle">
          Paste single or multi-job postings, generate personalized AI application emails instantly, review, or send all in 1-Click via Gmail SMTP.
        </p>
      </div>

      {/* Metric Counters Banner */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(148, 163, 184, 0.15)', color: '#cbd5e1' }}>
            <Layers size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Total Applications</p>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '700' }}>{totalCount}</h3>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <Sparkles size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Emails Generated</p>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#60a5fa' }}>{generatedCount}</h3>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' }}>
            <Send size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Applications Sent</p>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#4ade80' }}>{sentCount}</h3>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Failed Sends</p>
            <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f87171' }}>{failedCount}</h3>
          </div>
        </div>
      </div>

      {/* Ingestion Chat Area */}
      <ChatInput
        onParseText={onParseText}
        onUploadFile={onUploadFile}
        onResumeUpload={onResumeUpload}
        isParsing={isParsing}
      />

      {/* Applications List & Batch Action Bar */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '16px'
        }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Briefcase size={20} color="#6366f1" /> Active Applications ({activeParsedJobs.length})
          </h2>

          {/* 1-Click Batch Send Button */}
          {readyToSendCount > 0 && (
            <button
              className="btn btn-success"
              onClick={onBatchSend}
              disabled={isBatchSending}
              style={{ padding: '10px 20px', fontSize: '0.92rem', fontWeight: '600', boxShadow: '0 4px 12px rgba(34, 197, 94, 0.3)' }}
            >
              {isBatchSending ? (
                <>
                  <Loader2 size={16} className="animate-pulse" /> Sending Batch Emails...
                </>
              ) : (
                <>
                  <Rocket size={16} /> Send All {readyToSendCount} Applications (1-Click)
                </>
              )}
            </button>
          )}
        </div>

        {activeParsedJobs.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
            <Briefcase size={36} style={{ marginBottom: '12px', opacity: 0.5 }} />
            <p style={{ fontSize: '0.95rem' }}>No active applications. Paste single or multi-job opportunities above to generate and send emails.</p>
          </div>
        ) : (
          activeParsedJobs.map((app) => (
            <JobCard
              key={app.id}
              app={app}
              onReviewEdit={onReviewEdit}
              onSend={onSend}
              onSkip={onSkip}
              isSending={sendingIds.includes(app.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}
