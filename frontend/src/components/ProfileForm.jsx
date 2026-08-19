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
  AlertCircle
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
  profile, 
  appSettings, 
  resumesList,
  onSaveProfile, 
  onSaveAppSettings,
  onUploadResume,
  onDeleteResume,
  onTestEmail
}) {
  const [name, setName] = useState(profile?.name || 'Yash Nagapure');
  const [email, setEmail] = useState(profile?.email || 'yashnagapure25@gmail.com');
  const [degree, setDegree] = useState(profile?.degree || 'B.Tech Computer Science Engineering');
  const [college, setCollege] = useState(profile?.college || 'AISSMS IOIT, Pune');
  const [graduationYear, setGraduationYear] = useState(profile?.graduation_year || '2027');
  const [linkedin, setLinkedin] = useState(profile?.linkedin_url || 'https://linkedin.com/in/yashnagapure');
  const [github, setGithub] = useState(profile?.github_url || 'https://github.com/yashnagapure');
  const [portfolio, setPortfolio] = useState(profile?.portfolio_url || 'https://yashnagapure.dev');
  const [skillsText, setSkillsText] = useState((profile?.skills || []).join(', '));
  const [projectsText, setProjectsText] = useState((profile?.projects || []).join(', '));
  const [bio, setBio] = useState(profile?.bio || '');

  const [smtpHost, setSmtpHost] = useState(appSettings?.smtp_host || 'smtp.gmail.com');
  const [smtpPort, setSmtpPort] = useState(appSettings?.smtp_port || 587);
  const [smtpUsername, setSmtpUsername] = useState(appSettings?.smtp_username || 'yashnagapure25@gmail.com');
  const [smtpPassword, setSmtpPassword] = useState(appSettings?.smtp_password || 'awmtyyfozljwmbvu');
  const [senderEmail, setSenderEmail] = useState(appSettings?.sender_email || 'yashnagapure25@gmail.com');

  const [testRecipient, setTestRecipient] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testStatusMsg, setTestStatusMsg] = useState(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const fileRef = React.useRef(null);

  useEffect(() => {
    if (profile) {
      setName(profile.name || '');
      setEmail(profile.email || 'yashnagapure25@gmail.com');
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
  }, [profile]);

  useEffect(() => {
    if (appSettings) {
      setSmtpHost(appSettings.smtp_host || 'smtp.gmail.com');
      setSmtpPort(appSettings.smtp_port || 587);
      setSmtpUsername(appSettings.smtp_username || 'yashnagapure25@gmail.com');
      setSmtpPassword(appSettings.smtp_password || 'awmtyyfozljwmbvu');
      setSenderEmail(appSettings.sender_email || 'yashnagapure25@gmail.com');
    }
  }, [appSettings]);

  const handleSaveAll = (e) => {
    e.preventDefault();
    const skillsArray = skillsText.split(',').map(s => s.trim()).filter(Boolean);
    const projectsArray = projectsText.split(',').map(p => p.trim()).filter(Boolean);

    onSaveProfile({
      name,
      email,
      degree,
      college,
      graduation_year: graduationYear,
      linkedin_url: linkedin,
      github_url: github,
      portfolio_url: portfolio,
      skills: skillsArray,
      projects: projectsArray,
      bio
    });

    onSaveAppSettings({
      smtp_host: smtpHost,
      smtp_port: parseInt(smtpPort, 10),
      smtp_username: smtpUsername,
      smtp_password: smtpPassword,
      sender_email: senderEmail || smtpUsername,
      auto_send: appSettings?.auto_send || false,
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <form onSubmit={handleSaveAll}>
        {/* Candidate Profile Details */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={20} color="#6366f1" /> Candidate Personal & Contact Information
            </h3>
            {savedSuccess && (
              <span style={{ fontSize: '0.85rem', color: '#4ade80', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600' }}>
                <Check size={16} /> Saved Successfully!
              </span>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Degree / Qualification</label>
              <input
                type="text"
                className="form-input"
                value={degree}
                onChange={(e) => setDegree(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Graduation Year</label>
              <input
                type="text"
                className="form-input"
                value={graduationYear}
                onChange={(e) => setGraduationYear(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">College / University</label>
            <input
              type="text"
              className="form-input"
              value={college}
              onChange={(e) => setCollege(e.target.value)}
              required
            />
          </div>

          {/* Online Profiles & Links */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginTop: '8px' }}>
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

          {/* Technical Skills Strict Note */}
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span><Code size={14} style={{ display: 'inline', marginRight: '4px' }} /> Technical Skills (Possessed)</span>
              <span style={{ fontSize: '0.75rem', color: '#60a5fa' }}>Only list skills you actually possess (matched strictly in AI emails)</span>
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
              placeholder="DocuForge AI, Travel-Friend, Hotel Mitraya..."
            />
          </div>
        </div>

        {/* Resume Storage Manager */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#6366f1" /> Resume Attachment
          </h3>

          <div style={{
            padding: '16px',
            backgroundColor: 'var(--bg-app)',
            border: '1px dashed var(--border-focus)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <FileText size={28} color="#6366f1" />
              <div>
                <strong style={{ fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                  Active Resume: {appSettings?.active_resume || 'Yash_Nagapure_Resume.pdf'}
                </strong>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  Automatically attached to outgoing emails.
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

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fileRef.current?.click()}
            >
              <Upload size={16} /> Upload / Replace Resume
            </button>
          </div>
        </div>

        {/* SMTP Gmail Configuration */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="#6366f1" /> Gmail SMTP Configuration
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
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

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
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
              <label className="form-label">Gmail App Password</label>
              <input
                type="password"
                className="form-input"
                value={smtpPassword}
                onChange={(e) => setSmtpPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Test Email Row */}
          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px', marginTop: '12px' }}>
            <label className="form-label">Test SMTP Delivery</label>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="email"
                className="form-input"
                placeholder="Send test email to (e.g. yashnagapure25@gmail.com)..."
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
                {isTesting ? <Loader2 size={16} className="animate-pulse" /> : <Send size={16} />} Send Test Email
              </button>
            </div>

            {testStatusMsg && (
              <div style={{
                marginTop: '10px',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '0.85rem',
                backgroundColor: testStatusMsg.type === 'success' ? 'var(--status-sent-bg)' : 'var(--status-failed-bg)',
                color: testStatusMsg.type === 'success' ? 'var(--status-sent-text)' : 'var(--status-failed-text)'
              }}>
                {testStatusMsg.text}
              </div>
            )}
          </div>
        </div>

        {/* Global Save Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '12px 28px', fontSize: '1rem' }}>
            <Save size={18} /> Save All Details & Credentials
          </button>
        </div>
      </form>
    </div>
  );
}
