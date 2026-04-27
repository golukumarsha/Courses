/* =========================================
   CourseVault — API Dashboard
   script.js
   ========================================= */

let BASE = 'http://localhost:8000';
let deleteTargetId = null;

/* ──────────────────────────────────────────
   UTILITY: Get current base URL
────────────────────────────────────────── */
function getBase() {
  return document.getElementById('base-url').value.replace(/\/$/, '');
}

function updateBaseUrl() {
  BASE = getBase();
  document.getElementById('sidebar-url').textContent =
    BASE.replace('http://', '').replace('https://', '');
}

/* ──────────────────────────────────────────
   TAB SWITCHING
────────────────────────────────────────── */
function switchTab(name, el) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  if (el) el.classList.add('active');
  document.getElementById('topbar-title').textContent =
    el ? el.textContent.trim() : name;
  if (name === 'dashboard') loadDashboard();
  if (name === 'courses')   getAllCourses();
}

/* ──────────────────────────────────────────
   TOAST NOTIFICATIONS
────────────────────────────────────────── */
function toast(msg, type = 'info') {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  t.innerHTML = `<span>${icon}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

/* ──────────────────────────────────────────
   RESPONSE DISPLAY
────────────────────────────────────────── */
function showResponse(prefix, data, status, ok) {
  const rb = document.getElementById(prefix + '-response');
  if (rb) rb.style.display = 'block';
  const pill = document.getElementById(prefix + '-status');
  const raw  = document.getElementById(prefix + '-raw');
  if (pill) {
    pill.textContent = status;
    pill.className = 'status-pill ' + (ok ? 'status-ok' : 'status-error');
  }
  if (raw) raw.textContent = JSON.stringify(data, null, 2);
}

function setLoading(prefix) {
  const pill = document.getElementById(prefix + '-status');
  const raw  = document.getElementById(prefix + '-raw');
  if (pill) {
    pill.className = 'status-pill status-pending';
    pill.innerHTML = '<span class="loading-dots"><span></span><span></span><span></span></span>';
  }
  if (raw) raw.textContent = 'Loading...';
}

/* ──────────────────────────────────────────
   GENERIC API HELPER
────────────────────────────────────────── */
async function api(method, endpoint, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(getBase() + endpoint, opts);
  const data = await res.json();
  return { data, status: res.status, ok: res.ok };
}

/* ──────────────────────────────────────────
   PING API
────────────────────────────────────────── */
async function pingApi() {
  try {
    const r = await api('GET', '/');
    toast('API is online! ' + JSON.stringify(r.data), 'success');
  } catch (e) {
    toast('Cannot reach API. Check base URL.', 'error');
  }
}

/* ──────────────────────────────────────────
   DASHBOARD
────────────────────────────────────────── */
async function loadDashboard() {
  try {
    const r = await api('GET', '/courses');
    const courses = r.data;
    const pub  = courses.filter(c => c.is_published).length;
    const cats = new Set(courses.map(c => c.category)).size;

    document.getElementById('stat-total').textContent     = courses.length;
    document.getElementById('stat-published').textContent = pub;
    document.getElementById('stat-draft').textContent     = courses.length - pub;
    document.getElementById('stat-cats').textContent      = cats;

    const tbody = document.getElementById('dashboard-table');
    tbody.innerHTML = courses.slice(0, 8).map(c => `
      <tr>
        <td><strong>#${c.id}</strong></td>
        <td>${c.title}</td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td><span class="pill ${c.is_published ? 'published' : 'draft'}">
              ${c.is_published ? 'Published' : 'Draft'}
            </span></td>
      </tr>`).join('') ||
      '<tr><td colspan="6"><div class="empty-state"><p>No courses found</p></div></td></tr>';
  } catch (e) {
    toast('Error loading dashboard: ' + e.message, 'error');
  }
}

/* ──────────────────────────────────────────
   GET ALL COURSES
────────────────────────────────────────── */
async function getAllCourses() {
  setLoading('all-courses');
  try {
    const r = await api('GET', '/courses');
    document.getElementById('all-courses-response').style.display = 'block';
    showResponse('all-courses', r.data, r.status + ' OK', r.ok);

    const tbody = document.getElementById('all-courses-table');
    if (!r.data.length) {
      tbody.innerHTML = '<tr><td colspan="9"><div class="empty-state"><p>No courses found</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = r.data.map(c => `
      <tr>
        <td><strong>#${c.id}</strong></td>
        <td>${c.title}</td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td>${c.duration_hours}h</td>
        <td><span class="pill ${c.is_published ? 'published' : 'draft'}">
              ${c.is_published ? '✓ Published' : 'Draft'}
            </span></td>
        <td>${c.discount_percent
          ? `<span class="discount-tag">-${c.discount_percent}%</span>`
          : '—'}</td>
        <td>
          <div class="actions-cell">
            <button class="icon-btn" title="Edit"   onclick="quickEdit(${c.id})">✏️</button>
            <button class="icon-btn del" title="Delete" onclick="quickDelete(${c.id})">🗑️</button>
          </div>
        </td>
      </tr>`).join('');
  } catch (e) {
    showResponse('all-courses', { error: e.message }, 'Error', false);
    toast('Error: ' + e.message, 'error');
  }
}

/* ──────────────────────────────────────────
   GET COURSE BY ID
────────────────────────────────────────── */
async function getCourseById() {
  const id = document.getElementById('get-id').value;
  if (!id) { toast('Please enter a Course ID', 'error'); return; }
  setLoading('get-one');
  try {
    const r = await api('GET', `/course/${id}`);
    showResponse('get-one', r.data, r.status + (r.ok ? ' OK' : ' Error'), r.ok);
    if (r.ok) toast(`Course #${id} loaded`, 'success');
    else      toast(r.data.detail || 'Not found', 'error');
  } catch (e) {
    showResponse('get-one', { error: e.message }, 'Error', false);
    toast('Error: ' + e.message, 'error');
  }
}

/* ──────────────────────────────────────────
   CREATE COURSE
────────────────────────────────────────── */
async function createCourse() {
  const title      = document.getElementById('c-title').value.trim();
  const instructor = document.getElementById('c-instructor').value.trim();
  const category   = document.getElementById('c-category').value.trim();
  const price      = parseFloat(document.getElementById('c-price').value);
  const duration   = parseInt(document.getElementById('c-duration').value);
  const discount   = document.getElementById('c-discount').value;
  const published  = document.getElementById('c-published').checked;

  if (!title || !instructor || !category || isNaN(price) || isNaN(duration)) {
    toast('Please fill all required fields', 'error');
    return;
  }

  const body = { title, instructor, category, price, duration_hours: duration, is_published: published };
  if (discount) body.discount_percent = parseFloat(discount);

  setLoading('create');
  try {
    const r = await api('POST', '/create', body);
    showResponse('create', r.data, r.status + (r.ok ? ' Created' : ' Error'), r.ok);
    if (r.ok) {
      toast(`Course created! ID: ${r.data.id}`, 'success');
      clearCreateForm();
    } else {
      toast(r.data.detail || 'Error creating', 'error');
    }
  } catch (e) {
    showResponse('create', { error: e.message }, 'Error', false);
    toast('Error: ' + e.message, 'error');
  }
}

function clearCreateForm() {
  ['c-title', 'c-instructor', 'c-category', 'c-price', 'c-duration', 'c-discount']
    .forEach(id => document.getElementById(id).value = '');
  document.getElementById('c-published').checked = false;
}

/* ──────────────────────────────────────────
   UPDATE COURSE
────────────────────────────────────────── */
async function prefillUpdate() {
  const id = document.getElementById('u-id').value;
  if (!id) { toast('Enter an ID first', 'error'); return; }
  try {
    const r = await api('GET', `/course/${id}`);
    if (!r.ok) { toast('Course not found', 'error'); return; }
    const c = r.data;
    document.getElementById('u-title').value      = c.title || '';
    document.getElementById('u-instructor').value = c.instructor || '';
    document.getElementById('u-category').value   = c.category || '';
    document.getElementById('u-price').value      = c.price || '';
    document.getElementById('u-duration').value   = c.duration_hours || '';
    document.getElementById('u-discount').value   = c.discount_percent || '';
    document.getElementById('u-published').checked = !!c.is_published;
    toast('Fields prefilled from API', 'info');
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

async function updateCourse() {
  const id         = document.getElementById('u-id').value;
  const title      = document.getElementById('u-title').value.trim();
  const instructor = document.getElementById('u-instructor').value.trim();
  const category   = document.getElementById('u-category').value.trim();
  const price      = parseFloat(document.getElementById('u-price').value);
  const duration   = parseInt(document.getElementById('u-duration').value);
  const discount   = document.getElementById('u-discount').value;
  const published  = document.getElementById('u-published').checked;

  if (!id || !title || !instructor || !category || isNaN(price) || isNaN(duration)) {
    toast('Please fill all required fields', 'error');
    return;
  }

  const body = { title, instructor, category, price, duration_hours: duration, is_published: published };
  if (discount) body.discount_percent = parseFloat(discount);

  setLoading('update');
  try {
    const r = await api('PUT', `/update/${id}`, body);
    showResponse('update', r.data, r.status + (r.ok ? ' Updated' : ' Error'), r.ok);
    if (r.ok) toast(`Course #${id} updated!`, 'success');
    else      toast(r.data.detail || 'Update failed', 'error');
  } catch (e) {
    showResponse('update', { error: e.message }, 'Error', false);
    toast('Error: ' + e.message, 'error');
  }
}

function clearUpdateForm() {
  ['u-id', 'u-title', 'u-instructor', 'u-category', 'u-price', 'u-duration', 'u-discount']
    .forEach(id => document.getElementById(id).value = '');
  document.getElementById('u-published').checked = false;
}

/* ──────────────────────────────────────────
   DELETE COURSE
────────────────────────────────────────── */
function confirmDelete() {
  const id = document.getElementById('d-id').value;
  if (!id) { toast('Enter a Course ID', 'error'); return; }
  deleteTargetId = id;
  document.getElementById('modal-id').textContent = '#' + id;
  document.getElementById('delete-modal').classList.add('open');
}

function closeModal() {
  document.getElementById('delete-modal').classList.remove('open');
  deleteTargetId = null;
}

async function doDelete() {
  closeModal();
  const id = deleteTargetId || document.getElementById('d-id').value;
  if (!id) return;
  setLoading('delete');
  try {
    const r = await api('DELETE', `/delete/${id}`);
    showResponse('delete', r.data, r.status + (r.ok ? ' Deleted' : ' Error'), r.ok);
    if (r.ok) {
      toast(`Course #${id} deleted`, 'success');
      document.getElementById('d-id').value = '';
    } else {
      toast(r.data.detail || 'Delete failed', 'error');
    }
  } catch (e) {
    showResponse('delete', { error: e.message }, 'Error', false);
    toast('Error: ' + e.message, 'error');
  }
}

/* ──────────────────────────────────────────
   QUICK ACTIONS FROM TABLE
────────────────────────────────────────── */
function quickEdit(id) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.nav-item')[4].classList.add('active');
  switchTab('update', null);
  document.getElementById('u-id').value = id;
  prefillUpdate();
}

function quickDelete(id) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.nav-item')[5].classList.add('active');
  switchTab('delete', null);
  document.getElementById('d-id').value = id;
  confirmDelete();
}

/* ──────────────────────────────────────────
   FILTER COURSES
────────────────────────────────────────── */
async function filterCourses() {
  const params = new URLSearchParams();
  const cat  = document.getElementById('f-category').value.trim();
  const inst = document.getElementById('f-instructor').value.trim();
  const price = document.getElementById('f-price').value;
  const pub  = document.getElementById('f-published').value;

  if (cat)        params.set('category',     cat);
  if (inst)       params.set('instructor',   inst);
  if (price)      params.set('price',        price);
  if (pub !== '') params.set('is_published', pub);

  try {
    const res  = await fetch(getBase() + '/filter?' + params);
    const data = await res.json();
    document.getElementById('filter-response').style.display = 'block';
    showResponse('filter', data, res.status + ' OK', res.ok);

    const tbody = document.getElementById('filter-table');
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>No courses match these filters</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = data.map(c => `
      <tr>
        <td><strong>#${c.id}</strong></td>
        <td>${c.title}</td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td><span class="pill ${c.is_published ? 'published' : 'draft'}">
              ${c.is_published ? 'Published' : 'Draft'}
            </span></td>
      </tr>`).join('');
    toast(`${data.length} course(s) found`, 'success');
  } catch (e) {
    toast('Filter error: ' + e.message, 'error');
  }
}

function clearFilters() {
  ['f-category', 'f-instructor', 'f-price']
    .forEach(id => document.getElementById(id).value = '');
  document.getElementById('f-published').value = '';
}

/* ──────────────────────────────────────────
   PAGINATION
────────────────────────────────────────── */
async function paginateCourses(page) {
  if (page) document.getElementById('p-page').value = page;
  const pg  = parseInt(document.getElementById('p-page').value)  || 1;
  const lim = parseInt(document.getElementById('p-limit').value) || 5;

  try {
    const res  = await fetch(getBase() + `/pagination?page=${pg}&limit=${lim}`);
    const data = await res.json();
    document.getElementById('pagination-response').style.display = 'block';
    showResponse('pagination', data, res.status + ' OK', res.ok);

    const tbody = document.getElementById('pagination-table');
    if (!data.data || !data.data.length) {
      tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>No courses on this page</p></div></td></tr>';
      return;
    }
    tbody.innerHTML = data.data.map(c => `
      <tr>
        <td><strong>#${c.id}</strong></td>
        <td>${c.title}</td>
        <td>${c.instructor}</td>
        <td><span class="pill cat">${c.category}</span></td>
        <td><span class="price-tag">₹${c.price}</span></td>
        <td><span class="pill ${c.is_published ? 'published' : 'draft'}">
              ${c.is_published ? 'Published' : 'Draft'}
            </span></td>
      </tr>`).join('');

    const totalPages = Math.ceil(data.total / data.limit);
    const infoBar = document.getElementById('page-info-bar');
    infoBar.style.display = 'flex';
    document.getElementById('page-info-text').textContent =
      `Page ${data.page} of ${totalPages} · ${data.total} total courses`;

    const ctrl = document.getElementById('pagination-controls');
    ctrl.innerHTML = `
      ${pg > 1
        ? `<button class="btn btn-outline btn-sm" onclick="paginateCourses(${pg - 1})">← Prev</button>`
        : ''}
      <span style="padding:0 8px; font-size:0.85rem; color:var(--text-muted);">${pg} / ${totalPages}</span>
      ${pg < totalPages
        ? `<button class="btn btn-gold btn-sm" onclick="paginateCourses(${pg + 1})">Next →</button>`
        : ''}
    `;
    toast(`Page ${pg} loaded · ${data.data.length} items`, 'success');
  } catch (e) {
    toast('Pagination error: ' + e.message, 'error');
  }
}

/* ──────────────────────────────────────────
   INIT
────────────────────────────────────────── */
document.getElementById('delete-modal').addEventListener('click', function (e) {
  if (e.target === this) closeModal();
});

loadDashboard();