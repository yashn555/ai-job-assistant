import React, { useState, useRef } from 'react';
import { Clipboard, Upload, FileText, Sparkles, Loader2 } from 'lucide-react';

export default function ChatInput({ onParseText, onUploadFile, onResumeUpload, isParsing }) {
  const [inputText, setInputText] = useState('');
  const fileInputRef = useRef(null);
  const resumeInputRef = useRef(null);

  const handleParseSubmit = () => {
    if (!inputText.trim()) return;
    onParseText(inputText);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  const handleResumeFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onResumeUpload(e.target.files[0]);
    }
  };

  return (
    <div className="card" style={{
      marginBottom: '32px',
      backgroundColor: 'var(--bg-sidebar)',
      border: '1px solid var(--border-color)',
      borderRadius: '16px',
      padding: '24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={20} color="#6366f1" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600' }}>Paste Job Posting / Opportunity Details</h3>
        </div>
      </div>

      {/* Large Input Text Area */}
      <textarea
        className="form-textarea"
        rows={7}
        placeholder="Paste company name, job role, recipient email & job description here..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        style={{
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          backgroundColor: 'var(--bg-app)',
          borderRadius: '10px',
          marginBottom: '16px',
          resize: 'vertical'
        }}
      />

      {/* Action Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Secondary Upload Helpers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={async () => {
              try {
                const text = await navigator.clipboard.readText();
                if (text) setInputText(text);
              } catch (err) {
                alert('Clipboard permission denied.');
              }
            }}
          >
            <Clipboard size={16} /> Paste Clipboard
          </button>

          {/* Upload Job File */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.pdf,.docx"
            style={{ display: 'none' }}
          />
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={16} /> Upload Job File
          </button>

          {/* Upload Resume */}
          <input
            type="file"
            ref={resumeInputRef}
            onChange={handleResumeFileChange}
            accept=".pdf,.docx"
            style={{ display: 'none' }}
          />
          <button
            type="button"
            className="btn btn-outline"
            onClick={() => resumeInputRef.current?.click()}
          >
            <FileText size={16} /> Upload Resume
          </button>
        </div>

        {/* Primary Action Button */}
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleParseSubmit}
          disabled={!inputText.trim() || isParsing}
          style={{ padding: '12px 28px', fontSize: '0.95rem', fontWeight: '600' }}
        >
          {isParsing ? (
            <>
              <Loader2 size={18} className="animate-pulse" /> Generating Email...
            </>
          ) : (
            <>
              <Sparkles size={18} /> Generate Email Application
            </>
          )}
        </button>
      </div>
    </div>
  );
}
