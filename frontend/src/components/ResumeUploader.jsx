import React, { useRef } from 'react';
import { FileText, Upload, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ResumeUploader({ activeResume, resumesList, onUpload, onDelete }) {
  const fileRef = useRef(null);

  const handleFileSelected = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <FileText size={18} color="#6366f1" /> Resume Storage & Attachment Manager
      </h3>

      {/* Current Active Resume Indicator */}
      <div style={{
        padding: '16px',
        backgroundColor: 'var(--bg-app)',
        border: '1px dashed var(--border-focus)',
        borderRadius: '10px',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            backgroundColor: 'var(--accent-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)'
          }}>
            <FileText size={22} />
          </div>
          <div>
            <p style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-primary)' }}>
              Active Resume: {activeResume || 'None Uploaded'}
            </p>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Automatically attached to all outgoing application emails.
            </p>
          </div>
        </div>

        <input
          type="file"
          ref={fileRef}
          onChange={handleFileSelected}
          accept=".pdf,.docx"
          style={{ display: 'none' }}
        />

        <button
          className="btn btn-primary"
          onClick={() => fileRef.current?.click()}
        >
          <Upload size={16} /> {activeResume ? 'Replace Resume' : 'Upload Resume'}
        </button>
      </div>

      {/* List of uploaded resume files */}
      {resumesList && resumesList.length > 0 && (
        <div>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>Stored Resumes:</h4>
          <ul style={{ listStyle: 'none' }}>
            {resumesList.map((file) => {
              const isCurrent = file.filename === activeResume;
              return (
                <li key={file.filename} style={{
                  padding: '10px 14px',
                  backgroundColor: 'var(--bg-app)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <FileText size={16} color={isCurrent ? '#4ade80' : '#94a3b8'} />
                    <span style={{ fontSize: '0.88rem', fontWeight: isCurrent ? '600' : '400' }}>
                      {file.filename}
                    </span>
                    {isCurrent && (
                      <span className="badge badge-sent" style={{ fontSize: '0.65rem' }}>Active</span>
                    )}
                  </div>

                  <button
                    className="btn btn-danger"
                    style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                    onClick={() => onDelete(file.filename)}
                  >
                    <Trash2 size={12} /> Remove
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
