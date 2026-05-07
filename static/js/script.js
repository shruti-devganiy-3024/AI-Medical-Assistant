/* =========================================================
   GLOBAL CONFIG
   ========================================================= */
const API_BASE = '/api';

/* =========================================================
   AUTH HELPERS
   ========================================================= */
function getToken() {
  return localStorage.getItem('token');
}

function getUsername() {
  return localStorage.getItem('username') || 'User';
}

function saveAuth(token, username) {
  localStorage.setItem('token', token);
  localStorage.setItem('username', username);
}

function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
}

/**
 * Protect a page — call this at the top of dashboard/chat/etc.
 * Redirects to login if no token is found.
 */
function requireAuth() {
  if (!getToken()) {
    window.location.href = '/';
    return false;
  }
  return true;
}

/* =========================================================
   API WRAPPER (auto-attaches token)
   ========================================================= */
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) headers['Authorization'] = `Token ${token}`;

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 — token expired or invalid
    if (response.status === 401) {
      clearAuth();
      window.location.href = '/';
      throw new Error('Session expired. Please log in again.');
    }

    // Handle 204 No Content (DELETE)
    if (response.status === 204) return null;

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errMsg =
        data.error ||
        data.detail ||
        (typeof data === 'object' ? JSON.stringify(data) : 'Server error, try again');
      throw new Error(errMsg);
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError') {
      throw new Error('Network error. Check your connection.');
    }
    throw err;
  }
}

/* =========================================================
   TOAST NOTIFICATIONS
   ========================================================= */
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* =========================================================
   LOADING OVERLAY
   ========================================================= */
function showLoading(message = 'Loading...') {
  let overlay = document.getElementById('loadingOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `<div class="box"><div class="spinner"></div><span id="loadingText"></span></div>`;
    document.body.appendChild(overlay);
  }
  document.getElementById('loadingText').textContent = message;
  overlay.classList.add('show');
}

function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.remove('show');
}

/* =========================================================
   THEME (DARK MODE)
   ========================================================= */
function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon();
}

function updateThemeIcon() {
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.textContent = isDark ? '☀️' : '🌙';
}

/* =========================================================
   NAVBAR HELPERS
   ========================================================= */
function setupNavbar(activePage) {
  // Highlight current link
  document.querySelectorAll('.nav-links a[data-page]').forEach((a) => {
    if (a.dataset.page === activePage) a.classList.add('active');
  });

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      clearAuth();
      showToast('You have been logged out successfully', 'success');
      setTimeout(() => (window.location.href = '/'), 800);
    });
  }

  // Theme toggle
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // Mobile menu toggle
  const mobileBtn = document.getElementById('mobileToggle');
  const navLinks = document.querySelector('.nav-links');
  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => navLinks.classList.toggle('show'));
  }
}


/* =========================================================
   UTILITIES
   ========================================================= */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/* Initialize theme as soon as script loads */
initTheme();