import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import EmailPreviewModal from './components/EmailPreviewModal';
import AuthModal from './components/AuthModal';

import Dashboard from './pages/Dashboard';
import ApplicationsPage from './pages/ApplicationsPage';
import SettingsPage from './pages/SettingsPage';
import SupportPage from './pages/SupportPage';

import { api } from './services/api';

window.api = api;

export default function App() {
  const [user, setUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [applications, setApplications] = useState([]);
  const [profile, setProfile] = useState(null);
  const [appSettings, setAppSettings] = useState(null);
  const [resumesList, setResumesList] = useState([]);

  const [isParsing, setIsParsing] = useState(false);
  const [isBatchSending, setIsBatchSending] = useState(false);
  const [sendingIds, setSendingIds] = useState([]);

  // Mobile Menu Drawer state
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Modal State
  const [reviewApp, setReviewApp] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);


  const checkAuth = async () => {
    setIsAuthLoading(true);
    const token = localStorage.getItem('job_assistant_token');
    if (!token) {
      setUser(null);
      setShowAuthModal(true);
      setIsAuthLoading(false);
      return;
    }

    try {
      const currentUser = await api.getMe();
      setUser(currentUser);
      setShowAuthModal(false);
      await loadData();
    } catch (err) {
      console.warn('Initial session check:', err.message);
      api.logout();
      setUser(null);
      setShowAuthModal(true);
    } finally {
      setIsAuthLoading(false);
    }
  };



  const loadData = async () => {
    try {
      const [appsRes, profRes, settingsRes, resumesRes] = await Promise.all([
        api.getApplications(),
        api.getProfile(),
        api.getAppSettings(),
        api.getResumes()
      ]);
      setApplications(appsRes || []);
      setProfile(profRes);
      setAppSettings(settingsRes);
      setResumesList(resumesRes || []);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuthModal(false);
    loadData();
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setShowAuthModal(true);
    setApplications([]);
    setProfile(null);
    setAppSettings(null);
  };

  // High-Speed Multi-Job Ingestion
  const handleParseText = async (text) => {
    setIsParsing(true);
    try {
      const createdApps = await api.parseJobsText(text);
      await loadData();
      if (createdApps && createdApps.length === 1) {
        setReviewApp(createdApps[0]);
      }
      setActiveTab('dashboard');
    } catch (err) {
      alert(`Parsing failed: ${err.message}`);
    } finally {
      setIsParsing(false);
    }
  };

  const handleUploadJobFile = async (file) => {
    setIsParsing(true);
    try {
      const createdApps = await api.parseJobsFile(file);
      await loadData();
      if (createdApps && createdApps.length === 1) {
        setReviewApp(createdApps[0]);
      }
      setActiveTab('dashboard');
    } catch (err) {
      alert(`File upload parsing failed: ${err.message}`);
    } finally {
      setIsParsing(false);
    }
  };

  // Regenerate Email Handler
  const handleRegenerateEmail = async (appId) => {
    setIsRegenerating(true);
    try {
      const updatedApp = await api.generateEmail(appId);
      setApplications(prev => prev.map(a => a.id === updatedApp.id ? updatedApp : a));
      setReviewApp(updatedApp);
    } catch (err) {
      alert(`Regeneration failed: ${err.message}`);
    } finally {
      setIsRegenerating(false);
    }
  };

  // Review & Save Handler
  const handleSaveAppUpdates = async (appId, updates) => {
    try {
      const updatedApp = await api.updateApplication(appId, updates);
      setApplications(prev => prev.map(a => a.id === updatedApp.id ? updatedApp : a));
      if (reviewApp && reviewApp.id === appId) {
        setReviewApp(updatedApp);
      }
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    }
  };

  // Single Application Send
  const handleSendApp = async (appId, overrideDuplicate = false) => {
    setSendingIds(prev => [...prev, appId]);
    try {
      const sentApp = await api.sendApplication(appId, overrideDuplicate);
      setApplications(prev => prev.map(a => a.id === sentApp.id ? sentApp : a));
      if (reviewApp && reviewApp.id === appId) {
        setReviewApp(null);
      }
      alert(`Application sent successfully to ${sentApp.company_name} (${sentApp.recipient_email}) via Gmail SMTP!`);
    } catch (err) {
      if (err.message.includes('already sent') && !overrideDuplicate) {
        if (window.confirm(`${err.message}\nDo you want to manually override and send again?`)) {
          handleSendApp(appId, true);
        }
      } else {
        alert(`Sending failed: ${err.message}`);
      }
      await loadData();
    } finally {
      setSendingIds(prev => prev.filter(id => id !== appId));
    }
  };

  // 1-Click Batch Send All Active Applications
  const handleBatchSendAll = async () => {
    const readyApps = applications.filter(a => a.status !== 'SENT' && a.status !== 'SKIPPED' && a.recipient_email);
    if (readyApps.length === 0) {
      alert('No ready applications with recipient emails found to send.');
      return;
    }

    if (!window.confirm(`Are you sure you want to send all ${readyApps.length} application emails right now via Gmail SMTP?`)) {
      return;
    }

    setIsBatchSending(true);
    try {
      const appIds = readyApps.map(a => a.id);
      const res = await api.batchSendApplications(appIds);
      await loadData();
      alert(`Batch sending completed!\nSuccessfully sent: ${res.sent_count}\nFailed: ${res.failed_count}`);
    } catch (err) {
      alert(`Batch send failed: ${err.message}`);
    } finally {
      setIsBatchSending(false);
    }
  };

  const handleSkipApp = async (app) => {
    try {
      await api.updateApplication(app.id, { status: 'SKIPPED' });
      await loadData();
    } catch (err) {
      alert(`Failed to skip: ${err.message}`);
    }
  };

  const handleDeleteApp = async (appId) => {
    if (!window.confirm('Are you sure you want to delete this application record?')) return;
    try {
      await api.deleteApplication(appId);
      setApplications(prev => prev.filter(a => a.id !== appId));
      if (reviewApp && reviewApp.id === appId) {
        setReviewApp(null);
      }
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  // Settings Handlers
  const handleSaveProfile = async (profileData) => {
    try {
      const updated = await api.updateProfile(profileData);
      setProfile(updated);
      alert('Candidate profile saved successfully!');
    } catch (err) {
      alert(`Profile update failed: ${err.message}`);
    }
  };

  const handleSaveAppSettings = async (settingsData) => {
    try {
      const updated = await api.updateAppSettings(settingsData);
      setAppSettings(updated);
      alert('SMTP settings saved successfully!');
    } catch (err) {
      alert(`Settings update failed: ${err.message}`);
    }
  };

  const handleUploadResume = async (file) => {
    try {
      const res = await api.uploadResume(file);
      await loadData();
      alert(`Resume '${res.filename}' uploaded successfully.`);
    } catch (err) {
      alert(`Resume upload failed: ${err.message}`);
    }
  };

  const handleDeleteResume = async (filename) => {
    try {
      await api.deleteResume(filename);
      await loadData();
    } catch (err) {
      alert(`Failed to remove resume: ${err.message}`);
    }
  };

  const handleTestEmail = async (recipient) => {
    return await api.testEmail(recipient);
  };

  const counts = {
    parsed: applications.filter(a => a.status !== 'SENT' && a.status !== 'SKIPPED').length,
    sent: applications.filter(a => a.status === 'SENT').length,
    failed: applications.filter(a => a.status === 'FAILED').length
  };

  const tabTitles = {
    dashboard: 'Dashboard',
    new: 'New Job Application',
    parsed: 'Parsed Job Opportunities',
    sent: 'Sent Applications',
    failed: 'Failed Applications',
    support: 'User Support & Help Center',
    settings: 'Candidate Profile & Credentials'
  };

  if (isAuthLoading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-app)', color: 'var(--text-primary)' }}>
        <p className="animate-pulse" style={{ fontSize: '1.1rem', fontWeight: '600' }}>Loading AI Job Assistant...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        counts={counts}
        user={user}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      <main className="main-content">
        <Header
          title={tabTitles[activeTab] || 'AI Job Application Assistant'}
          activeResume={appSettings?.active_resume}
          autoSend={appSettings?.auto_send}
          user={user}
          onLogout={handleLogout}
          onToggleMobileMenu={() => setIsMobileOpen(!isMobileOpen)}
        />

        {(activeTab === 'dashboard' || activeTab === 'new') && (
          <Dashboard
            applications={applications}
            onParseText={handleParseText}
            onUploadFile={handleUploadJobFile}
            onResumeUpload={handleUploadResume}
            onReviewEdit={(app) => setReviewApp(app)}
            onSend={(app) => handleSendApp(app.id)}
            onBatchSend={handleBatchSendAll}
            onSkip={handleSkipApp}
            isParsing={isParsing}
            isBatchSending={isBatchSending}
            sendingIds={sendingIds}
          />
        )}

        {(activeTab === 'parsed' || activeTab === 'sent' || activeTab === 'failed') && (
          <ApplicationsPage
            applications={applications}
            activeFilter={activeTab === 'parsed' ? 'DRAFT' : activeTab.toUpperCase()}
            onReviewEdit={(app) => setReviewApp(app)}
            onSend={(app) => handleSendApp(app.id)}
            onDelete={handleDeleteApp}
          />
        )}

        {activeTab === 'support' && (
          <SupportPage user={user} />
        )}

        {activeTab === 'settings' && (
          <SettingsPage
            user={user}
            profile={profile}
            appSettings={appSettings}
            resumesList={resumesList}
            onSaveProfile={handleSaveProfile}
            onSaveAppSettings={handleSaveAppSettings}
            onUploadResume={handleUploadResume}
            onDeleteResume={handleDeleteResume}
            onTestEmail={handleTestEmail}
          />
        )}
      </main>

      <EmailPreviewModal
        isOpen={Boolean(reviewApp)}
        app={reviewApp}
        onClose={() => setReviewApp(null)}
        onSave={handleSaveAppUpdates}
        onRegenerate={handleRegenerateEmail}
        onSend={(appId) => handleSendApp(appId)}
        isRegenerating={isRegenerating}
        sendingIds={sendingIds}
      />

      <AuthModal
        isOpen={showAuthModal}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}

