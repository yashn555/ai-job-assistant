const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api';

async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Jobs API
  async parseJobsText(text) {
    const res = await fetch(`${API_BASE_URL}/jobs/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return handleResponse(res);
  },

  async parseJobsFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/jobs/upload-parse`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async generateEmail(applicationId) {
    const res = await fetch(`${API_BASE_URL}/jobs/generate-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ application_id: applicationId }),
    });
    return handleResponse(res);
  },

  // Applications API
  async getApplications(status = null) {
    const url = status ? `${API_BASE_URL}/applications?status=${status}` : `${API_BASE_URL}/applications`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getApplicationById(id) {
    const res = await fetch(`${API_BASE_URL}/applications/${id}`);
    return handleResponse(res);
  },

  async updateApplication(id, updates) {
    const res = await fetch(`${API_BASE_URL}/applications/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return handleResponse(res);
  },

  async sendApplication(id, overrideDuplicate = false) {
    const url = `${API_BASE_URL}/applications/${id}/send?override_duplicate=${overrideDuplicate}`;
    const res = await fetch(url, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  async batchSendApplications(appIds = null) {
    const res = await fetch(`${API_BASE_URL}/applications/batch-send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appIds || []),
    });
    return handleResponse(res);
  },

  async deleteApplication(id) {
    const res = await fetch(`${API_BASE_URL}/applications/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Settings API
  async getProfile() {
    const res = await fetch(`${API_BASE_URL}/settings/profile`);
    return handleResponse(res);
  },

  async updateProfile(profileData) {
    const res = await fetch(`${API_BASE_URL}/settings/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    });
    return handleResponse(res);
  },

  async getAppSettings() {
    const res = await fetch(`${API_BASE_URL}/settings/app`);
    return handleResponse(res);
  },

  async updateAppSettings(settingsData) {
    const res = await fetch(`${API_BASE_URL}/settings/app`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settingsData),
    });
    return handleResponse(res);
  },

  async uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/settings/resume`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async getResumes() {
    const res = await fetch(`${API_BASE_URL}/settings/resume`);
    return handleResponse(res);
  },

  async deleteResume(filename) {
    const res = await fetch(`${API_BASE_URL}/settings/resume/${filename}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  async testEmail(recipientEmail) {
    const res = await fetch(`${API_BASE_URL}/settings/test-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient_email: recipientEmail }),
    });
    return handleResponse(res);
  }
};
