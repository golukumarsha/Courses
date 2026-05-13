// ─── CONFIG ───────────────────────────────────────────
const BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:8000'
  : window.location.origin;

// ─── STATE ────────────────────────────────────────────
let authToken = null;
let currentUser = null;
let deleteTargetId = null;

// ─── INIT ─────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  showAuthPage();
});

// ─── PAGES ────────────────────────────────────────────
function showAuthPage() {
  document.getElementById('auth-page').style.display = 'flex';
  document.getElementById('dashboard-page').style.display = 'none';
}

function showDashboard() {
  document.getElementById('auth-page').style.display = 'none';
  document.getElementById('dashboard-page').style.display = 'block';
  document.getElementById('base-url').value = BASE_URL;
  document.getElementById('sidebar-url').textContent = BASE_URL;
  setupUserUI();
  loadDashboard();
}

function getBase() { return BASE_URL; }
function updateBaseUrl() {}

// ─── USER UI ──────────────────────────────────────────
function setupUserUI() {
  if (!currentUser) return;
  const name = currentUser.username || '?';
  const role = currentUser.role || 'user';
  document.getElementById('sidebar-avatar').textContent = name[0].toUpperCase();
  document.getElementById('sidebar-username').textContent = name;
  const badge = document.getElementById('sidebar-role-badge');
  badge.textContent = role.toUpperCase();
  badge.className = 'role-badge ' + role;
  document.querySelectorAll('.nav-item.admin-only').forEach(el => {
    el.style.display = (role === 'admin') ? 'flex' : 'none';
  });
}

// ─── AUTH TABS ────────────────────────────────────────
function switchAuthTab(tab, btn) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.auth-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('auth-' + tab).classList.add('active');
  clearAuthMessages();
}

function clearAuthMessages() {
  ['login-error','login-success','register-error','register-success'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.style.display = 'none'; el.textContent = ''; }
  });
}

function showAuthMsg(id, msg, type='error') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  el.className = type === 'error' ? 'auth-error' : 'auth-success';
}

// ─── LOGIN ────────────────────────────────────────────
async function doLogin() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  clearAuthMessages();

  if (!email || !password) { showAuthMsg('login-error', 'Email aur password daalein'); return; }

  const btn = document.getElementById('login-btn');
  btn.disabled = true; btn.textContent = 'Signing in...';

  try {
    const res = await fetch(BASE_URL + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) { showAuthMsg('login-error', data.detail || 'Login failed'); return; }
    authToken = data.access_token;
    currentUser = { username: data.username, role: data.role };
    showAuthMsg('login-success', 'Welcome, ' + data.username + '! Logging in...', 'success');
    setTimeout(showDashboard, 800);
  } catch (e) {
    showAuthMsg('login-error', 'Server se connect nahi hua. Kya uvicorn chal raha hai?');
  } finally {
    btn.disabled = false; btn.textContent = 'Sign In →';
  }
}

// ─── REGISTER ─────────────────────────────────────────
async function doRegister() {
  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const role = document.getElementById('reg-role').value;
  clearAuthMessages();

  // ── Frontend validation (backend se match karta hai) ──
  if (!username || !email || !password) {
    showAuthMsg('register-error', 'Saare fields bharna zaroori hai'); return;
  }
  if (username.length < 3) {
    showAuthMsg('register-error', 'Username kam se kam 3 characters ka hona chahiye'); return;
  }
  if (!/^[a-zA-Z0-9_\.]+$/.test(username)) {
    showAuthMsg('register-error', 'Username mein sirf letters, numbers, _ aur . allowed hain'); return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showAuthMsg('register-error', 'Valid email daalo (e.g. user@example.com)'); return;
  }
  if (password.length < 8) {
    showAuthMsg('register-error', 'Password kam se kam 8 characters ka hona chahiye'); return;
  }
  if (!/[A-Z]/.test(password)) {
    showAuthMsg('register-error', 'Password mein kam se kam 1 uppercase letter hona chahiye (A-Z)'); return;
  }
  if (!/[a-z]/.test(password)) {
    showAuthMsg('register-error', 'Password mein kam se kam 1 lowercase letter hona chahiye (a-z)'); return;
  }
  if (!/\d/.test(password)) {
    showAuthMsg('register-error', 'Password mein kam se kam 1 number hona chahiye (0-9)'); return;
  }
  if (!/[!@#$%^&*()_+\-=\[\]{}|;\':",./<>?]/.test(password)) {
    showAuthMsg('register-error', 'Password mein kam se kam 1 special character chahiye (!@#$% etc)'); return;
  }

  const btn = document.getElementById('register-btn');
  btn.disabled = true; btn.textContent = 'Creating account...';

  try {
    const res = await fetch(BASE_URL + '/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role })
    });
    const data = await res.json();
    if (!res.ok) {
      // 422 validation errors
      if (res.status === 422 && Array.isArray(data.detail)) {
        const msg = data.detail.map(e => e.msg).join(' | ');
        showAuthMsg('register-error', msg);
      } else {
        showAuthMsg('register-error', data.detail || 'Registration failed');
      }
      return;
    }
    showAuthMsg('register-success', 'Account bana! Ab Sign In karein, ' + username, 'success');
    setTimeout(() => {
      document.querySelectorAll('.auth-tab')[0].click();
      document.getElementById('login-email').value = email;
    }, 1200);
  } catch (e) {
    showAuthMsg('register-error', 'Server se connect nahi hua. Kya uvicorn chal raha hai?');
  } finally {
    btn.disabled = false; btn.textContent = 'Create Account →';
  }
}

// ─── LOGOUT ───────────────────────────────────────────
function doLogout() {
  authToken = null; currentUser = null;
  toast('Signed out', 'info');
  setTimeout(showAuthPage, 500);
}

// ─── API HELPER ───────────────────────────────────────
async function api(method, path, body=null) {
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BASE_URL + path, opts);
  if (res.status === 401) { toast('Session expire — dobara login karein', 'error'); doLogout(); throw new Error('Unauthorized'); }
  let data;
  try {
    data = await res.json();
  } catch(e) {
    const text = await res.text().catch(() => 'Server error');
    data = { detail: 'Server error: ' + res.status + ' — ' + text.substring(0, 100) };
  }
  // ── 422 Validation errors — readable banao ──────────
  if (res.status === 422 && data.detail && Array.isArray(data.detail)) {
    const msgs = data.detail.map(err => {
      const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
      return `• <strong>${field}</strong>: ${err.msg}`;
    });
    showValidationErrors(msgs);
    data._validationMessages = msgs;
  }
  return { ok: res.ok, status: res.status, data };
}

// ─── VALIDATION ERROR POPUP ───────────────────────────
function showValidationErrors(msgs) {
  // Remove old popup if any
  const old = document.getElementById('validation-popup');
  if (old) old.remove();

  const popup = document.createElement('div');
  popup.id = 'validation-popup';
  popup.className = 'validation-popup';
  popup.innerHTML = `
    <div class="vp-header">
      <span>⚠️ Validation Errors</span>
      <button onclick="document.getElementById('validation-popup').remove()">✕</button>
    </div>
    <div class="vp-body">${msgs.join('<br>')}</div>
  `;
  document.body.appendChild(popup);
  // Auto remove after 8 seconds
  setTimeout(() => { if (popup.parentNode) popup.remove(); }, 8000);
  toast('Validation error — fields check karein ⚠️', 'error');
}

// ─── TOAST ────────────────────────────────────────────
function toast(msg, type='info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  const icons = { success:'✅', error:'❌', info:'ℹ️' };
  el.innerHTML = '<span>' + (icons[type]||'ℹ️') + '</span><span>' + msg + '</span>';
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ─── RESPONSE BOX ─────────────────────────────────────
function showResponse(section, data, statusText, ok) {
  const raw = document.getElementById(section+'-raw');
  const status = document.getElementById(section+'-status');
  if (raw) raw.textContent = JSON.stringify(data, null, 2);
  if (status) { status.textContent = statusText; status.className = 'status-pill ' + (ok ? 'status-ok' : 'status-error'); }
}
function setLoading(section) {
  const status = document.getElementById(section+'-status');
  if (status) { status.innerHTML = '<span class="loading-dots"><span></span><span></span><span></span></span>'; status.className = 'status-pill status-pending'; }
}

// ─── NAVIGATION ───────────────────────────────────────
const tabTitles = { dashboard:'Dashboard', courses:'All Courses', 'get-one':'Get by ID', create:'Create Course', update:'Update Course', delete:'Delete Course', search:'Search', sort:'Sort Courses', filter:'Filter Courses', pagination:'Pagination', analytics:'Analytics', reviews:'Reviews & Ratings', 'top-rated':'Top Rated Courses', 'my-reviews':'My Reviews', enroll:'Enroll in Course', 'my-enrollments':'My Enrollments', 'all-enrollments':'All Enrollments', 'top-courses':'Top Enrolled Courses', 'my-account':'My Account' };

function switchTab(name, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const section = document.getElementById('section-' + name);
  if (section) section.classList.add('active');
  if (btn) btn.classList.add('active');
  document.getElementById('topbar-title').textContent = tabTitles[name] || name;
  ['create','update','delete'].forEach(p => {
    if (name === p) {
      const banner = document.getElementById(p + '-admin-banner');
      if (banner) banner.style.display = (currentUser && currentUser.role === 'admin') ? 'none' : 'flex';
    }
  });
  if (name === 'my-account')       loadMyAccount();
  if (name === 'analytics')        loadAllAnalytics();
  if (name === 'top-rated')        loadTopRated();
  if (name === 'my-reviews')       loadMyReviews();
  if (name === 'my-enrollments')   loadMyEnrollments();
  if (name === 'all-enrollments')  loadAllEnrollments();
  if (name === 'top-courses')      loadTopEnrolled();
}

// ─── PING ─────────────────────────────────────────────
async function pingApi() {
  try {
    const r = await api('GET', '/home');
    toast(r.ok ? '✅ API Online!' : '⚠️ Error', r.ok ? 'success' : 'error');
  } catch(e) { toast('❌ Cannot reach API', 'error'); }
}

// ─── DASHBOARD ────────────────────────────────────────
async function loadDashboard() {
  try {
    const r = await api('GET', '/courses');
    if (!r.ok) return;
    const courses = r.data;
    document.getElementById('stat-total').textContent = courses.length;
    document.getElementById('stat-published').textContent = courses.filter(c => c.is_published).length;
    document.getElementById('stat-draft').textContent = courses.filter(c => !c.is_published).length;
    document.getElementById('stat-cats').textContent = new Set(courses.map(c => c.category)).size;
    document.getElementById('dashboard-table').innerHTML = courses.slice(0,8).map(c =>
      '<tr><td><strong>#'+c.id+'</strong></td><td>'+c.title+'</td><td>'+c.instructor+'</td><td><span class="pill cat">'+c.category+'</span></td><td><span class="price-tag">₹'+c.price+'</span></td><td><span class="pill '+(c.is_published?'published':'draft')+'">'+(c.is_published?'Published':'Draft')+'</span></td></tr>'
    ).join('');
  } catch(e) {}
}

// ─── ALL COURSES ──────────────────────────────────────
async function getAllCourses() {
  const isAdmin = currentUser && currentUser.role === 'admin';
  try {
    const r = await api('GET', '/courses');
    document.getElementById('all-courses-response').style.display = 'block';
    document.getElementById('all-courses-raw').textContent = JSON.stringify(r.data, null, 2);
    document.getElementById('all-courses-status').textContent = r.status + (r.ok ? ' OK' : ' Error');
    document.getElementById('all-courses-status').className = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (!r.ok) { toast('Failed to load courses', 'error'); return; }
    document.getElementById('all-courses-table').innerHTML = r.data.map(c =>
      '<tr><td><strong>#'+c.id+'</strong></td><td>'+c.title+'</td><td>'+c.instructor+'</td><td><span class="pill cat">'+c.category+'</span></td><td><span class="price-tag">₹'+c.price+'</span></td><td>'+c.duration_hours+'h</td><td><span class="pill '+(c.is_published?'published':'draft')+'">'+(c.is_published?'Published':'Draft')+'</span></td><td>'+(c.discount_percent?'<span class="discount-tag">'+c.discount_percent+'% OFF</span>':'—')+'</td><td class="actions-cell"><button class="icon-btn" onclick="quickEdit('+c.id+')" '+(isAdmin?'':'disabled')+'>✏️</button><button class="icon-btn del" onclick="quickDelete('+c.id+')" '+(isAdmin?'':'disabled')+'>🗑️</button></td></tr>'
    ).join('');
    toast(r.data.length + ' courses loaded', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// ─── GET ONE ──────────────────────────────────────────
async function getCourseById() {
  const id = document.getElementById('get-id').value;
  if (!id) { toast('Course ID daalein', 'error'); return; }
  setLoading('get-one');
  try {
    const r = await api('GET', '/course/' + id);
    showResponse('get-one', r.data, r.status + (r.ok?' OK':' Error'), r.ok);
    if (r.ok) toast('Course #'+id+' mila!', 'success');
    else toast(r.data.detail || 'Not found', 'error');
  } catch(e) { showResponse('get-one', {error: e.message}, 'Error', false); }
}

// ─── CREATE ───────────────────────────────────────────
async function createCourse() {
  if (!currentUser || currentUser.role !== 'admin') { toast('Sirf Admin create kar sakta hai 🚫', 'error'); return; }
  const title = document.getElementById('c-title').value.trim();
  const instructor = document.getElementById('c-instructor').value.trim();
  const category = document.getElementById('c-category').value.trim();
  const price = parseFloat(document.getElementById('c-price').value);
  const duration = parseInt(document.getElementById('c-duration').value);
  const discount = document.getElementById('c-discount').value;
  const published = document.getElementById('c-published').checked;
  if (!title || !instructor || !category || isNaN(price) || isNaN(duration)) { toast('Saare required fields bharo', 'error'); return; }
  const body = { title, instructor, category, price, duration_hours: duration, is_published: published };
  if (discount) body.discount_percent = parseFloat(discount);
  setLoading('create');
  try {
    const r = await api('POST', '/create', body);
    showResponse('create', r.data, r.status + (r.ok?' Created':' Error'), r.ok);
    if (r.ok) { toast('Course created! ✅', 'success'); clearCreateForm(); }
    else toast(r.data.detail || 'Create failed', 'error');
  } catch(e) { showResponse('create', {error: e.message}, 'Error', false); }
}
function clearCreateForm() {
  ['c-title','c-instructor','c-category','c-price','c-duration','c-discount'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('c-published').checked = false;
}

// ─── UPDATE ───────────────────────────────────────────
async function prefillUpdate() {
  const id = document.getElementById('u-id').value;
  if (!id) { toast('ID pehle daalo', 'error'); return; }
  try {
    const r = await api('GET', '/course/' + id);
    if (!r.ok) { toast('Course not found', 'error'); return; }
    const c = r.data;
    document.getElementById('u-title').value = c.title || '';
    document.getElementById('u-instructor').value = c.instructor || '';
    document.getElementById('u-category').value = c.category || '';
    document.getElementById('u-price').value = c.price || '';
    document.getElementById('u-duration').value = c.duration_hours || '';
    document.getElementById('u-discount').value = c.discount_percent || '';
    document.getElementById('u-published').checked = !!c.is_published;
    toast('Data prefilled ✅', 'info');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}
async function updateCourse() {
  if (!currentUser || currentUser.role !== 'admin') { toast('Sirf Admin update kar sakta hai 🚫', 'error'); return; }
  const id = document.getElementById('u-id').value;
  const title = document.getElementById('u-title').value.trim();
  const instructor = document.getElementById('u-instructor').value.trim();
  const category = document.getElementById('u-category').value.trim();
  const price = parseFloat(document.getElementById('u-price').value);
  const duration = parseInt(document.getElementById('u-duration').value);
  const discount = document.getElementById('u-discount').value;
  const published = document.getElementById('u-published').checked;
  if (!id||!title||!instructor||!category||isNaN(price)||isNaN(duration)) { toast('Saare required fields bharo', 'error'); return; }
  const body = { title, instructor, category, price, duration_hours: duration, is_published: published };
  if (discount) body.discount_percent = parseFloat(discount);
  setLoading('update');
  try {
    const r = await api('PUT', '/update/' + id, body);
    showResponse('update', r.data, r.status + (r.ok?' Updated':' Error'), r.ok);
    if (r.ok) toast('Course #'+id+' updated! ✅', 'success');
    else toast(r.data.detail || 'Update failed', 'error');
  } catch(e) { showResponse('update', {error: e.message}, 'Error', false); }
}
function clearUpdateForm() {
  ['u-id','u-title','u-instructor','u-category','u-price','u-duration','u-discount'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('u-published').checked = false;
}

// ─── DELETE ───────────────────────────────────────────
function confirmDelete() {
  if (!currentUser || currentUser.role !== 'admin') { toast('Sirf Admin delete kar sakta hai 🚫', 'error'); return; }
  const id = document.getElementById('d-id').value;
  if (!id) { toast('Course ID daalo', 'error'); return; }
  deleteTargetId = id;
  document.getElementById('modal-id').textContent = '#' + id;
  document.getElementById('delete-modal').classList.add('open');
}
function closeModal() { document.getElementById('delete-modal').classList.remove('open'); deleteTargetId = null; }
async function doDelete() {
  closeModal();
  const id = deleteTargetId || document.getElementById('d-id').value;
  if (!id) return;
  setLoading('delete');
  try {
    const r = await api('DELETE', '/delete/' + id);
    showResponse('delete', r.data, r.status + (r.ok?' Deleted':' Error'), r.ok);
    if (r.ok) { toast('Course #'+id+' deleted ✅', 'success'); document.getElementById('d-id').value = ''; }
    else toast(r.data.detail || 'Delete failed', 'error');
  } catch(e) { showResponse('delete', {error: e.message}, 'Error', false); }
}
function quickEdit(id) { switchTab('update', null); document.getElementById('u-id').value = id; prefillUpdate(); }
function quickDelete(id) { switchTab('delete', null); document.getElementById('d-id').value = id; confirmDelete(); }

// ─── FILTER ───────────────────────────────────────────
async function filterCourses() {
  const params = new URLSearchParams();
  const cat = document.getElementById('f-category').value.trim();
  const inst = document.getElementById('f-instructor').value.trim();
  const minPrice = document.getElementById('f-min-price').value;
  const maxPrice = document.getElementById('f-max-price').value;
  const pub = document.getElementById('f-published').value;
  if (cat) params.set('category', cat);
  if (inst) params.set('instructor', inst);
  if (minPrice) params.set('min_price', minPrice);
  if (maxPrice) params.set('max_price', maxPrice);
  if (pub !== '') params.set('is_published', pub);
  try {
    const headers = {};
    if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
    const res = await fetch(BASE_URL + '/filter?' + params, { headers });
    const data = await res.json();
    document.getElementById('filter-response').style.display = 'block';
    document.getElementById('filter-raw').textContent = JSON.stringify(data, null, 2);
    document.getElementById('filter-status').textContent = res.status + (res.ok?' OK':' Error');
    document.getElementById('filter-status').className = 'status-pill ' + (res.ok ? 'status-ok' : 'status-error');
    if (!data.length) { document.getElementById('filter-table').innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Koi course nahi mila</p></div></td></tr>'; return; }
    document.getElementById('filter-table').innerHTML = data.map(c =>
      '<tr><td><strong>#'+c.id+'</strong></td><td>'+c.title+'</td><td>'+c.instructor+'</td><td><span class="pill cat">'+c.category+'</span></td><td><span class="price-tag">₹'+c.price+'</span></td><td><span class="pill '+(c.is_published?'published':'draft')+'">'+(c.is_published?'Published':'Draft')+'</span></td></tr>'
    ).join('');
    toast(data.length + ' course(s) mila', 'success');
  } catch(e) { toast('Filter error: ' + e.message, 'error'); }
}
function clearFilters() {
  ['f-category','f-instructor','f-min-price','f-max-price'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('f-published').value = '';
}

// ─── PAGINATION ───────────────────────────────────────
async function paginateCourses(page) {
  if (page) document.getElementById('p-page').value = page;
  const pg = parseInt(document.getElementById('p-page').value) || 1;
  const lim = parseInt(document.getElementById('p-limit').value) || 5;
  try {
    const headers = {};
    if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
    const res = await fetch(BASE_URL + '/items?page=' + pg + '&limit=' + lim, { headers });
    const data = await res.json();
    document.getElementById('pagination-response').style.display = 'block';
    document.getElementById('pagination-raw').textContent = JSON.stringify(data, null, 2);
    document.getElementById('pagination-status').textContent = res.status + (res.ok?' OK':' Error');
    document.getElementById('pagination-status').className = 'status-pill ' + (res.ok ? 'status-ok' : 'status-error');
    if (!data.data||!data.data.length) { document.getElementById('pagination-table').innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Is page pe koi course nahi</p></div></td></tr>'; return; }
    document.getElementById('pagination-table').innerHTML = data.data.map(c =>
      '<tr><td><strong>#'+c.id+'</strong></td><td>'+c.title+'</td><td>'+c.instructor+'</td><td><span class="pill cat">'+c.category+'</span></td><td><span class="price-tag">₹'+c.price+'</span></td><td><span class="pill '+(c.is_published?'published':'draft')+'">'+(c.is_published?'Published':'Draft')+'</span></td></tr>'
    ).join('');
    const totalPages = data.total_pages || Math.ceil(data.total / lim);
    document.getElementById('page-info-bar').style.display = 'flex';
    document.getElementById('page-info-text').textContent = 'Page ' + pg + ' of ' + totalPages + ' · ' + data.total + ' total';
    document.getElementById('pagination-controls').innerHTML =
      (pg>1 ? '<button class="btn btn-outline btn-sm" onclick="paginateCourses('+(pg-1)+')">← Prev</button>' : '') +
      '<span style="padding:0 8px;font-size:0.85rem;color:var(--text-muted);">'+pg+' / '+totalPages+'</span>' +
      (pg<totalPages ? '<button class="btn btn-gold btn-sm" onclick="paginateCourses('+(pg+1)+')">Next →</button>' : '');
    toast('Page ' + pg + ' loaded', 'success');
  } catch(e) { toast('Pagination error: ' + e.message, 'error'); }
}

// ─── MY ACCOUNT ───────────────────────────────────────
async function loadMyAccount() {
  try {
    const r = await api('GET', '/auth/me');
    if (!r.ok) return;
    const u = r.data;
    document.getElementById('account-info').style.display = 'block';
    document.getElementById('acc-username').textContent = u.username;
    document.getElementById('acc-email').textContent = u.email;
    document.getElementById('acc-id').textContent = '#' + u.id;
    document.getElementById('acc-role').innerHTML = '<span class="role-badge ' + u.role + '" style="font-size:0.85rem;padding:4px 12px;">' + u.role.toUpperCase() + '</span>';
    document.getElementById('acc-token').textContent = authToken || '—';
  } catch(e) {}
}

// ─── ENROLLMENTS ──────────────────────────────────────

function formatDateShort(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}

function statusBadge(status) {
  const map = {
    active:    'pill published',
    completed: 'pill',
    cancelled: 'pill draft'
  };
  const style = {
    active:    '',
    completed: 'background:var(--teal-pale);color:var(--teal);',
    cancelled: ''
  };
  return `<span class="${map[status]||'pill'}" style="${style[status]||''}">${status}</span>`;
}

async function enrollCourse() {
  const courseId = document.getElementById('en-course-id').value;
  if (!courseId) { toast('Course ID daalo', 'error'); return; }
  const respBox  = document.getElementById('en-response');
  const statusEl = document.getElementById('en-status-pill');
  const rawPre   = document.getElementById('en-raw');
  respBox.style.display = 'block';
  statusEl.textContent  = 'Processing...';
  try {
    const r = await api('POST', '/enrollments/enroll/' + courseId, {});
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' OK' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) toast('Successfully enrolled! 🎓', 'success');
    else toast(r.data.detail || 'Error', 'error');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function cancelEnrollment() {
  const courseId = document.getElementById('en-course-id').value;
  if (!courseId) { toast('Course ID daalo', 'error'); return; }
  if (!confirm('Enrollment cancel karna chahte hain?')) return;
  const respBox  = document.getElementById('en-response');
  const statusEl = document.getElementById('en-status-pill');
  const rawPre   = document.getElementById('en-raw');
  respBox.style.display = 'block';
  try {
    const r = await api('DELETE', '/enrollments/cancel/' + courseId);
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' OK' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) toast('Enrollment cancel ho gaya ✅', 'success');
    else toast(r.data.detail || 'Error', 'error');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function updateEnrollStatus() {
  const courseId = document.getElementById('en-status-course-id').value;
  const status   = document.getElementById('en-status-val').value;
  if (!courseId) { toast('Course ID daalo', 'error'); return; }
  const respBox  = document.getElementById('en-response');
  const statusEl = document.getElementById('en-status-pill');
  const rawPre   = document.getElementById('en-raw');
  respBox.style.display = 'block';
  try {
    const r = await api('PUT', '/enrollments/status/' + courseId, { status });
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' Updated' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) toast('Status update ho gaya ✅', 'success');
    else toast(r.data.detail || 'Error', 'error');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function loadMyEnrollments() {
  const tbody   = document.getElementById('my-en-table');
  const statsEl = document.getElementById('my-en-stats');
  tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const r = await api('GET', '/enrollments/my');
    if (!r.ok) { toast(r.data.detail || 'Error', 'error'); return; }
    const d = r.data;
    statsEl.style.display = 'flex';
    document.getElementById('my-en-active').textContent    = d.stats.active;
    document.getElementById('my-en-completed').textContent = d.stats.completed;
    document.getElementById('my-en-cancelled').textContent = d.stats.cancelled;
    document.getElementById('my-en-total').textContent     = d.stats.total;
    if (!d.enrollments.length) {
      tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="icon">📚</div><p>Koi enrollment nahi. Koi course enroll karo!</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = d.enrollments.map(e => `
      <tr>
        <td><strong>#${e.course_id}</strong> ${e.course_title}</td>
        <td>${e.instructor}</td>
        <td><span class="pill cat">${e.category}</span></td>
        <td><span class="price-tag">₹${e.discounted_price ?? e.price}</span></td>
        <td>${statusBadge(e.status)}</td>
        <td style="color:var(--text-muted);font-size:0.82rem">${formatDateShort(e.enrolled_at)}</td>
      </tr>`).join('');
    toast(`${d.stats.total} enrollment(s) loaded`, 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function loadAllEnrollments() {
  const tbody   = document.getElementById('all-en-table');
  const statsEl = document.getElementById('all-en-stats');
  tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const r = await api('GET', '/enrollments/all');
    if (!r.ok) { toast(r.data.detail || 'Admin access chahiye', 'error'); return; }
    const d = r.data;
    statsEl.style.display = 'flex';
    document.getElementById('all-en-active').textContent    = d.stats.active;
    document.getElementById('all-en-completed').textContent = d.stats.completed;
    document.getElementById('all-en-cancelled').textContent = d.stats.cancelled;
    document.getElementById('all-en-total').textContent     = d.stats.total;
    if (!d.enrollments.length) {
      tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="icon">👥</div><p>Koi enrollment nahi abhi tak</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = d.enrollments.map(e => `
      <tr>
        <td><strong>${e.username}</strong></td>
        <td>#${e.course_id} ${e.course_title}</td>
        <td><span class="pill cat">${e.category}</span></td>
        <td>${e.instructor}</td>
        <td>${statusBadge(e.status)}</td>
        <td style="color:var(--text-muted);font-size:0.82rem">${formatDateShort(e.enrolled_at)}</td>
      </tr>`).join('');
    toast(`${d.stats.total} enrollment(s) loaded`, 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function loadTopEnrolled() {
  const tbody = document.getElementById('top-courses-table');
  tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res  = await fetch(BASE_URL + '/enrollments/top-courses');
    const data = await res.json();
    if (!res.ok || !data.top_courses.length) {
      tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="icon">🔥</div><p>Koi enrollment nahi abhi tak</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = data.top_courses.map((c, i) => `
      <tr>
        <td><strong>#${i+1}</strong>${i===0?' 🥇':i===1?' 🥈':i===2?' 🥉':''}</td>
        <td><strong>${c.title}</strong></td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td><strong>${c.total_enrollments}</strong></td>
        <td style="color:var(--teal)">${c.completed_enrollments}</td>
      </tr>`).join('');
    toast('Top courses loaded 🔥', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// ─── REVIEWS & RATINGS ────────────────────────────────

let selectedRating = 0;

function setStarRating(val) {
  selectedRating = val;
  document.getElementById('rv-rating').value = val;
  document.querySelectorAll('#star-picker .star').forEach((s, i) => {
    s.classList.toggle('active', i < val);
  });
}

function starsHTML(rating, size = 'sm') {
  const full  = Math.floor(rating);
  const empty = 5 - full;
  return '<span class="stars stars-' + size + '">' +
    '★'.repeat(full) + '<span class="stars-empty">' + '★'.repeat(empty) + '</span>' +
    '</span>';
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}

// Load all reviews for a course
async function loadCourseReviews() {
  const id = document.getElementById('rv-course-id').value;
  if (!id) { toast('Course ID daalo', 'error'); return; }
  const listDiv  = document.getElementById('rv-list');
  const summDiv  = document.getElementById('rv-summary');
  listDiv.innerHTML = '<div class="empty-state"><p>Loading...</p></div>';
  summDiv.style.display = 'none';
  try {
    const res  = await fetch(BASE_URL + '/reviews/course/' + id);
    const data = await res.json();
    if (!res.ok) { toast(data.detail || 'Error', 'error'); listDiv.innerHTML = ''; return; }

    const stats = data.stats;
    const total = Number(stats.total_reviews);

    if (total === 0) {
      summDiv.style.display = 'none';
      listDiv.innerHTML = '<div class="empty-state"><div class="icon">💬</div><p>Is course pe abhi koi review nahi. Pehle review lijiye!</p></div>';
      return;
    }

    // Summary box
    summDiv.style.display = 'flex';
    document.getElementById('rv-avg-score').textContent  = stats.avg_rating ?? '—';
    document.getElementById('rv-avg-stars').innerHTML    = starsHTML(stats.avg_rating, 'lg');
    document.getElementById('rv-total-text').textContent = total + ' review' + (total > 1 ? 's' : '');

    const bars = [5,4,3,2,1].map(n => {
      const cnt  = Number(stats[['','one','two','three','four','five'][n] + '_star'] || 0);
      const pct  = total ? Math.round(cnt / total * 100) : 0;
      return `<div class="rv-bar-row">
        <span class="rv-bar-label">${starsHTML(n,'xs')}</span>
        <div class="rv-bar-track"><div class="rv-bar-fill" style="width:${pct}%"></div></div>
        <span class="rv-bar-count">${cnt}</span>
      </div>`;
    }).join('');
    document.getElementById('rv-bar-chart').innerHTML = bars;

    // Reviews list
    listDiv.innerHTML = data.reviews.map(r => `
      <div class="rv-card">
        <div class="rv-card-top">
          <div class="rv-avatar">${r.username[0].toUpperCase()}</div>
          <div class="rv-meta">
            <div class="rv-username">${r.username}</div>
            <div class="rv-date">${formatDate(r.created_at)}</div>
          </div>
          <div class="rv-rating-badge">${starsHTML(r.rating,'sm')} <strong>${r.rating}</strong>/5</div>
        </div>
        ${r.review ? `<div class="rv-text">${r.review}</div>` : ''}
      </div>`).join('');

    // Auto-fill submit form course id
    document.getElementById('rv-submit-course-id').value = id;
    toast(`${total} review(s) loaded`, 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// Submit new review
async function submitReview() {
  const courseId = document.getElementById('rv-submit-course-id').value;
  const rating   = parseInt(document.getElementById('rv-rating').value);
  const review   = document.getElementById('rv-text').value.trim();
  if (!courseId)       { toast('Course ID daalo', 'error'); return; }
  if (!rating || rating < 1) { toast('Rating select karein (1–5 stars)', 'error'); return; }

  const respBox  = document.getElementById('rv-submit-response');
  const statusEl = document.getElementById('rv-submit-status');
  const rawPre   = document.getElementById('rv-submit-raw');
  respBox.style.display = 'block';
  statusEl.textContent  = 'Submitting...';

  try {
    const r = await api('POST', '/reviews/course/' + courseId, { rating, review: review || null });
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' Created' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) {
      toast('Review submit ho gaya! ⭐', 'success');
      document.getElementById('rv-text').value = '';
      setStarRating(0);
      document.getElementById('rv-course-id').value = courseId;
      loadCourseReviews();
    } else {
      toast(r.data.detail || 'Submit failed', 'error');
    }
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// Update existing review
async function updateReview() {
  const courseId = document.getElementById('rv-submit-course-id').value;
  const rating   = parseInt(document.getElementById('rv-rating').value);
  const review   = document.getElementById('rv-text').value.trim();
  if (!courseId)       { toast('Course ID daalo', 'error'); return; }
  if (!rating || rating < 1) { toast('Rating select karein (1–5 stars)', 'error'); return; }

  const respBox  = document.getElementById('rv-submit-response');
  const statusEl = document.getElementById('rv-submit-status');
  const rawPre   = document.getElementById('rv-submit-raw');
  respBox.style.display = 'block';

  try {
    const r = await api('PUT', '/reviews/course/' + courseId, { rating, review: review || null });
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' Updated' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) {
      toast('Review update ho gaya! ✅', 'success');
      document.getElementById('rv-course-id').value = courseId;
      loadCourseReviews();
    } else {
      toast(r.data.detail || 'Update failed', 'error');
    }
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// Delete my review
async function deleteMyReview() {
  const courseId = document.getElementById('rv-submit-course-id').value;
  if (!courseId) { toast('Course ID daalo', 'error'); return; }
  if (!confirm('Apna review delete karna chahte hain?')) return;

  const respBox  = document.getElementById('rv-submit-response');
  const statusEl = document.getElementById('rv-submit-status');
  const rawPre   = document.getElementById('rv-submit-raw');
  respBox.style.display = 'block';

  try {
    const r = await api('DELETE', '/reviews/course/' + courseId);
    rawPre.textContent   = JSON.stringify(r.data, null, 2);
    statusEl.textContent = r.status + (r.ok ? ' Deleted' : ' Error');
    statusEl.className   = 'status-pill ' + (r.ok ? 'status-ok' : 'status-error');
    if (r.ok) {
      toast('Review delete ho gaya ✅', 'success');
      document.getElementById('rv-course-id').value = courseId;
      loadCourseReviews();
    } else {
      toast(r.data.detail || 'Delete failed', 'error');
    }
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// Top rated courses
async function loadTopRated() {
  const tbody = document.getElementById('top-rated-table');
  tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res  = await fetch(BASE_URL + '/reviews/top-rated');
    const data = await res.json();
    if (!res.ok || !data.top_rated.length) {
      tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="icon">🏅</div><p>Abhi koi rated course nahi. Kuch reviews dijiye!</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = data.top_rated.map((c, i) => `
      <tr>
        <td><strong>#${i+1}</strong>${i===0?' 🥇':i===1?' 🥈':i===2?' 🥉':''}</td>
        <td><strong>${c.title}</strong></td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td>
          ${starsHTML(c.avg_rating, 'sm')}
          <strong style="margin-left:4px">${c.avg_rating}</strong>
        </td>
        <td>${c.total_reviews}</td>
      </tr>`).join('');
    toast(data.top_rated.length + ' courses loaded', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// My all reviews
async function loadMyReviews() {
  const tbody = document.getElementById('my-reviews-table');
  tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const r = await api('GET', '/reviews/my/all');
    if (!r.ok) { toast(r.data.detail || 'Error', 'error'); return; }
    const reviews = r.data.reviews || [];
    if (!reviews.length) {
      tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="icon">📝</div><p>Aapne abhi koi review nahi diya</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = reviews.map(rv => `
      <tr>
        <td><strong>#${rv.course_id}</strong> — ${rv.course_title}</td>
        <td>${starsHTML(rv.rating,'sm')} <strong>${rv.rating}</strong>/5</td>
        <td>${rv.review || '<span style="color:var(--text-muted)">—</span>'}</td>
        <td style="color:var(--text-muted);font-size:0.82rem">${formatDate(rv.created_at)}</td>
      </tr>`).join('');
    toast(`${reviews.length} review(s) loaded`, 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// ─── SORT ─────────────────────────────────────────────
let sortField = 'price';
let sortOrder = 'asc';
let sortPub   = null;   // null=all, true=published, false=draft

function setSortField(btn) {
  document.querySelectorAll('.sort-chip[data-field]').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  sortField = btn.dataset.field;
  updateSortInfo();
  updateSortArrows();
}

function setSortFieldByCol(field) {
  // Click on table header — toggle order if same field
  if (sortField === field) {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  } else {
    sortField = field;
    sortOrder = 'asc';
  }
  // Sync chips
  document.querySelectorAll('.sort-chip[data-field]').forEach(b => {
    b.classList.toggle('active', b.dataset.field === field);
  });
  document.getElementById('sort-asc').classList.toggle('active',  sortOrder === 'asc');
  document.getElementById('sort-desc').classList.toggle('active', sortOrder === 'desc');
  updateSortInfo();
  updateSortArrows();
  applySorting();
}

function setSortOrder(order, btn) {
  document.getElementById('sort-asc').classList.remove('active');
  document.getElementById('sort-desc').classList.remove('active');
  btn.classList.add('active');
  sortOrder = order;
  updateSortInfo();
  updateSortArrows();
}

function setSortPub(val, btn) {
  document.getElementById('pub-all').classList.remove('active');
  document.getElementById('pub-yes').classList.remove('active');
  document.getElementById('pub-no').classList.remove('active');
  btn.classList.add('active');
  sortPub = val;
  updateSortInfo();
}

function updateSortInfo() {
  const pubText = sortPub === null ? 'All' : sortPub ? 'Published only' : 'Drafts only';
  document.getElementById('sort-info-text').innerHTML =
    `Sorting by <strong>${sortField}</strong> · <strong>${sortOrder}ending</strong> · <strong>${pubText}</strong>`;
}

function updateSortArrows() {
  const fields = ['id','title','instructor','category','price','duration_hours','discount_percent'];
  fields.forEach(f => {
    const el = document.getElementById('arr-' + f);
    if (!el) return;
    if (f === sortField) el.textContent = sortOrder === 'asc' ? '↑' : '↓';
    else el.textContent = '';
  });
}

function resetSort() {
  sortField = 'price'; sortOrder = 'asc'; sortPub = null;
  document.querySelectorAll('.sort-chip[data-field]').forEach(b => b.classList.toggle('active', b.dataset.field === 'price'));
  document.getElementById('sort-asc').classList.add('active');
  document.getElementById('sort-desc').classList.remove('active');
  document.getElementById('pub-all').classList.add('active');
  document.getElementById('pub-yes').classList.remove('active');
  document.getElementById('pub-no').classList.remove('active');
  document.getElementById('sort-table').innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="icon">📊</div><p>Sort options chuniye aur Apply dabao</p></div></td></tr>';
  document.getElementById('sort-response').style.display = 'none';
  document.getElementById('sort-result-info').style.display = 'none';
  updateSortInfo();
  updateSortArrows();
}

async function applySorting() {
  const tbody    = document.getElementById('sort-table');
  const respBox  = document.getElementById('sort-response');
  const rawPre   = document.getElementById('sort-raw');
  const statusEl = document.getElementById('sort-status');
  const infoDiv  = document.getElementById('sort-result-info');
  const countEl  = document.getElementById('sort-count-text');

  tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  respBox.style.display = 'none';

  let url = `${BASE_URL}/sort?sort_by=${sortField}&order=${sortOrder}`;
  if (sortPub !== null) url += `&is_published=${sortPub}`;

  try {
    const res  = await fetch(url);
    const data = await res.json();

    respBox.style.display  = 'block';
    rawPre.textContent     = JSON.stringify(data, null, 2);
    statusEl.textContent   = res.status + (res.ok ? ' OK' : ' Error');
    statusEl.className     = 'status-pill ' + (res.ok ? 'status-ok' : 'status-error');

    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><p>Error: ${data.detail}</p></div></td></tr>`;
      toast(data.detail || 'Error', 'error');
      return;
    }

    const results = data.data || [];
    infoDiv.style.display  = 'block';
    countEl.textContent    = `${results.length} course${results.length !== 1 ? 's' : ''} — sorted by ${sortField} (${sortOrder})`;

    if (!results.length) {
      tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="icon">😕</div><p>Koi course nahi mila</p></div></td></tr>';
      return;
    }

    tbody.innerHTML = results.map(c => `
      <tr>
        <td><strong>#${c.id}</strong></td>
        <td>${c.title}</td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag ${sortField==='price'?'sort-highlight-cell':''}">₹${c.price}</span></td>
        <td class="${sortField==='duration_hours'?'sort-highlight-cell':''}">${c.duration_hours}h</td>
        <td class="${sortField==='discount_percent'?'sort-highlight-cell':''}">${c.discount_percent ? '<span class="discount-tag">'+c.discount_percent+'% OFF</span>' : '—'}</td>
        <td><span class="pill ${c.is_published?'published':'draft'}">${c.is_published?'Published':'Draft'}</span></td>
      </tr>`).join('');

    updateSortArrows();
    toast(`${results.length} courses sorted by ${sortField} ↑↓`, 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// ─── SEARCH ───────────────────────────────────────────
async function doSearch() {
  const q = document.getElementById('search-q').value.trim();
  if (!q) { toast('Kuch type karein search ke liye', 'error'); return; }

  const tbody   = document.getElementById('search-table');
  const respBox = document.getElementById('search-response');
  const rawPre  = document.getElementById('search-raw');
  const statusEl = document.getElementById('search-status');
  const infoDiv = document.getElementById('search-result-info');
  const countEl = document.getElementById('search-count-text');

  tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="icon">⏳</div><p>Searching...</p></div></td></tr>';
  respBox.style.display = 'none';

  try {
    const res  = await fetch(BASE_URL + '/search?q=' + encodeURIComponent(q));
    const data = await res.json();

    respBox.style.display = 'block';
    rawPre.textContent = JSON.stringify(data, null, 2);
    statusEl.textContent  = res.status + (res.ok ? ' OK' : ' Error');
    statusEl.className    = 'status-pill ' + (res.ok ? 'status-ok' : 'status-error');

    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><p>Error: ${data.detail || 'Something went wrong'}</p></div></td></tr>`;
      return;
    }

    const results = data.results || [];
    infoDiv.style.display = 'block';

    if (!results.length) {
      countEl.textContent = `"${q}" ke liye koi result nahi mila`;
      countEl.className   = 'search-result-count no-result';
      tbody.innerHTML     = `<tr><td colspan="8"><div class="empty-state"><div class="icon">😕</div><p>Koi course nahi mila "<strong>${q}</strong>" ke liye</p></div></td></tr>`;
      return;
    }

    countEl.textContent = `${results.length} course${results.length > 1 ? 's' : ''} mila "${q}" ke liye`;
    countEl.className   = 'search-result-count has-result';

    tbody.innerHTML = results.map(c => {
      const titleHL      = highlight(c.title,      q);
      const instrHL      = highlight(c.instructor,  q);
      const catHL        = highlight(c.category,    q);
      return `<tr>
        <td><strong>#${c.id}</strong></td>
        <td>${titleHL}</td>
        <td>${instrHL}</td>
        <td><span class="pill cat">${catHL}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td>${c.duration_hours}h</td>
        <td><span class="pill ${c.is_published ? 'published' : 'draft'}">${c.is_published ? 'Published' : 'Draft'}</span></td>
        <td>${c.discount_percent ? '<span class="discount-tag">'+c.discount_percent+'% OFF</span>' : '—'}</td>
      </tr>`;
    }).join('');

    toast(`${results.length} result${results.length > 1 ? 's' : ''} mila!`, 'success');
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><p>Server error: ${e.message}</p></div></td></tr>`;
    toast('Search error: ' + e.message, 'error');
  }
}

function highlight(text, query) {
  if (!text || !query) return text || '';
  const regex = new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
}

function clearSearch() {
  document.getElementById('search-q').value = '';
  document.getElementById('search-table').innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="icon">🔍</div><p>Type something and press Search</p></div></td></tr>';
  document.getElementById('search-response').style.display = 'none';
  document.getElementById('search-result-info').style.display = 'none';
}

// ─── ANALYTICS ────────────────────────────────────────
async function loadAllAnalytics() {
  await loadAnalyticsSummary();
  await loadPopularCategory();
  await loadAvgPrice();
  await loadRevenue();
  await loadTopInstructors();
}

async function loadAnalyticsSummary() {
  try {
    const res = await fetch(BASE_URL + '/analytics/summary');
    if (!res.ok) return;
    const d = await res.json();
    document.getElementById('an-gross').textContent = '₹' + (d.revenue?.gross_revenue ?? '—');
    document.getElementById('an-net').textContent   = '₹' + (d.revenue?.net_revenue   ?? '—');
    document.getElementById('an-avg').textContent   = '₹' + (d.pricing?.avg_price     ?? '—');
    document.getElementById('an-top-cat').textContent = d.most_popular_category ?? '—';
  } catch(e) {}
}

async function loadPopularCategory() {
  const tbody = document.getElementById('popular-cat-table');
  tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res = await fetch(BASE_URL + '/analytics/popular-category');
    const d   = await res.json();
    if (!res.ok) { tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Error: '+d.detail+'</p></div></td></tr>'; return; }
    const all = d.all_categories;
    const total = all.reduce((s, r) => s + Number(r.total_courses), 0);
    tbody.innerHTML = all.map((r, i) => {
      const share = total ? Math.round(Number(r.total_courses) / total * 100) : 0;
      return `<tr>
        <td><strong>#${i+1}</strong>${i===0?' 🏆':''}</td>
        <td><span class="pill cat">${r.category}</span></td>
        <td><strong>${r.total_courses}</strong></td>
        <td>${r.published_courses}</td>
        <td>
          <div class="progress-wrap">
            <div class="progress-bar" style="width:${share}%"></div>
            <span class="progress-label">${share}%</span>
          </div>
        </td>
      </tr>`;
    }).join('');
    toast('Categories loaded ✅', 'success');
  } catch(e) { tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Server error</p></div></td></tr>'; }
}

async function loadAvgPrice() {
  const tbody = document.getElementById('avg-price-table');
  tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res = await fetch(BASE_URL + '/analytics/avg-price');
    const d   = await res.json();
    if (!res.ok) { tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Error</p></div></td></tr>'; return; }
    tbody.innerHTML = d.data.map(r => `
      <tr>
        <td><span class="pill cat">${r.category}</span></td>
        <td><span class="price-tag">₹${r.avg_price}</span></td>
        <td style="color:var(--teal)">₹${r.min_price}</td>
        <td style="color:var(--crimson)">₹${r.max_price}</td>
        <td>${r.total_courses}</td>
      </tr>`).join('');
    toast('Prices loaded ✅', 'success');
  } catch(e) { tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>Server error</p></div></td></tr>'; }
}

async function loadRevenue() {
  const tbody = document.getElementById('revenue-table');
  tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res = await fetch(BASE_URL + '/analytics/revenue');
    const d   = await res.json();
    if (!res.ok) { tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><p>Error</p></div></td></tr>'; return; }
    tbody.innerHTML = d.by_category.map(r => `
      <tr>
        <td><span class="pill cat">${r.category}</span></td>
        <td>${r.total_courses}</td>
        <td><span class="price-tag">₹${r.gross_revenue}</span></td>
        <td><span class="price-tag" style="color:var(--gold)">₹${r.net_revenue_after_discount}</span></td>
      </tr>`).join('');
    toast('Revenue loaded ✅', 'success');
  } catch(e) { tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><p>Server error</p></div></td></tr>'; }
}

async function loadTopInstructors() {
  const tbody = document.getElementById('instructors-table');
  tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Loading...</p></div></td></tr>';
  try {
    const res = await fetch(BASE_URL + '/analytics/top-instructors');
    const d   = await res.json();
    if (!res.ok) { tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Error</p></div></td></tr>'; return; }
    tbody.innerHTML = d.data.map((r, i) => `
      <tr>
        <td><strong>#${i+1}</strong>${i===0?' ⭐':''}</td>
        <td><strong>${r.instructor}</strong></td>
        <td>${r.total_courses} <small style="color:var(--text-muted)">(${r.published_courses} pub)</small></td>
        <td><span class="price-tag">₹${r.avg_price}</span></td>
        <td><span class="price-tag" style="color:var(--gold)">₹${r.net_revenue}</span></td>
        <td>${r.avg_duration_hours}h</td>
      </tr>`).join('');
    toast('Instructors loaded ✅', 'success');
  } catch(e) { tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>Server error</p></div></td></tr>'; }
}

// ─── MODAL CLOSE ──────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('delete-modal');
  if (modal) modal.addEventListener('click', function(e) { if (e.target === this) closeModal(); });
});