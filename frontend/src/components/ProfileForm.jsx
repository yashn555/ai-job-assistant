import React, { useState, useEffect } from 'react';
import { 
  User, 
  GraduationCap, 
  Globe, 
  Code, 
  Rocket, 
  Save, 
  Check, 
  Mail, 
  Server, 
  Lock, 
  FileText, 
  Upload, 
  Trash2, 
  Send,
  Loader2,
  Sparkles,
  Link as LinkIcon
} from 'lucide-react';

const LinkedinIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0077b5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
    <rect x="2" y="9" width="4" height="12"></rect>
    <circle cx="4" cy="4" r="2"></circle>
  </svg>
);

const GithubIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
);

export default function ProfileForm({ 
  user,
  profile, 
  appSettings, 
  resumesList,
  onSaveProfile, 
  onSaveAppSettings,
  onUploadResume,
  onDeleteResume,
  onTestEmail
}) {
  // Personal Details
  const [name, setName] = useState(profile?.name || user?.name || '');
  const [email, setEmail] = useState(profile?.email || user?.email || '');
  const [phone, setPhone] = useState(profile?.phone || user?.phone || '');
  const [degree, setDegree] = useState(profile?.degree || '');
  const [college, setCollege] = useState(profile?.college || '');
  const [graduationYear, setGraduationYear] = useState(profile?.graduation_year || '');

  // Social Links
  const [linkedin, setLinkedin] = useState(profile?.linkedin_url || '');
  const [github, setGithub] = useState(profile?.github_url || '');
  const [portfolio, setPortfolio] = useState(profile?.portfolio_url || '');

  // Skills & Projects
  const [skillsText, setSkillsText] = useState((profile?.skills || []).join(', '));
  const [projectsText, setProjectsText] = useState((profile?.projects || []).join(', '));
  const [bio, setBio] = useState(profile?.bio || '');

  // Resume Extraction state
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractSuccessMsg, setExtractSuccessMsg] = useState('');
  const extractFileRef = React.useRef(null);

  // SMTP Settings
  const [smtpHost, setSmtpHost] = useState(appSettings?.smtp_host || 'smtp.gmail.com');
  const [smtpPort, setSmtpPort] = useState(appSettings?.smtp_port || 587);
  const [smtpUsername, setSmtpUsername] = useState(appSettings?.smtp_username || user?.email || '');
  const [smtpPassword, setSmtpPassword] = useState(appSettings?.smtp_password || user?.app_password || '');
  const [senderEmail, setSenderEmail] = useState(appSettings?.sender_email || user?.email || '');

  // Test Email
  const [testRecipient, setTestRecipient] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testStatusMsg, setTestStatusMsg] = useState(null);

  // Independent Feedback Badges
  const [savedPersonalSuccess, setSavedPersonalSuccess] = useState(false);
  const [savedLinksSuccess, setSavedLinksSuccess] = useState(false);
  const [savedSkillsSuccess, setSavedSkillsSuccess] = useState(false);
  const [savedSmtpSuccess, setSavedSmtpSuccess] = useState(false);
  const [savedAllSuccess, setSavedAllSuccess] = useState(false);

  const fileRef = React.useRef(null);

  useEffect(() => {
    if (profile) {
      setName(profile.name || user?.name || '');
      setEmail(profile.email || user?.email || '');
      setPhone(profile.phone || user?.phone || '');
      setDegree(profile.degree || '');
      setCollege(profile.college || '');
      setGraduationYear(profile.graduation_year || '');
      setLinkedin(profile.linkedin_url || '');
      setGithub(profile.github_url || '');
      setPortfolio(profile.portfolio_url || '');
      setSkillsText((profile.skills || []).join(', '));
      setProjectsText((profile.projects || []).join(', '));
      setBio(profile.bio || '');
    }
  }, [profile, user]);

  useEffect(() => {
    if (appSettings) {
      setSmtpHost(appSettings.smtp_host || 'smtp.gmail.com');
      setSmtpPort(appSettings.smtp_port || 587);
      setSmtpUsername(appSettings.smtp_username || user?.email || '');
      setSmtpPassword(appSettings.smtp_password || user?.app_password || '');
      setSenderEmail(appSettings.sender_email || user?.email || '');
    }
  }, [appSettings, user]);

  const handleExtractResumeFile = async (file) => {
    if (!file) return;
    setIsExtracting(true);
    setExtractSuccessMsg('');
    try {
      const ext = await window.api.extractResumeProfile(file);
      if (ext.name) setName(ext.name);
      if (ext.email) setEmail(ext.email);
      if (ext.phone) setPhone(ext.phone);
      if (ext.degree) setDegree(ext.degree);
      if (ext.college) setCollege(ext.college);
      if (ext.graduation_year) setGraduationYear(ext.graduation_year);
      if (ext.linkedin_url) setLinkedin(ext.linkedin_url);
      if (ext.github_url) setGithub(ext.github_url);
      if (ext.portfolio_url) setPortfolio(ext.portfolio_url);
      if (ext.skills && ext.skills.length > 0) setSkillsText(ext.skills.join(', '));
      if (ext.projects && ext.projects.length > 0) setProjectsText(ext.projects.join(', '));
      if (ext.bio) setBio(ext.bio);
      
      setExtractSuccessMsg(`Extracted details successfully from '${file.name}'!`);
      setTimeout(() => setExtractSuccessMsg(''), 4000);
    } catch (err) {
      alert(`Resume extraction failed: ${err.message}`);
    } finally {
      setIsExtracting(false);
    }
  };

  // Helper to build full profile payload without losing current state
  const getCurrentProfilePayload = () => {
    return {
      name,
      email,
      phone,
      degree,
      college,
      graduation_year: graduationYear,
      linkedin_url: linkedin,
      github_url: github,
      portfolio_url: portfolio,
      skills: skillsText.split(',').map(s => s.trim()).filter(Boolean),
      projects: projectsText.split(',').map(p => p.trim()).filter(Boolean),
      bio
    };
  };

  // Section 1: Save Personal Info
  const handleSavePersonalInfo = (e) => {
    if (e) e.preventDefault();
    onSaveProfile(getCurrentProfilePayload());
    setSavedPersonalSuccess(true);
    setTimeout(() => setSavedPersonalSuccess(false), 3000);
  };

  // Section 2: Save Social Links
  const handleSaveSocialLinks = (e) => {
    if (e) e.preventDefault();
    onSaveProfile(getCurrentProfilePayload());
    setSavedLinksSuccess(true);
    setTimeout(() => setSavedLinksSuccess(false), 3000);
  };

  // Section 3: Save Skills & Projects
  const handleSaveSkillsAndProjects = (e) => {
    if (e) e.preventDefault();
    onSaveProfile(getCurrentProfilePayload());
    setSavedSkillsSuccess(true);
    setTimeout(() => setSavedSkillsSuccess(false), 3000);
  };

  // Section 4: Save SMTP Credentials
  const handleSaveSmtpSettings = (e) => {
    if (e) e.preventDefault();
    onSaveAppSettings({
      smtp_host: smtpHost,
      smtp_port: parseInt(smtpPort, 10) || 587,
      smtp_username: smtpUsername,
      smtp_password: smtpPassword,
      sender_email: senderEmail || smtpUsername,
      auto_send: appSettings?.auto_send || false,
      active_resume: appSettings?.active_resume || ''
    });
    setSavedSmtpSuccess(true);
    setTimeout(() => setSavedSmtpSuccess(false), 3000);
  };

  // Global Save All
  const handleSaveAll = () => {
    onSaveProfile(getCurrentProfilePayload());
    onSaveAppSettings({
      smtp_host: smtpHost,
      smtp_port: parseInt(smtpPort, 10) || 587,
      smtp_username: smtpUsername,
      smtp_password: smtpPassword,
      sender_email: senderEmail || smtpUsername,
      auto_send: appSettings?.auto_send || false,
      active_resume: appSettings?.active_resume || ''
    });
    setSavedAllSuccess(true);
    setTimeout(() => setSavedAllSuccess(false), 3000);
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Extract From Resume Action Box */}
      <div style={{
        padding: '20px 24px',
        backgroundColor: 'rgba(99, 102, 241, 0.08)',
        border: '1px dashed var(--accent-primary)',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} color="var(--accent-primary)" /> Auto-fill Profile from Resume PDF
          </h4>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '4px', margin: 0 }}>
            Upload your resume PDF/DOCX to extract Name, Phone, Degree, Skills, Projects, and Social links automatically.
          </p>
        </div>

        <input
          type="file"
          ref={extractFileRef}
          onChange={(e) => {
            if (e.target.files?.[0]) {
              const selectedFile = e.target.files[0];
              e.target.value = '';
              handleExtractResumeFile(selectedFile);
            }
          }}
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
        />


        <button
          type="button"
          onClick={() => extractFileRef.current?.click()}
          disabled={isExtracting}
          className="btn btn-primary"
          style={{ padding: '10px 20px', fontSize: '0.9rem', fontWeight: '700', borderRadius: '10px', boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)' }}
        >
          {isExtracting ? (
            <>
              <Loader2 size={16} className="animate-pulse" /> Extracting Details...
            </>
          ) : (
            <>
              <Upload size={16} /> Extract From Resume PDF
            </>
          )}
        </button>
      </div>

      {extractSuccessMsg && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: 'rgba(34, 197, 94, 0.15)',
          border: '1px solid rgba(34, 197, 94, 0.4)',
          borderRadius: '10px',
          color: '#4ade80',
          fontSize: '0.88rem',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Check size={18} /> {extractSuccessMsg}
        </div>
      )}

      {/* Global Quick Action Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '16px 20px',
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div>
          <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)', display: 'block' }}>
            Independent Section Control
          </strong>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Each section below has its own dedicated Save button. Modifying one section will not overwrite your other saved data.
          </span>
        </div>

        <button 
          type="button" 
          onClick={handleSaveAll}
          className="btn btn-primary" 
          style={{ padding: '10px 20px', fontSize: '0.9rem' }}
        >
          <Save size={16} /> Save All Settings
        </button>
      </div>

      {savedAllSuccess && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: 'rgba(34, 197, 94, 0.15)',
          border: '1px solid rgba(34, 197, 94, 0.4)',
          borderRadius: '8px',
          color: '#4ade80',
          fontSize: '0.88rem',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Check size={18} /> All profile details and system settings saved successfully!
        </div>
      )}

      {/* SECTION 1: Personal & Academic Details */}
      <form onSubmit={handleSavePersonalInfo} className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <User size={20} color="#6366f1" /> Candidate Personal & Academic Details
          </h3>
          {savedPersonalSuccess && (
            <span style={{ fontSize: '0.85rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
              <Check size={16} /> Personal Details Saved!
            </span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address *</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="text"
              className="form-input"
              placeholder="+91 9876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">Degree / Qualification</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. B.Tech Computer Science Engineering"
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Graduation Year</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. 2026"
              value={graduationYear}
              onChange={(e) => setGraduationYear(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label">College / University</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g. University / College Name"
            value={college}
            onChange={(e) => setCollege(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '9px 20px', fontSize: '0.88rem' }}>
            <Save size={15} /> Save Personal Details
          </button>
        </div>
      </form>

      {/* SECTION 2: Online Profiles & Links */}
      <form onSubmit={handleSaveSocialLinks} className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <LinkIcon size={20} color="#6366f1" /> Online Profiles & Portfolio Links
          </h3>
          {savedLinksSuccess && (
            <span style={{ fontSize: '0.85rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
              <Check size={16} /> Links Saved!
            </span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '20px' }}>
          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><LinkedinIcon /> LinkedIn Profile</span>
            </label>
            <input
              type="url"
              className="form-input"
              placeholder="https://linkedin.com/in/username"
              value={linkedin}
              onChange={(e) => setLinkedin(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><GithubIcon /> GitHub Profile</span>
            </label>
            <input
              type="url"
              className="form-input"
              placeholder="https://github.com/username"
              value={github}
              onChange={(e) => setGithub(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Globe size={13} style={{ display: 'inline', marginRight: '4px', color: '#10b981' }} /> Portfolio Website
            </label>
            <input
              type="url"
              className="form-input"
              placeholder="https://yourportfolio.dev"
              value={portfolio}
              onChange={(e) => setPortfolio(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '9px 20px', fontSize: '0.88rem' }}>
            <Save size={15} /> Save Social Links
          </button>
        </div>
      </form>

      {/* SECTION 3: Technical Skills & Key Projects */}
      <form onSubmit={handleSaveSkillsAndProjects} className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Code size={20} color="#6366f1" /> Technical Skills & Key Projects
          </h3>
          {savedSkillsSuccess && (
            <span style={{ fontSize: '0.85rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
              <Check size={16} /> Skills & Projects Saved!
            </span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span><Code size={14} style={{ display: 'inline', marginRight: '4px' }} /> Technical Skills (Possessed)</span>
            <span style={{ fontSize: '0.75rem', color: '#60a5fa' }}>Comma-separated list (matched strictly in AI emails)</span>
          </label>
          <textarea
            className="form-textarea"
            rows={3}
            value={skillsText}
            onChange={(e) => setSkillsText(e.target.value)}
            placeholder="Java, C++, JavaScript, React.js, Node.js, Python, SQL..."
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <Rocket size={14} style={{ display: 'inline', marginRight: '4px' }} /> Key Projects Built
          </label>
          <textarea
            className="form-textarea"
            rows={2}
            value={projectsText}
            onChange={(e) => setProjectsText(e.target.value)}
            placeholder="List key projects you have built..."
          />
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label">Candidate Bio / Professional Summary</label>
          <textarea
            className="form-textarea"
            rows={2}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Brief bio or elevator pitch for hiring managers..."
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '9px 20px', fontSize: '0.88rem' }}>
            <Save size={15} /> Save Skills & Projects
          </button>
        </div>
      </form>

      {/* SECTION 4: Resume Attachment & Storage */}
      <div className="card">
        <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={20} color="#6366f1" /> Resume Attachment & Storage
        </h3>

        <div style={{
          padding: '16px',
          backgroundColor: 'var(--bg-app)',
          border: '1px dashed var(--border-focus)',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <FileText size={28} color="#6366f1" />
            <div>
              <strong style={{ fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                Active Resume: {appSettings?.active_resume || 'None uploaded'}
              </strong>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0 }}>
                Automatically attached to outgoing job application emails.
              </p>
            </div>
          </div>

          <input
            type="file"
            ref={fileRef}
            onChange={(e) => e.target.files?.[0] && onUploadResume(e.target.files[0])}
            accept=".pdf,.docx"
            style={{ display: 'none' }}
          />

          <div style={{ display: 'flex', gap: '10px' }}>
            {appSettings?.active_resume && (
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => onDeleteResume(appSettings.active_resume)}
                style={{ color: '#f87171', borderColor: 'rgba(248, 113, 113, 0.4)' }}
              >
                <Trash2 size={15} /> Remove
              </button>
            )}

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fileRef.current?.click()}
            >
              <Upload size={16} /> Upload / Replace Resume
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 5: Gmail SMTP Credentials & Settings */}
      <form onSubmit={handleSaveSmtpSettings} className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Server size={20} color="#6366f1" /> Gmail SMTP Configuration & Credentials
          </h3>
          {savedSmtpSuccess && (
            <span style={{ fontSize: '0.85rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
              <Check size={16} /> SMTP Settings Saved!
            </span>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">SMTP Server Host</label>
            <input
              type="text"
              className="form-input"
              value={smtpHost}
              onChange={(e) => setSmtpHost(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Port</label>
            <input
              type="number"
              className="form-input"
              value={smtpPort}
              onChange={(e) => setSmtpPort(e.target.value)}
              required
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">Gmail Username</label>
            <input
              type="email"
              className="form-input"
              value={smtpUsername}
              onChange={(e) => setSmtpUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Gmail App Password (16 chars)</label>
            <input
              type="password"
              className="form-input"
              placeholder="16-character Gmail App Password"
              value={smtpPassword}
              onChange={(e) => setSmtpPassword(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label">Sender Email Address</label>
          <input
            type="email"
            className="form-input"
            value={senderEmail}
            onChange={(e) => setSenderEmail(e.target.value)}
            placeholder="defaults to Gmail username if empty"
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '16px', marginBottom: '20px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '9px 20px', fontSize: '0.88rem' }}>
            <Save size={15} /> Save SMTP Credentials
          </button>
        </div>

        {/* Test Email Row */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <label className="form-label">Test SMTP Delivery</label>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <input
              type="email"
              className="form-input"
              placeholder="Send test email to (e.g. recipient@example.com)..."
              value={testRecipient}
              onChange={(e) => setTestRecipient(e.target.value)}
              style={{ flex: 1, minWidth: '220px' }}
            />
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleRunTest}
              disabled={!testRecipient || isTesting}
            >
              {isTesting ? <Loader2 size={16} className="animate-pulse" /> : <Send size={16} />} Send Test Email
            </button>
          </div>

          {testStatusMsg && (
            <div style={{
              marginTop: '10px',
              padding: '10px 14px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              backgroundColor: testStatusMsg.type === 'success' ? 'var(--status-sent-bg)' : 'var(--status-failed-bg)',
              color: testStatusMsg.type === 'success' ? 'var(--status-sent-text)' : 'var(--status-failed-text)'
            }}>
              {testStatusMsg.text}
            </div>
          )}
        </div>
      </form>

      {/* Global Save Button at Bottom */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
        <button type="button" onClick={handleSaveAll} className="btn btn-primary" style={{ padding: '12px 28px', fontSize: '1rem' }}>
          <Save size={18} /> Save All Details & Credentials
        </button>
      </div>
    </div>
  );
}
