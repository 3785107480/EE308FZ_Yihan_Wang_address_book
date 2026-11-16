'use strict';

const $ = (selector) => document.querySelector(selector);
const state = { contacts: [], view: 'all', selected: null, editing: null, deleting: null, file: null };
const methodTypes = ['phone', 'email', 'social', 'address', 'website', 'other'];
const typeSymbols = { phone: '☎', email: '@', social: '#', address: '⌂', website: '↗', other: '⋯' };
let toastTimer;
let loadingPromise = null;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(className, text, action, label) {
  const node = element('button', className, text);
  node.type = 'button';
  if (label) node.setAttribute('aria-label', label);
  node.addEventListener('click', action);
  return node;
}

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, credentials: 'same-origin' });
  const json = await response.json().catch(() => null);
  if (!response.ok) throw new Error(json?.error || `Request failed (${response.status}). Please retry.`);
  if (!json) throw new Error('The server returned an unexpected response.');
  return json;
}

function jsonOptions(method, payload) {
  return { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) };
}

function message(error) {
  return error instanceof TypeError ? 'The server could not be reached. Check the connection and try again.' : error.message;
}

function notify(text) {
  clearTimeout(toastTimer);
  $('#toast').textContent = text;
  $('#toast').hidden = false;
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 4500);
}

function errorIn(selector, text) {
  $(selector).textContent = text;
  $(selector).hidden = !text;
}

function connected(value) {
  $('#refresh-button').classList.toggle('offline', !value);
  $('#connection-text').textContent = value ? 'Connected' : 'Connection unavailable';
}

async function loadContacts() {
  if (loadingPromise) return loadingPromise;
  loadingPromise = (async () => {
    $('#contact-list').setAttribute('aria-busy', 'true');
    $('#refresh-button').disabled = true;
    try {
      const result = await api('/api/contacts');
      state.contacts = result.data;
      $('#load-error').hidden = true;
      connected(true);
      render();
      return true;
    } catch (error) {
      connected(false);
      $('#load-error-text').textContent = message(error);
      $('#load-error').hidden = false;
      $('#list-description').textContent = state.contacts.length ? 'Showing previously loaded contacts. Refresh to retry.' : 'Contacts could not be loaded.';
      if (!state.contacts.length) {
        $('#contact-list').replaceChildren(element('div', 'loading', 'Your contacts will appear here when the connection is restored.'));
      }
      return false;
    } finally {
      $('#contact-list').setAttribute('aria-busy', 'false');
      $('#refresh-button').disabled = false;
    }
  })();
  try { return await loadingPromise; } finally { loadingPromise = null; }
}

function initials(name) {
  return name.split(/\s+/).slice(0, 2).map((part) => Array.from(part)[0]).join('').toUpperCase();
}

function avatar(contact, size = '') {
  const node = element('div', `avatar tone-${contact.id % 5} ${size}`, initials(contact.name));
  node.setAttribute('aria-hidden', 'true');
  return node;
}

function visibleContacts() {
  const query = $('#search').value.trim().toLocaleLowerCase();
  return state.contacts.filter((contact) => {
    if (state.view === 'bookmarks' && !contact.bookmarked) return false;
    const text = [contact.name, contact.company, contact.job_title, contact.notes,
      ...contact.methods.map((method) => `${method.label} ${method.value}`)].join(' ').toLocaleLowerCase();
    return !query || text.includes(query);
  }).sort((a, b) => $('#sort').value === 'recent' ? b.id - a.id : a.name.localeCompare(b.name));
}

function setView(view) {
  state.view = view;
  state.selected = null;
  $('#search').value = '';
  render();
}

function render() {
  const previousFocus = document.activeElement;
  const focusedBookmark = previousFocus?.dataset.bookmarkId;
  const bookmarked = state.contacts.filter((contact) => contact.bookmarked).length;
  $('#stat-total').textContent = state.contacts.length;
  $('#stat-bookmarks').textContent = bookmarked;
  $('#stat-methods').textContent = state.contacts.reduce((total, contact) => total + contact.methods.length, 0);
  $('#nav-all').textContent = state.contacts.length;
  $('#nav-bookmarks').textContent = bookmarked;
  $('#list-title').textContent = state.view === 'all' ? 'All contacts' : 'Bookmarks';
  for (const view of ['all', 'bookmarks']) {
    $(`#${view}-view`).classList.toggle('selected', view === state.view);
    $(`#${view}-view`).setAttribute('aria-pressed', String(view === state.view));
  }
  const contacts = visibleContacts();
  $('#visible-count').textContent = contacts.length;
  $('#list-description').textContent = `Showing ${contacts.length} of ${state.contacts.length} contacts`;
  const list = $('#contact-list');
  list.replaceChildren();
  if (!contacts.some((contact) => contact.id === state.selected)) state.selected = null;
  if (!contacts.length) {
    const empty = element('div', 'empty-state');
    const searching = Boolean($('#search').value.trim());
    empty.append(element('div', 'empty-symbol', searching ? '⌕' : state.view === 'bookmarks' ? '☆' : '▤'));
    empty.append(element('h3', '', searching ? 'No matches just yet.' : state.view === 'bookmarks' ? 'Keep your favorites close.' : 'Every connection starts here.'));
    empty.append(element('p', '', searching ? 'Try another name, company or contact detail.' : state.view === 'bookmarks' ? 'Select the star beside a contact to add them to your bookmarks.' : 'Add your first contact, or bring your people together from an Excel file.'));
    const actions = element('div', 'empty-actions');
    if (searching) actions.append(button('button', 'Clear search', () => { $('#search').value = ''; render(); }));
    else if (state.view === 'bookmarks') actions.append(button('button', 'View all contacts', () => setView('all')));
    else {
      actions.append(button('button primary', '＋ Add your first contact', () => openContact()));
      actions.append(button('button', 'Import Excel', openImport));
    }
    empty.append(actions);
    list.append(empty);
  } else {
    const heading = element('div', 'table-heading');
    heading.append(element('span', '', 'CONTACT'), element('span', 'secondary-column', 'CONTACT DETAILS'), element('span', 'secondary-column company-heading', 'ORGANIZATION'), element('span', 'sr-only', 'Bookmark'));
    list.append(heading);
    for (const contact of contacts) {
      const row = element('article', `contact-row${contact.id === state.selected ? ' active' : ''}`);
      const person = button('contact-person', '', () => { state.selected = contact.id; render(); }, `View ${contact.name}`);
      person.setAttribute('aria-expanded', String(state.selected === contact.id));
      const copy = element('span', 'person-copy');
      copy.append(element('span', 'person-name', contact.name), element('span', 'person-role', contact.job_title || contact.company || 'Personal contact'));
      person.append(avatar(contact), copy);
      const preview = element('div', 'method-preview');
      const first = contact.methods.find((method) => method.type === 'email') || contact.methods[0];
      if (first) {
        preview.append(element('span', '', first.value));
        preview.append(element('small', '', `${contact.methods.length} contact method${contact.methods.length === 1 ? '' : 's'}`));
      } else preview.append(element('span', '', 'No contact methods'));
      const star = button('bookmark-button', contact.bookmarked ? '★' : '☆', () => toggleBookmark(contact), `${contact.bookmarked ? 'Remove bookmark from' : 'Bookmark'} ${contact.name}`);
      star.setAttribute('aria-pressed', String(contact.bookmarked));
      star.dataset.bookmarkId = contact.id;
      row.append(person, preview, element('div', 'company-preview', contact.company || '—'), star);
      list.append(row);
    }
  }
  renderDetail();
  if (focusedBookmark) document.querySelector(`[data-bookmark-id="${focusedBookmark}"]`)?.focus();
}

function renderDetail() {
  const detail = $('#contact-detail');
  const contact = state.contacts.find((item) => item.id === state.selected);
  detail.hidden = !contact;
  $('#list-layout').classList.toggle('has-detail', Boolean(contact));
  detail.replaceChildren();
  if (!contact) return;
  const top = element('div', 'detail-top');
  top.append(button('icon-button', '×', () => { state.selected = null; render(); }, 'Close contact details'));
  const person = element('div', 'detail-person');
  person.append(avatar(contact), element('h3', '', contact.name), element('p', '', [contact.job_title, contact.company].filter(Boolean).join(' · ') || 'Personal contact'));
  const actions = element('div', 'detail-actions');
  actions.append(button('button small', 'Edit contact', () => openContact(contact)));
  const star = button('button small', contact.bookmarked ? '★ Bookmarked' : '☆ Bookmark', () => toggleBookmark(contact));
  star.dataset.bookmarkId = contact.id;
  star.setAttribute('aria-pressed', String(contact.bookmarked));
  actions.append(star);
  person.append(actions);
  detail.append(top, person);
  const methods = element('section', 'detail-section');
  methods.append(element('h4', '', `CONTACT METHODS · ${contact.methods.length}`));
  if (!contact.methods.length) methods.append(element('p', 'detail-notes', 'No contact methods have been added.'));
  for (const method of contact.methods) {
    const row = element('div', 'detail-method');
    row.append(element('div', 'method-type-icon', typeSymbols[method.type]));
    const body = element('span');
    body.append(element('small', '', method.label ? `${method.type} · ${method.label}` : method.type));
    let value;
    if (['email', 'phone', 'website'].includes(method.type)) {
      value = element('a', '', method.value);
      value.href = method.type === 'email' ? `mailto:${encodeURIComponent(method.value)}` : method.type === 'phone' ? `tel:${method.value.replace(/[^\d+]/g, '')}` : method.value;
      if (method.type === 'website') { value.target = '_blank'; value.rel = 'noopener noreferrer'; }
    } else value = element('span', 'method-value', method.value);
    body.append(value);
    row.append(body);
    methods.append(row);
  }
  detail.append(methods);
  if (contact.notes) {
    const notes = element('section', 'detail-section');
    notes.append(element('h4', '', 'NOTES'), element('p', 'detail-notes', contact.notes));
    detail.append(notes);
  }
  const bottom = element('div', 'detail-bottom');
  bottom.append(button('delete-link', 'Delete contact', () => openDelete(contact)));
  detail.append(bottom);
}

async function toggleBookmark(contact) {
  const controls = document.querySelectorAll(`[data-bookmark-id="${contact.id}"]`);
  controls.forEach((control) => { control.disabled = true; });
  try {
    const result = await api(`/api/contacts/${contact.id}/bookmark`, jsonOptions('PATCH', { bookmarked: !contact.bookmarked }));
    state.contacts = state.contacts.map((item) => item.id === contact.id ? result.data : item);
    render();
    notify(result.data.bookmarked ? 'Contact added to bookmarks.' : 'Bookmark removed.');
  } catch (error) { notify(message(error)); } finally { controls.forEach((control) => { control.disabled = false; }); }
}

function addMethod(method = { type: 'phone', label: '', value: '' }) {
  if ($('#method-fields').children.length >= 100) { notify('A contact can have up to 100 contact methods.'); return; }
  const row = element('div', 'method-fields-row');
  const select = element('select', 'method-type');
  select.setAttribute('aria-label', 'Contact method type');
  for (const kind of methodTypes) {
    const option = element('option', '', kind[0].toUpperCase() + kind.slice(1));
    option.value = kind;
    select.append(option);
  }
  select.value = method.type;
  const label = element('input', 'method-label');
  label.setAttribute('aria-label', 'Contact method label');
  label.placeholder = 'Label (e.g. Work)'; label.maxLength = 80; label.value = method.label;
  const value = element('input', 'method-value-input');
  value.setAttribute('aria-label', 'Contact method value');
  value.placeholder = 'Phone number or contact detail'; value.maxLength = 1000; value.value = method.value;
  const configure = () => {
    value.type = select.value === 'email' ? 'email' : select.value === 'website' ? 'url' : 'text';
    value.placeholder = { phone: '+86 138 0000 0000', email: 'name@example.com', website: 'https://example.com', social: '@username', address: 'Street, city, country', other: 'Contact detail' }[select.value];
  };
  select.addEventListener('change', configure);
  configure();
  const remove = button('icon-button remove-method', '×', () => { row.remove(); }, 'Remove contact method');
  row.append(select, label, value, remove);
  $('#method-fields').append(row);
}

function openContact(contact = null) {
  state.editing = contact?.id || null;
  const form = $('#contact-form');
  form.reset();
  for (const key of ['name', 'company', 'job_title', 'notes']) form.elements.namedItem(key).value = contact?.[key] || '';
  form.elements.namedItem('bookmarked').checked = Boolean(contact?.bookmarked);
  $('#contact-dialog-title').textContent = contact ? 'Edit contact' : 'Add a contact';
  $('#save-contact').textContent = contact ? 'Save changes' : 'Save contact';
  errorIn('#contact-error', '');
  $('#method-fields').replaceChildren();
  if (contact?.methods.length) contact.methods.forEach(addMethod);
  else addMethod();
  $('#contact-dialog').showModal();
  $('#contact-name').focus();
}

async function saveContact(event) {
  event.preventDefault();
  errorIn('#contact-error', '');
  const form = $('#contact-form');
  const payload = {};
  for (const key of ['name', 'company', 'job_title', 'notes']) payload[key] = form.elements.namedItem(key).value.trim();
  payload.bookmarked = form.elements.namedItem('bookmarked').checked;
  payload.methods = [];
  for (const row of $('#method-fields').children) {
    const label = row.querySelector('.method-label').value.trim();
    const value = row.querySelector('.method-value-input').value.trim();
    if (!label && !value) continue;
    if (!value) { errorIn('#contact-error', 'Enter a value for each labeled contact method, or remove the empty method.'); return; }
    payload.methods.push({ type: row.querySelector('.method-type').value, label, value });
  }
  const save = $('#save-contact');
  save.disabled = true;
  try {
    const edited = Boolean(state.editing);
    const result = await api(edited ? `/api/contacts/${state.editing}` : '/api/contacts', jsonOptions(edited ? 'PUT' : 'POST', payload));
    state.contacts = edited ? state.contacts.map((item) => item.id === result.data.id ? result.data : item) : [...state.contacts, result.data];
    state.selected = result.data.id;
    $('#search').value = '';
    if (state.view === 'bookmarks' && !result.data.bookmarked) state.view = 'all';
    render();
    $('#contact-dialog').close();
    notify(edited ? 'Contact updated.' : 'A new connection, saved.');
  } catch (error) { errorIn('#contact-error', message(error)); } finally { save.disabled = false; }
}

function openDelete(contact) {
  state.deleting = contact.id;
  $('#delete-description').textContent = `Delete ${contact.name} from your address book?`;
  errorIn('#delete-error', '');
  $('#delete-dialog').showModal();
  $('#cancel-delete').focus();
}

async function deleteContact() {
  $('#confirm-delete').disabled = true;
  try {
    await api(`/api/contacts/${state.deleting}`, { method: 'DELETE' });
    state.contacts = state.contacts.filter((contact) => contact.id !== state.deleting);
    state.selected = null;
    render();
    $('#delete-dialog').close();
    notify('Contact deleted.');
  } catch (error) { errorIn('#delete-error', message(error)); } finally { $('#confirm-delete').disabled = false; }
}

function openImport() {
  state.file = null;
  $('#import-file').value = '';
  $('#file-description').textContent = 'or drop it here · .xlsx · up to 5 MiB';
  $('#start-import').disabled = true;
  $('#import-result').hidden = true;
  errorIn('#import-error', '');
  $('#import-dialog').showModal();
}

function chooseFile(file) {
  errorIn('#import-error', '');
  $('#import-result').hidden = true;
  state.file = null;
  $('#start-import').disabled = true;
  if (!file) return;
  if (!/\.xlsx$/i.test(file.name) || file.size > 5 * 1024 * 1024 || !file.size) {
    errorIn('#import-error', 'Choose a non-empty .xlsx file no larger than 5 MiB.');
    return;
  }
  state.file = file;
  $('#file-description').textContent = `${file.name} · ${(file.size / 1024).toFixed(1)} KiB`;
  $('#start-import').disabled = false;
}

async function importContacts() {
  if (!state.file) return;
  const start = $('#start-import');
  start.disabled = true;
  start.textContent = 'Importing…';
  errorIn('#import-error', '');
  try {
    const result = await api('/api/import', { method: 'POST', headers: { 'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }, body: state.file });
    const summary = `${result.data.imported} contact${result.data.imported === 1 ? '' : 's'} imported. ${result.data.skipped} exact duplicate${result.data.skipped === 1 ? '' : 's'} skipped.`;
    $('#import-result').textContent = summary;
    $('#import-result').hidden = false;
    state.file = null;
    $('#search').value = '';
    state.view = 'all';
    await loadContacts();
    notify(summary);
  } catch (error) { errorIn('#import-error', message(error)); } finally { start.disabled = !state.file; start.textContent = 'Import contacts'; }
}

async function exportContacts() {
  $('#export-button').disabled = true;
  try {
    const response = await fetch('/api/export');
    if (!response.ok) throw new Error('The workbook could not be exported. Please retry.');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'address-book-contacts.xlsx';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
    notify('Your Excel export is ready. All contacts and methods are included.');
  } catch (error) { notify(message(error)); } finally { $('#export-button').disabled = false; }
}

$('#all-view').addEventListener('click', () => setView('all'));
$('#bookmarks-view').addEventListener('click', () => setView('bookmarks'));
$('#search').addEventListener('input', render);
$('#sort').addEventListener('change', render);
$('#add-contact').addEventListener('click', () => openContact());
$('#add-method').addEventListener('click', () => addMethod());
$('#contact-form').addEventListener('submit', saveContact);
document.querySelectorAll('.close-contact').forEach((node) => node.addEventListener('click', () => $('#contact-dialog').close()));
$('#refresh-button').addEventListener('click', loadContacts);
$('#retry-button').addEventListener('click', loadContacts);
$('#open-import').addEventListener('click', openImport);
$('#close-import').addEventListener('click', () => $('#import-dialog').close());
$('#import-file').addEventListener('change', (event) => chooseFile(event.target.files[0]));
$('#start-import').addEventListener('click', importContacts);
$('#export-button').addEventListener('click', exportContacts);
$('#cancel-delete').addEventListener('click', () => $('#delete-dialog').close());
$('#confirm-delete').addEventListener('click', deleteContact);
$('#format-help').addEventListener('click', () => $('#help-dialog').showModal());
$('#close-help').addEventListener('click', () => $('#help-dialog').close());
for (const type of ['dragenter', 'dragover']) $('#upload-zone').addEventListener(type, (event) => { event.preventDefault(); $('#upload-zone').classList.add('dragover'); });
for (const type of ['dragleave', 'drop']) $('#upload-zone').addEventListener(type, (event) => { event.preventDefault(); $('#upload-zone').classList.remove('dragover'); });
$('#upload-zone').addEventListener('drop', (event) => chooseFile(event.dataTransfer.files[0]));

loadContacts();
