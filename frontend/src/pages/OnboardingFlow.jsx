import React, { useState } from 'react';
import { 
  User, 
  KeyRound, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  Loader2, 
  Upload, 
  Save, 
  FileText, 
  Mail, 
  Phone, 
  GraduationCap, 
  Lock, 
  HelpCircle,
  AlertCircle
} from 'lucide-react';

export default function OnboardingFlow({ 
  user, 
  profile, 
  appSettings, 
  onSaveProfile, 
  onSaveAppSettings, 
  onCompleteOnboarding 
}) {
  const [step, setStep] = useState(1); // 1: Profile Details, 2: App Password, 3: Saving/Spinner, 4: Ready Confirmation
  const [loading, setLoading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractMsg, setExtractMsg] = useState('');
  const [showAppPassHelp, setShowAppPassHelp] = useState(false);

  // Profile Form State
  const [name, setName] = useState(profile?.name || user?.name || '');
  const [email, setEmail] = useState(profile?.email || user?.email || '');
  const [phone, setPhone] = useState(profile?.phone || user?.phone || '');
  const [degree, setDegree] = useState(profile?.degree || '');
  const [college, setCollege] = useState(profile?.college || '');
  const [graduationYear, setGraduationYear] = useState(profile?.graduation_year || '');
  const [linkedin, setLinkedin] = useState(profile?.linkedin_url || '');
  const [github, setGithub] = useState(profile?.github_url || '');
  const [portfolio, setPortfolio] = useState(profile?.portfolio_url || '');
  const [skillsText, setSkillsText] = useState((profile?.skills || []).join(', '));
  const [projectsText, setProjectsText] = useState((profile?.projects || []).join(', '));
  const [bio, setBio] = useState(profile?.bio || '');

  // App Password State
  const [appPassword, setAppPassword] = useState(appSettings?.smtp_password || user?.app_password || '');

  const fileRef = React.useRef(null);

  const handleExtractFromResume = async (file) => {
    if (!file) return;
    setIsExtracting(true);
    setExtractMsg('');
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

      setExtractMsg(`Extracted details from '${file.name}' successfully!`);
    } catch (err) {
      alert(`Resume extraction failed: ${err.message}`);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !degree.trim()) {
      alert('Please fill in your Name, Email, and Qualification/Degree.');
      return;
    }

    const payload = {
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

    await onSaveProfile(payload);
    setStep(2);
  };

  const handleStep2Submit = async (e) => {
    e.preventDefault();
    if (!appPassword.trim()) {
      alert('Please enter your 16-character Gmail App Password to enable email sending.');
      return;
    }

    setStep(3); // Show Saving Spinner
    setLoading(true);

    try {
      await onSaveAppSettings({
        smtp_host: 'smtp.gmail.com',
        smtp_port: 587,
        smtp_username: email,
        smtp_password: appPassword.trim(),
        sender_email: email,
        auto_send: false,
        active_resume: appSettings?.active_resume || ''
      });

      setTimeout(() => {
        setLoading(false);
        setStep(4); // Show Ready Message
      }, 1200);
    } catch (err) {
      setLoading(false);
      setStep(2);
      alert(`App password save failed: ${err.message}`);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--bg-app)',
      padding: '40px 20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '680px',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '24px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 25px 50px rgba(0,0,0,0.3)',
        overflow: 'hidden'
      }}>
        
        {/* Step Progress Header */}
        <div style={{
          padding: '24px 32px',
          backgroundColor: 'var(--bg-sidebar)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              backgroundColor: 'var(--accent-primary)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: '800', margin: 0, color: 'var(--text-primary)' }}>
                Candidate Onboarding Setup
              </h2>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>
                Step {step > 3 ? 3 : step} of 3
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: step >= 1 ? 'var(--accent-primary)' : 'var(--border-color)'
            }} />
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: step >= 2 ? 'var(--accent-primary)' : 'var(--border-color)'
            }} />
            <span style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: step >= 4 ? '#4ade80' : 'var(--border-color)'
            }} />
          </div>
        </div>

        {/* STEP 1: Profile Details Form + Resume Extraction */}
        {step === 1 && (
          <form onSubmit={handleStep1Submit} style={{ padding: '32px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
                Fill Candidate Profile Details
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Enter your academic background, skills, and portfolio details, or auto-fill directly from your resume PDF.
              </p>
            </div>

            {/* Extract from Resume Banner */}
            <div style={{
              padding: '18px 20px',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              border: '1px dashed var(--accent-primary)',
              borderRadius: '14px',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <div>
                <strong style={{ fontSize: '0.92rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <FileText size={16} color="var(--accent-primary)" /> Auto-Extract From Resume PDF
                </strong>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', display: 'block', marginTop: '2px' }}>
                  Upload PDF to autofill name, degree, college, skills & social links instantly.
                </span>
              </div>

              <input
                type="file"
                ref={fileRef}
                onChange={(e) => e.target.files?.[0] && handleExtractFromResume(e.target.files[0])}
                accept=".pdf,.docx,.txt"
                style={{ display: 'none' }}
              />

              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={isExtracting}
                className="btn btn-secondary"
                style={{ padding: '9px 16px', fontSize: '0.85rem', fontWeight: '700' }}
              >
                {isExtracting ? (
                  <>
                    <Loader2 size={15} className="animate-pulse" /> Extracting...
                  </>
                ) : (
                  <>
                    <Upload size={15} /> Extract From Resume
                  </>
                )}
              </button>
            </div>

            {extractMsg && (
              <div style={{
                padding: '10px 14px',
                backgroundColor: 'rgba(34, 197, 94, 0.15)',
                border: '1px solid rgba(34, 197, 94, 0.4)',
                borderRadius: '8px',
                color: '#4ade80',
                fontSize: '0.84rem',
                marginBottom: '20px'
              }}>
                <CheckCircle2 size={16} style={{ display: 'inline', marginRight: '6px' }} /> {extractMsg}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
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
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="+91 8668220011"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Degree / Qualification *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. B.Tech CSE"
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
                  placeholder="e.g. 2026"
                  value={graduationYear}
                  onChange={(e) => setGraduationYear(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label className="form-label">College / University</label>
              <input
                type="text"
                className="form-input"
                placeholder="College / University Name"
                value={college}
                onChange={(e) => setCollege(e.target.value)}
              />
            </div>

            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label className="form-label">Technical Skills Possessed (Comma-separated)</label>
              <input
                type="text"
                className="form-input"
                placeholder="React.js, Node.js, JavaScript, Python, SQL, REST APIs"
                value={skillsText}
                onChange={(e) => setSkillsText(e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '24px' }}>
              <div className="form-group">
                <label className="form-label">LinkedIn URL</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="linkedin.com/in/username"
                  value={linkedin}
                  onChange={(e) => setLinkedin(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">GitHub URL</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="github.com/username"
                  value={github}
                  onChange={(e) => setGithub(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Portfolio URL</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="portfolio.dev"
                  value={portfolio}
                  onChange={(e) => setPortfolio(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '1rem',
                fontWeight: '700',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              Save Profile & Next Step <ArrowRight size={18} />
            </button>
          </form>
        )}

        {/* STEP 2: Gmail App Password & Email Setup */}
        {step === 2 && (
          <form onSubmit={handleStep2Submit} style={{ padding: '32px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <KeyRound size={22} color="#f59e0b" /> Configure Gmail Email & App Password
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Provide your 16-character Gmail App Password so the application can send job emails from your email address.
              </p>
            </div>

            <div className="form-group" style={{ marginBottom: '18px' }}>
              <label className="form-label">Gmail Address</label>
              <input
                type="email"
                className="form-input"
                value={email}
                disabled
                style={{ opacity: 0.8 }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label" style={{ margin: 0 }}>Gmail 16-Character App Password *</label>
                <button
                  type="button"
                  onClick={() => setShowAppPassHelp(!showAppPassHelp)}
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
                  <HelpCircle size={14} /> How to get App Password?
                </button>
              </div>

              <input
                type="password"
                className="form-input"
                placeholder="e.g. awmt yyfo zljw mbvu"
                value={appPassword}
                onChange={(e) => setAppPassword(e.target.value)}
                required
                style={{ fontSize: '1rem', letterSpacing: '1px' }}
              />

              {showAppPassHelp && (
                <div style={{
                  marginTop: '12px',
                  padding: '14px',
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '10px',
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  lineHeight: '1.5'
                }}>
                  <strong style={{ color: 'var(--text-primary)' }}>3 Quick Steps to Get Gmail App Password:</strong>
                  <ol style={{ paddingLeft: '18px', marginTop: '6px', marginBottom: 0 }}>
                    <li>Open <strong>Google Account</strong> &gt; Security.</li>
                    <li>Enable <strong>2-Step Verification</strong>.</li>
                    <li>Search <strong>App Passwords</strong>, create one for "Mail", and paste the 16 letters here.</li>
                  </ol>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => setStep(1)}
                style={{ padding: '14px 20px', borderRadius: '12px' }}
              >
                Back
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                style={{
                  flex: 1,
                  padding: '14px',
                  fontSize: '1rem',
                  fontWeight: '700',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                Save All Details & Finish <CheckCircle2 size={18} />
              </button>
            </div>
          </form>
        )}

        {/* STEP 3: Saving Spinner & Processing */}
        {step === 3 && (
          <div style={{ padding: '60px 32px', textAlign: 'center' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              color: 'var(--accent-primary)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '20px'
            }}>
              <Loader2 size={36} className="animate-pulse" />
            </div>
            <h3 style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              Saving & Configuring Your Profile...
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
              Validating Gmail SMTP credentials and storing profile details securely.
            </p>
          </div>
        )}

        {/* STEP 4: Ready to Send Confirmation */}
        {step === 4 && (
          <div style={{ padding: '48px 32px', textAlign: 'center' }}>
            <div style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              backgroundColor: 'rgba(34, 197, 94, 0.15)',
              color: '#4ade80',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '20px',
              boxShadow: '0 8px 24px rgba(34, 197, 94, 0.3)'
            }}>
              <CheckCircle2 size={44} />
            </div>

            <h2 style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              Now ready to send!
            </h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '8px', marginBottom: '28px', maxWidth: '440px', marginInline: 'auto' }}>
              Your profile details and Gmail App Password have been successfully saved. You can now paste job postings on your Dashboard and send tailored AI application emails in 1-Click.
            </p>

            <button
              type="button"
              onClick={onCompleteOnboarding}
              className="btn btn-success"
              style={{
                padding: '14px 32px',
                fontSize: '1.05rem',
                fontWeight: '800',
                borderRadius: '12px',
                boxShadow: '0 6px 20px rgba(34, 197, 94, 0.4)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              Open Dashboard & Start Sending <ArrowRight size={20} />
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
