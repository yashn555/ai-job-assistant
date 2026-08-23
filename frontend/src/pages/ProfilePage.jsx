import React from 'react';
import { 
  User, 
  GraduationCap, 
  Globe, 
  Code, 
  Rocket, 
  FileText, 
  Mail, 
  Server, 
  Edit3, 
  ExternalLink,
  CheckCircle2,
  Sparkles
} from 'lucide-react';

const LinkedinIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0077b5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
    <rect x="2" y="9" width="4" height="12"></rect>
    <circle cx="4" cy="4" r="2"></circle>
  </svg>
);

const GithubIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
);

export default function ProfilePage({ user, profile, appSettings, onNavigateToEdit }) {
  const skillsList = profile?.skills && profile.skills.length > 0
    ? profile.skills
    : ['Python', 'JavaScript', 'React', 'HTML', 'CSS'];

  const projectsList = profile?.projects && profile.projects.length > 0
    ? profile.projects
    : ['AI Job Application Assistant'];

  return (
    <div className="page-container" style={{ maxWidth: '960px' }}>
      {/* Page Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h1 className="page-title">Candidate Profile & Information</h1>
          <p className="page-subtitle">
            View your candidate details, possessed skills, active resume, and system credentials.
          </p>
        </div>

        <button
          onClick={onNavigateToEdit}
          className="btn btn-primary"
          style={{ padding: '10px 20px', fontSize: '0.92rem', fontWeight: '600' }}
        >
          <Edit3 size={16} /> Edit Profile & Credentials
        </button>
      </div>

      {/* Main Candidate Card */}
      <div className="card" style={{ marginBottom: '24px', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div style={{
            width: '68px',
            height: '68px',
            borderRadius: '18px',
            backgroundColor: 'var(--accent-primary)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.8rem',
            fontWeight: '800',
            boxShadow: '0 8px 20px rgba(99, 102, 241, 0.4)'
          }}>
            {(profile?.name || user?.name || 'C').charAt(0).toUpperCase()}
          </div>

          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--text-primary)', margin: 0 }}>
              {profile?.name || user?.name || 'Candidate'}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Mail size={15} color="var(--accent-primary)" /> {profile?.email || user?.email || 'email@example.com'}
              </span>
              <span>•</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <GraduationCap size={15} color="#10b981" /> {profile?.graduation_year ? `Batch ${profile.graduation_year}` : 'Active Student'}
              </span>
            </div>
          </div>
        </div>

        {/* Education Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '16px',
          backgroundColor: 'var(--bg-app)',
          padding: '16px 20px',
          borderRadius: '12px',
          border: '1px solid var(--border-color)',
          marginBottom: '20px'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Degree / Qualification</span>
            <p style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)', marginTop: '4px' }}>
              {profile?.degree || 'Not specified'}
            </p>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>College / University</span>
            <p style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)', marginTop: '4px' }}>
              {profile?.college || 'Not specified'}
            </p>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Graduation Year</span>
            <p style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)', marginTop: '4px' }}>
              {profile?.graduation_year || 'Not specified'}
            </p>
          </div>
        </div>

        {/* Online Links */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {profile?.linkedin_url && (
            <a
              href={profile.linkedin_url}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
            >
              <LinkedinIcon /> LinkedIn Profile <ExternalLink size={13} />
            </a>
          )}
          {profile?.github_url && (
            <a
              href={profile.github_url}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
            >
              <GithubIcon /> GitHub Profile <ExternalLink size={13} />
            </a>
          )}
          {profile?.portfolio_url && (
            <a
              href={profile.portfolio_url}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline"
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
            >
              <Globe size={14} color="#10b981" /> Portfolio Website <ExternalLink size={13} />
            </a>
          )}
        </div>
      </div>

      {/* Grid for Skills & Active Resume */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        
        {/* Technical Skills Possessed */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Code size={18} color="#6366f1" /> Technical Skills (Possessed)
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
            Skills matched strictly during AI email generation.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {skillsList.map((skill, idx) => (
              <span
                key={idx}
                style={{
                  backgroundColor: 'rgba(99, 102, 241, 0.12)',
                  color: 'var(--accent-primary)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '0.85rem',
                  fontWeight: '600'
                }}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Active Resume Attachment */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#6366f1" /> Active Resume Attachment
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
            Automatically attached to outgoing job application emails.
          </p>

          <div style={{
            padding: '16px',
            backgroundColor: 'var(--bg-app)',
            border: '1px solid var(--border-color)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '14px'
          }}>
            <FileText size={32} color="#6366f1" />
            <div>
              <strong style={{ fontSize: '0.92rem', color: 'var(--text-primary)', display: 'block' }}>
                {appSettings?.active_resume || 'Active Resume Attached'}
              </strong>
              <span style={{ fontSize: '0.78rem', color: '#4ade80', display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                <CheckCircle2 size={13} /> Reconstituted & Ready
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* Key Projects */}
      <div className="card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Rocket size={18} color="#6366f1" /> Key Projects Built
        </h3>
        
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {projectsList.map((proj, idx) => (
            <div
              key={idx}
              style={{
                padding: '10px 16px',
                backgroundColor: 'var(--bg-app)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                fontSize: '0.9rem',
                fontWeight: '600',
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Sparkles size={14} color="#f59e0b" /> {proj}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
