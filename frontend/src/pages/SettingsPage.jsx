import React from 'react';
import ProfileForm from '../components/ProfileForm';

export default function SettingsPage({
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
  return (
    <div className="page-container" style={{ maxWidth: '900px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 className="page-title">Candidate Profile & System Settings</h1>
        <p className="page-subtitle">
          Manage your candidate details, LinkedIn & GitHub links, technical skills, resume attachment, and Gmail SMTP credentials.
        </p>
      </div>

      <ProfileForm
        user={user}
        profile={profile}
        appSettings={appSettings}
        resumesList={resumesList}
        onSaveProfile={onSaveProfile}
        onSaveAppSettings={onSaveAppSettings}
        onUploadResume={onUploadResume}
        onDeleteResume={onDeleteResume}
        onTestEmail={onTestEmail}
      />
    </div>
  );
}
