const API_URL = (typeof window !== 'undefined' && window.API_URL) || (window.localStorage.getItem('API_URL') || window.location.origin);

function getToken() {
  return localStorage.getItem('token');
}

function guardAuthOrRedirect() {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
  }
}

function showAlert(message, type = 'info') {
  const el = document.getElementById('alert');
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = message;
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (_) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
}

async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = options.headers || {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) headers['Content-Type'] = headers['Content-Type'] || 'application/json';

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  let data = null;
  try { data = await res.json(); } catch (_) {}
  return { ok: res.ok, status: res.status, data };
}

async function apiGet(path) {
  return apiRequest(path, { method: 'GET' });
}

async function apiPost(path, body) {
  return apiRequest(path, { method: 'POST', body: JSON.stringify(body) });
}

async function apiDelete(path) {
  return apiRequest(path, { method: 'DELETE' });
}

async function apiUpload(path, file) {
  const form = new FormData();
  form.append('file', file);
  return apiRequest(path, { method: 'POST', body: form, headers: {} });
}


