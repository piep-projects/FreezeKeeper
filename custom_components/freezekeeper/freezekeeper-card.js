// FreezeKeeper Lovelace Card  v0.2.0
// https://github.com/piep-projects/FreezeKeeper

class FreezekeeperCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._entityId = 'sensor.freezekeeper';
    this._s = {
      view: 'dashboard',        // dashboard | inventory | add | withdraw | settings
      filter: 'all',            // all | green | orange | red
      sortCol: 'mhd_min',
      sortDir: 'asc',
      colFilters: {},
      expandedId: null,
      selectedIds: new Set(),
      form: _emptyForm(),
      withdrawInput: '',
      withdrawEntry: null,
      loading: false,
      error: null,
      settingsTab: 'categories', // categories | units
      editForm: null,            // null | { type:'cat'|'unit', id:string|null, data:{} }
    };
  }

  connectedCallback() {
    this.addEventListener('click',  e => this._onClick(e));
    this.addEventListener('change', e => this._onChange(e));
    this.addEventListener('input',  e => this._onInput(e));
    this.addEventListener('submit', e => { e.preventDefault(); this._onSubmit(e); });

    // HA registers a keydown capture listener on document that opens Quick Search.
    // A capture listener on window fires before document, so we can stop propagation
    // there to prevent HA from intercepting keys typed in our inputs.
    this._keyGuard = e => {
      const t = e.target;
      if (t && t.closest && t.closest('freezekeeper-card') &&
          (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA')) {
        e.stopPropagation();
      }
    };
    window.addEventListener('keydown', this._keyGuard, true);
  }

  disconnectedCallback() {
    if (this._keyGuard) {
      window.removeEventListener('keydown', this._keyGuard, true);
      this._keyGuard = null;
    }
  }

  setConfig(config) {
    this._entityId = config.entity || 'sensor.freezekeeper';
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 4; }

  // ─────────────────────────────────────────────────────── render ──

  _render() {
    const data = this._data();
    const view = this._s.view;
    const body = !data
      ? `<div class="no-sensor">Sensor <code>${_esc(this._entityId)}</code> nicht gefunden.</div>`
      : view === 'dashboard'  ? this._vDashboard(data)
      : view === 'inventory'  ? this._vInventory(data)
      : view === 'add'        ? this._vAdd(data)
      : view === 'withdraw'   ? this._vWithdraw(data)
      : view === 'settings'   ? this._vSettings(data)
      : '';
    this.innerHTML = _CSS + `<div class="card">${body}</div>`;
  }

  // ── Dashboard ─────────────────────────────────────────────────────

  _vDashboard(d) {
    const { green = 0, orange = 0, red = 0, total = 0 } = d;
    return `
      <div class="header">
        <span class="title">🧊 FreezeKeeper</span>
        <button class="ibtn" data-a="to-add"      title="Neu einfrieren">＋</button>
        <button class="ibtn" data-a="to-withdraw" title="Entnehmen">↑</button>
        <button class="ibtn" data-a="to-settings" title="Einstellungen">⚙</button>
      </div>
      <div class="circles">
        <button class="circle green"  data-a="to-inv" data-f="green">
          <span class="cn">${green}</span><span class="cl">haltbar</span>
        </button>
        <button class="circle orange" data-a="to-inv" data-f="orange">
          <span class="cn">${orange}</span><span class="cl">bald ablaufend</span>
        </button>
        <button class="circle red"    data-a="to-inv" data-f="red">
          <span class="cn">${red}</span><span class="cl">abgelaufen</span>
        </button>
        <button class="circle dark"   data-a="to-inv" data-f="all">
          <span class="cn">${total}</span><span class="cl">gesamt</span>
        </button>
      </div>
      <div class="hint">Tippen zum Öffnen der gefilterten Übersicht</div>`;
  }

  // ── Inventory ─────────────────────────────────────────────────────

  _vInventory(d) {
    const { sortCol, sortDir, colFilters, expandedId, selectedIds, filter } = this._s;
    const cats = d.categories || [];
    const units = d.freezer_units || [];
    const entries = this._filtered(d);

    const filterLabel = { all: 'Gesamtbestand', green: 'haltbar 🟢', orange: 'bald ablaufend 🟠', red: 'abgelaufen 🔴' }[filter];

    const COLS = [
      { k: 'id',           l: 'ID',          w: '68px' },
      { k: 'description',  l: 'Beschreibung', w: 'auto' },
      { k: 'category_id',  l: 'Kategorie',   w: '150px' },
      { k: 'mhd_min',      l: 'MHD',         w: '90px' },
      { k: 'traffic_light',l: 'St.',          w: '40px' },
      { k: 'portions',     l: 'Port.',        w: '50px' },
      { k: 'freezer_unit', l: 'Einheit',      w: '110px' },
    ];

    const thead = COLS.map(c => {
      const active = sortCol === c.k;
      const arr = active ? (sortDir === 'asc' ? '▲' : '▼') : '⇅';
      const fv = _esc(colFilters[c.k] || '');
      return `<th style="width:${c.w}">
        <button class="sh" data-a="sort" data-col="${c.k}">${c.l} <span>${arr}</span></button>
        <input class="sf" data-col="${c.k}" value="${fv}" placeholder="…">
      </th>`;
    }).join('');

    const rows = this._inventoryRows(d);

    const bulk = selectedIds.size ? `<div class="bulk">
      <span>${selectedIds.size} ausgewählt</span>
      <button class="abtn" data-a="bulk-print">🖨 Etiketten drucken</button>
      <button class="abtn sec" data-a="clear-sel">Aufheben</button>
    </div>` : '';

    return `
      <div class="header">
        <button class="ibtn" data-a="to-dash">←</button>
        <span class="title">${filterLabel}</span>
        <button class="ibtn sm" data-a="clear-filters">✕ Filter</button>
      </div>
      <div class="tw">
        <table>
          <thead><tr>
            <th style="width:32px"><input type="checkbox" id="ca"></th>
            ${thead}
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${bulk}`;
  }

  _inventoryRows(d) {
    if (!d) return `<tr><td colspan="9" class="empty">Keine Einträge</td></tr>`;
    const cats  = d.categories    || [];
    const units = d.freezer_units || [];
    const { expandedId, selectedIds } = this._s;
    const entries = this._filtered(d);
    return entries.map(e => {
      const cat  = (cats.find(c => c.id === e.category_id) || {}).name  || e.category_id;
      const unit = (units.find(u => u.id === e.freezer_unit) || {}).name || e.freezer_unit;
      const tl   = { green: '🟢', orange: '🟠', red: '🔴' }[e.traffic_light] || '⚪';
      const exp  = expandedId === e.id;
      const chk  = selectedIds.has(e.id);
      const ar   = exp ? `<tr class="ar"><td colspan="9">
        <button class="abtn" data-a="withdraw-row" data-id="${e.id}">Entnehmen</button>
        <button class="abtn" data-a="print-row"    data-id="${e.id}">🖨 Etikett</button>
        <button class="abtn sec" data-a="collapse">✕ Schließen</button>
      </td></tr>` : '';
      return `<tr class="dr ${exp ? 'exp' : ''}" data-id="${e.id}">
        <td><input type="checkbox" class="rc" data-id="${e.id}" ${chk ? 'checked' : ''}></td>
        <td class="mo">${String(e.id).padStart(6,'0')}</td>
        <td>${_esc(e.description)}<br><small>${e.package_index}/${e.package_total}</small></td>
        <td class="sm">${_esc(cat)}</td>
        <td class="sm mo">${_fmtS(e.mhd_min)}</td>
        <td class="cc">${tl}</td>
        <td class="cc">${e.portions}</td>
        <td class="sm">${_esc(unit)}</td>
      </tr>${ar}`;
    }).join('') || `<tr><td colspan="9" class="empty">Keine Einträge</td></tr>`;
  }

  // ── Neuaufnahme ───────────────────────────────────────────────────

  _vAdd(d) {
    const cats  = (d.categories    || []).slice().sort((a, b) => a.name.localeCompare(b.name, 'de'));
    const units = (d.freezer_units || []).slice().sort((a, b) => a.name.localeCompare(b.name, 'de'));
    const f = this._s.form;

    const catOpts  = cats.map(c =>
      `<option value="${c.id}" ${f.category_id === c.id ? 'selected' : ''}>${_esc(c.name)}</option>`).join('');
    const unitOpts = units.map(u =>
      `<option value="${u.id}" ${f.freezer_unit === u.id ? 'selected' : ''}>${_esc(u.name)}</option>`).join('');

    let mhd = '';
    if (f.category_id && f.frozen_date) {
      const cat = cats.find(c => c.id === f.category_id);
      if (cat) {
        const base = new Date(f.frozen_date);
        const mn = _addDays(base, cat.min_days), mx = _addDays(base, cat.max_days);
        mhd = `<div class="mhd">🟢 MHD: ${_fmtD(mn)} – ${_fmtD(mx)}</div>`;
      }
    }

    const err  = this._s.error   ? `<div class="err">${_esc(this._s.error)}</div>` : '';
    const busy = this._s.loading;
    const pkg  = parseInt(f.package_total) || 1;

    return `
      <div class="header">
        <button class="ibtn" data-a="to-dash">←</button>
        <span class="title">Neuaufnahme</span>
      </div>
      <form class="form" id="add-form">
        ${err}
        <label>Beschreibung
          <input name="description" value="${_esc(f.description)}" required placeholder="z. B. Kichererbsen-Curry">
        </label>
        <label>Kategorie
          <select name="category_id" required>
            <option value="">– bitte wählen –</option>${catOpts}
          </select>
        </label>
        <div class="r2">
          <label>Portionen<input name="portions" type="number" min="1" value="${f.portions}"></label>
          <label>Packungen<input name="package_total" type="number" min="1" value="${pkg}"></label>
        </div>
        <label>Gefriereinheit
          <select name="freezer_unit" required>
            <option value="">– bitte wählen –</option>${unitOpts}
          </select>
        </label>
        <label>Einfrierdatum
          <input name="frozen_date" type="date" value="${f.frozen_date}">
        </label>
        ${mhd}
        <button class="sbtn" type="submit" ${busy ? 'disabled' : ''}>
          ${busy ? 'Wird gespeichert…' : `🖨 ${pkg} Etikett(en) drucken & speichern`}
        </button>
      </form>`;
  }

  // ── Entnahme ──────────────────────────────────────────────────────

  _vWithdraw(d) {
    const e   = this._s.withdrawEntry;
    const err = this._s.error ? `<div class="err">${_esc(this._s.error)}</div>` : '';
    const cats = d.categories || [];

    const detail = e ? (() => {
      const cat = (cats.find(c => c.id === e.category_id) || {}).name || e.category_id;
      const tl  = { green: '🟢 noch haltbar', orange: '🟠 bald ablaufend', red: '🔴 abgelaufen' }[e.traffic_light] || '';
      return `<div class="wd">
        <div class="wdt">${_esc(e.description)}</div>
        ${_wdRow('Kategorie', cat)}${_wdRow('Einheit', e.freezer_unit)}
        ${_wdRow('Portionen', e.portions)}${_wdRow('Eingefroren', _fmtS(e.frozen_date))}
        ${_wdRow('MHD', _fmtS(e.mhd_min) + ' – ' + _fmtS(e.mhd_max))}
        ${_wdRow('Status', tl)}
      </div>
      <div class="fa">
        <button class="sbtn" data-a="confirm-wd" data-id="${e.id}">✓ Entnahme buchen</button>
        <button class="abtn sec" data-a="cancel-wd">✕ Abbrechen</button>
      </div>`;
    })() : `<form class="form" id="wd-form">
      ${err}
      <label>Barcode-Nummer
        <div class="ir">
          <input name="wd_id" type="number" min="1" placeholder="ID eingeben" value="${this._s.withdrawInput}" autofocus>
          <button class="ibtn lg" type="button" data-a="scan-hint" title="Kamera-Tipp">📷</button>
        </div>
      </label>
      <button class="sbtn" type="submit">Suchen →</button>
    </form>`;

    return `
      <div class="header">
        <button class="ibtn" data-a="to-dash">←</button>
        <span class="title">Entnahme</span>
      </div>
      ${detail}`;
  }

  // ── Einstellungen ─────────────────────────────────────────────────

  _vSettings(d) {
    const { settingsTab, editForm, error } = this._s;
    const cats  = (d.categories    || []).slice().sort((a, b) => a.name.localeCompare(b.name, 'de'));
    const units = (d.freezer_units || []).slice().sort((a, b) => a.name.localeCompare(b.name, 'de'));
    const err   = error ? `<div class="err" style="margin:8px 14px">${_esc(error)}</div>` : '';

    const header = `
      <div class="header">
        <button class="ibtn" data-a="to-dash">←</button>
        <span class="title">Einstellungen</span>
      </div>`;

    if (editForm) {
      const isNew = !editForm.id;
      const d2    = editForm.data;
      const body  = editForm.type === 'cat'
        ? `<label>Name<input name="name" value="${_esc(d2.name)}" required placeholder="z. B. Rindfleisch (roh)"></label>
           <div class="r2">
             <label>Min. Tage<input name="min_days" type="number" min="1" value="${d2.min_days || ''}"></label>
             <label>Max. Tage<input name="max_days" type="number" min="1" value="${d2.max_days || ''}"></label>
           </div>`
        : `<label>Name<input name="name" value="${_esc(d2.name)}" required placeholder="z. B. Gefriertruhe"></label>`;

      return `${header}
        <form class="form" id="edit-form">
          ${err}
          <div class="stitle">${isNew ? (editForm.type === 'cat' ? 'Neue Kategorie' : 'Neue Gefriereinheit') : 'Bearbeiten'}</div>
          ${body}
          <div class="r2">
            <button class="sbtn" type="submit">${this._s.loading ? 'Speichern…' : '✓ Speichern'}</button>
            <button class="abtn sec" type="button" data-a="cancel-edit" style="padding:10px">✕ Abbrechen</button>
          </div>
        </form>`;
    }

    const tabCat = settingsTab === 'categories';
    const tabs   = `
      <div class="stabs">
        <button class="stab ${tabCat ? 'act' : ''}" data-a="settings-tab" data-tab="categories">Kategorien (${cats.length})</button>
        <button class="stab ${!tabCat ? 'act' : ''}" data-a="settings-tab" data-tab="units">Gefriereinheiten (${units.length})</button>
      </div>`;

    const list = tabCat
      ? cats.map(c => `
          <div class="srow">
            <div class="sinfo">
              <div class="sname">${_esc(c.name)}</div>
              <div class="smeta">${c.min_days}–${c.max_days} Tage</div>
            </div>
            <button class="abtn sm" data-a="edit-cat" data-id="${_esc(c.id)}">✎</button>
            <button class="abtn sm sec" data-a="del-cat" data-id="${_esc(c.id)}">✕</button>
          </div>`).join('') || '<div class="empty" style="padding:16px">Keine Kategorien</div>'
      : units.map(u => `
          <div class="srow">
            <div class="sinfo"><div class="sname">${_esc(u.name)}</div></div>
            <button class="abtn sm" data-a="edit-unit" data-id="${_esc(u.id)}">✎</button>
            <button class="abtn sm sec" data-a="del-unit" data-id="${_esc(u.id)}">✕</button>
          </div>`).join('') || '<div class="empty" style="padding:16px">Keine Gefriereinheiten</div>';

    const addBtn = tabCat
      ? `<button class="abtn" data-a="new-cat">＋ Kategorie</button>`
      : `<button class="abtn" data-a="new-unit">＋ Gefriereinheit</button>`;

    return `${header}${tabs}${err}
      <div class="slist">${list}</div>
      <div class="sadd">${addBtn}</div>`;
  }

  // ─────────────────────────────────────────────── event handlers ──

  _onClick(e) {
    const btn = e.target.closest('[data-a]');
    if (!btn) {
      const row = e.target.closest('tr.dr');
      if (row) { this._toggleExpand(parseInt(row.dataset.id)); }
      return;
    }
    const a  = btn.dataset.a;
    const id = btn.dataset.id !== undefined ? btn.dataset.id : null;
    switch (a) {
      case 'to-dash':      this._nav('dashboard'); break;
      case 'to-inv':       this._nav('inventory', btn.dataset.f || 'all'); break;
      case 'to-add':       this._nav('add'); break;
      case 'to-withdraw':  this._nav('withdraw'); break;
      case 'to-settings':  this._nav('settings'); break;
      case 'settings-tab': this._s.settingsTab = btn.dataset.tab; this._render(); break;
      case 'new-cat':      this._s.editForm = { type: 'cat',  id: null, data: { name: '', min_days: 90,  max_days: 180 } }; this._render(); break;
      case 'new-unit':     this._s.editForm = { type: 'unit', id: null, data: { name: '' } }; this._render(); break;
      case 'edit-cat': {
        const c = (this._data().categories || []).find(c => c.id === id);
        if (c) { this._s.editForm = { type: 'cat', id: c.id, data: { ...c } }; this._render(); }
        break;
      }
      case 'edit-unit': {
        const u = (this._data().freezer_units || []).find(u => u.id === id);
        if (u) { this._s.editForm = { type: 'unit', id: u.id, data: { ...u } }; this._render(); }
        break;
      }
      case 'del-cat':      this._deleteCat(id); break;
      case 'del-unit':     this._deleteUnit(id); break;
      case 'cancel-edit':  this._s.editForm = null; this._s.error = null; this._render(); break;
      case 'sort':         this._sort(btn.dataset.col); break;
      case 'clear-filters':this._s.colFilters = {}; this._render(); break;
      case 'clear-sel':    this._s.selectedIds.clear(); this._render(); break;
      case 'collapse':     this._s.expandedId = null; this._render(); break;
      case 'withdraw-row': this._openWithdrawById(parseInt(id)); break;
      case 'confirm-wd':   this._confirmWithdraw(parseInt(id)); break;
      case 'cancel-wd':    this._s.withdrawEntry = null; this._render(); break;
      case 'print-row':    this._callPrint([parseInt(id)]); break;
      case 'bulk-print':   this._callPrint([...this._s.selectedIds]); break;
      case 'scan-hint':    this._scanHint(); break;
    }
  }

  _onChange(e) {
    const el = e.target;
    if (el.id === 'ca') { this._toggleAll(el.checked); return; }
    if (el.classList.contains('rc')) {
      const id = parseInt(el.dataset.id);
      el.checked ? this._s.selectedIds.add(id) : this._s.selectedIds.delete(id);
      this._render(); return;
    }
    if (this._s.view === 'add' && el.name) {
      this._s.form[el.name] = el.value;
      if (['category_id', 'frozen_date', 'package_total'].includes(el.name)) this._render();
    }
    if (this._s.view === 'settings' && this._s.editForm && el.name) {
      this._s.editForm.data[el.name] = el.value;
    }
  }

  _onInput(e) {
    const el = e.target;
    if (el.classList.contains('sf')) {
      this._s.colFilters[el.dataset.col] = el.value;
      const tbody = this.querySelector('table tbody');
      if (tbody) tbody.innerHTML = this._inventoryRows(this._data());
      else this._render();
      return;
    }
    if (this._s.view === 'add' && el.name) {
      this._s.form[el.name] = el.value;
    }
    if (this._s.view === 'settings' && this._s.editForm && el.name) {
      this._s.editForm.data[el.name] = el.value;
    }
  }

  _onSubmit(e) {
    if (e.target.id === 'add-form')  this._submitAdd();
    if (e.target.id === 'wd-form')   this._lookupWithdraw();
    if (e.target.id === 'edit-form') this._submitEdit();
  }

  // ──────────────────────────────────────────────── interactions ──

  _nav(view, filter) {
    this._s.view = view; this._s.error = null;
    if (filter) this._s.filter = filter;
    if (view === 'withdraw') { this._s.withdrawEntry = null; this._s.withdrawInput = ''; }
    if (view === 'add')      this._s.form = _emptyForm();
    if (view === 'settings') this._s.editForm = null;
    this._render();
  }

  _sort(col) {
    if (this._s.sortCol === col) this._s.sortDir = this._s.sortDir === 'asc' ? 'desc' : 'asc';
    else { this._s.sortCol = col; this._s.sortDir = 'asc'; }
    this._render();
  }

  _toggleExpand(id) {
    this._s.expandedId = this._s.expandedId === id ? null : id;
    this._render();
  }

  _toggleAll(checked) {
    const entries = this._filtered(this._data());
    if (checked) entries.forEach(e => this._s.selectedIds.add(e.id));
    else this._s.selectedIds.clear();
    this._render();
  }

  _openWithdrawById(id) {
    const e = (this._data().entries || []).find(e => e.id === id);
    if (e) { this._s.withdrawEntry = e; this._s.view = 'withdraw'; this._s.error = null; this._render(); }
  }

  async _submitAdd() {
    const f = this._s.form;
    if (!f.description || !f.category_id || !f.freezer_unit) {
      this._s.error = 'Bitte alle Pflichtfelder ausfüllen.'; this._render(); return;
    }
    this._s.loading = true; this._s.error = null; this._render();
    try {
      await this._hass.callService('freezekeeper', 'add_entries', {
        description: f.description, category_id: f.category_id,
        portions: parseInt(f.portions), package_total: parseInt(f.package_total),
        freezer_unit: f.freezer_unit, frozen_date: f.frozen_date,
      });
      this._nav('dashboard');
    } catch (err) { this._s.error = String(err.message || err); }
    this._s.loading = false; this._render();
  }

  async _submitEdit() {
    const ef = this._s.editForm;
    if (!ef) return;
    const d = ef.data;
    if (!d.name) { this._s.error = 'Name erforderlich.'; this._render(); return; }
    const id = ef.id || _toId(d.name);
    this._s.loading = true; this._s.error = null; this._render();
    try {
      if (ef.type === 'cat') {
        if (!d.min_days || !d.max_days) { this._s.error = 'Min/Max-Tage erforderlich.'; this._s.loading = false; this._render(); return; }
        await this._hass.callService('freezekeeper', 'upsert_category', {
          id, name: d.name, min_days: parseInt(d.min_days), max_days: parseInt(d.max_days),
        });
      } else {
        await this._hass.callService('freezekeeper', 'upsert_freezer_unit', { id, name: d.name });
      }
      this._s.editForm = null; this._s.error = null;
    } catch (err) { this._s.error = String(err.message || err); }
    this._s.loading = false; this._render();
  }

  async _deleteCat(id) {
    const cat = (this._data().categories || []).find(c => c.id === id);
    if (!confirm(`Kategorie „${cat ? cat.name : id}" löschen?`)) return;
    try {
      await this._hass.callService('freezekeeper', 'delete_category', { id });
      this._render();
    } catch (err) { this._s.error = String(err.message || err); this._render(); }
  }

  async _deleteUnit(id) {
    const unit = (this._data().freezer_units || []).find(u => u.id === id);
    if (!confirm(`Gefriereinheit „${unit ? unit.name : id}" löschen?`)) return;
    try {
      await this._hass.callService('freezekeeper', 'delete_freezer_unit', { id });
      this._render();
    } catch (err) { this._s.error = String(err.message || err); this._render(); }
  }

  _lookupWithdraw() {
    const el = this.querySelector('[name=wd_id]');
    const id = parseInt(el?.value || '');
    if (!id) { this._s.error = 'Bitte eine ID eingeben.'; this._render(); return; }
    const entry = (this._data().entries || []).find(e => e.id === id);
    if (!entry) { this._s.error = `ID ${id} nicht im aktiven Bestand.`; this._render(); return; }
    this._s.withdrawEntry = entry; this._s.error = null; this._render();
  }

  async _confirmWithdraw(id) {
    this._s.loading = true; this._render();
    try {
      await this._hass.callService('freezekeeper', 'withdraw', { id });
      this._nav('dashboard');
    } catch (err) { this._s.error = String(err.message || err); }
    this._s.loading = false; this._render();
  }

  async _callPrint(ids) {
    try {
      await this._hass.callService('freezekeeper', 'print_labels', { ids });
    } catch (err) { alert('Druckfehler: ' + (err.message || err)); }
  }

  _scanHint() {
    alert('Direktscan: Nutze die native Kamera-App (iOS/Android), um den QR-Code auf dem Etikett zu scannen — die Entnahme wird dann automatisch gebucht, ohne HA zu öffnen.');
  }

  // ──────────────────────────────────────────────────── helpers ──

  _data() {
    if (!this._hass) return null;
    const s = this._hass.states[this._entityId];
    return s ? s.attributes : null;
  }

  _filtered(data) {
    let list = (data.entries || []).slice();
    const { filter, sortCol, sortDir, colFilters } = this._s;
    const cats  = data.categories    || [];
    const units = data.freezer_units || [];

    if (filter !== 'all') list = list.filter(e => e.traffic_light === filter);

    for (const [col, val] of Object.entries(colFilters)) {
      if (!val) continue;
      const q = val.toLowerCase();
      list = list.filter(e => {
        if (col === 'id')           return String(e.id).includes(q);
        if (col === 'description')  return e.description.toLowerCase().includes(q);
        if (col === 'category_id')  return ((cats.find(c => c.id === e.category_id) || {}).name || '').toLowerCase().includes(q);
        if (col === 'freezer_unit') return ((units.find(u => u.id === e.freezer_unit) || {}).name || '').toLowerCase().includes(q);
        if (col === 'mhd_min')      return (e.mhd_min + e.mhd_max).includes(q);
        if (col === 'traffic_light')return e.traffic_light.startsWith(q);
        if (col === 'portions')     return String(e.portions).includes(q);
        return true;
      });
    }

    list.sort((a, b) => {
      let av = a[sortCol] ?? '', bv = b[sortCol] ?? '';
      if (typeof av === 'number') return sortDir === 'asc' ? av - bv : bv - av;
      av = String(av); bv = String(bv);
      return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    return list;
  }
}

// ────────────────────────────────────────────────────── utils ──

function _emptyForm() {
  return { description: '', category_id: '', portions: 1, package_total: 1,
           freezer_unit: '', frozen_date: new Date().toISOString().slice(0, 10) };
}
function _toId(name) {
  return name.toLowerCase()
    .replace(/[äöüß]/g, c => ({ ä: 'ae', ö: 'oe', ü: 'ue', ß: 'ss' }[c] || c))
    .replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').slice(0, 40) || 'item_' + Date.now();
}
function _esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function _fmtS(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return `${String(d.getUTCDate()).padStart(2,'0')}.${String(d.getUTCMonth()+1).padStart(2,'0')}.${String(d.getUTCFullYear()).slice(2)}`;
}
function _fmtD(d) {
  return `${String(d.getDate()).padStart(2,'0')}.${String(d.getMonth()+1).padStart(2,'0')}.${d.getFullYear()}`;
}
function _addDays(d, n) { const r = new Date(d); r.setDate(r.getDate() + n); return r; }
function _wdRow(l, v) { return `<div class="wdr"><span>${l}</span><span>${_esc(v)}</span></div>`; }

// ─────────────────────────────────────────────────────── CSS ──

const _S = 'freezekeeper-card';
const _CSS = `<style>
${_S} *,${_S} *::before,${_S} *::after{box-sizing:border-box;margin:0;padding:0}
${_S} .card{background:var(--card-background-color,#1e293b);border-radius:12px;overflow:hidden;
  font-family:var(--primary-font-family,system-ui,sans-serif);font-size:14px;
  color:var(--primary-text-color,#f1f5f9)}
${_S} .no-sensor{padding:16px;color:#ef4444;font-size:13px}
${_S} .header{display:flex;align-items:center;gap:6px;padding:10px 14px 9px;
  border-bottom:1px solid var(--divider-color,#334155);
  background:linear-gradient(90deg,#0ea5e918 0%,transparent 100%)}
${_S} .title{flex:1;font-weight:600;font-size:15px}
${_S} .ibtn{background:none;border:none;cursor:pointer;color:var(--secondary-text-color,#94a3b8);
  font-size:17px;padding:3px 5px;border-radius:5px;line-height:1}
${_S} .ibtn:hover{background:var(--divider-color,#334155);color:var(--primary-text-color,#f1f5f9)}
${_S} .ibtn.sm{font-size:11px}${_S} .ibtn.lg{font-size:21px}
${_S} .circles{display:flex;justify-content:space-around;padding:18px 8px 6px}
${_S} .circle{display:flex;flex-direction:column;align-items:center;justify-content:center;
  width:78px;height:78px;border-radius:50%;border:none;cursor:pointer;
  transition:transform .15s,box-shadow .15s}
${_S} .circle:hover{transform:scale(1.07);box-shadow:0 4px 16px #0005}
${_S} .circle.green{background:#22c55e}${_S} .circle.orange{background:#f97316}
${_S} .circle.red{background:#ef4444}${_S} .circle.dark{background:#4b5563}
${_S} .cn{font-size:21px;font-weight:700;color:#fff;line-height:1}
${_S} .cl{font-size:9px;color:#ffffffbb;text-align:center;margin-top:2px}
${_S} .hint{text-align:center;font-size:10px;color:var(--disabled-text-color,#475569);padding:4px 0 10px}
${_S} .tw{overflow-x:auto}
${_S} table{width:100%;border-collapse:collapse;font-size:12px}
${_S} th{background:var(--table-header-background-color,#0f172a);position:sticky;top:0;z-index:1;padding:0}
${_S} .sh{background:none;border:none;cursor:pointer;text-align:left;padding:5px 7px 1px;
  font-size:11px;font-weight:600;color:var(--secondary-text-color,#94a3b8);width:100%;white-space:nowrap}
${_S} .sh:hover,${_S} .sh.act{color:#0ea5e9}
${_S} .sf{width:100%;border:none;border-top:1px solid var(--divider-color,#334155);
  background:var(--secondary-background-color,#0f172a)!important;
  color:var(--primary-text-color,#f1f5f9)!important;padding:3px 7px;font-size:11px}
${_S} .sf:focus{outline:none!important;background:#1e3a5f!important;color:#f1f5f9!important}
${_S} td{padding:5px 7px;border-bottom:1px solid #33415530;vertical-align:middle}
${_S} tr.dr:hover td{background:#0f172a40;cursor:pointer}
${_S} tr.exp td{background:#0f172a60!important}
${_S} tr.ar td{padding:3px 7px 7px;background:#0f172a40}
${_S} .mo{font-family:monospace}${_S} .sm{font-size:11px}${_S} .cc{text-align:center}
${_S} small{color:var(--secondary-text-color,#94a3b8)}
${_S} .empty{text-align:center;color:var(--secondary-text-color,#94a3b8);padding:20px}
${_S} .bulk{display:flex;align-items:center;gap:8px;padding:7px 14px;
  background:var(--secondary-background-color,#0f172a);
  border-top:1px solid var(--divider-color,#334155);font-size:12px;flex-wrap:wrap}
${_S} .bulk span{color:var(--secondary-text-color,#94a3b8)}
${_S} .abtn{padding:4px 11px;border-radius:5px;border:1px solid #0ea5e9;
  background:#0ea5e918;color:#0ea5e9;cursor:pointer;font-size:12px}
${_S} .abtn:hover{background:#0ea5e935}
${_S} .abtn.sm{padding:2px 7px;font-size:11px}
${_S} .abtn.sec{border-color:var(--divider-color,#334155);color:var(--secondary-text-color,#94a3b8);background:none}
${_S} .abtn.sec:hover{background:var(--divider-color,#334155)}
${_S} .sbtn{width:100%;padding:10px;border-radius:7px;border:none;background:#0ea5e9;
  color:#fff;font-size:14px;font-weight:600;cursor:pointer;margin-top:6px}
${_S} .sbtn:hover{background:#0284c7}${_S} .sbtn:disabled{opacity:.55;cursor:default}
${_S} .form{padding:14px;display:flex;flex-direction:column;gap:11px}
${_S} label{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--secondary-text-color,#94a3b8)}
${_S} input,${_S} select{padding:7px 9px;border-radius:6px;border:1px solid var(--divider-color,#334155);
  background:var(--secondary-background-color,#0f172a);
  color:var(--primary-text-color,#f1f5f9);font-size:14px}
${_S} input:focus,${_S} select:focus{outline:2px solid #0ea5e9;border-color:transparent}
${_S} .r2{display:grid;grid-template-columns:1fr 1fr;gap:11px}
${_S} .ir{display:flex;gap:7px}${_S} .ir input{flex:1}
${_S} .mhd{padding:7px 11px;border-radius:6px;background:#22c55e1a;border:1px solid #22c55e35;color:#4ade80;font-size:13px}
${_S} .err{padding:7px 11px;border-radius:6px;background:#ef44441a;border:1px solid #ef444435;color:#f87171;font-size:13px}
${_S} .fa{padding:0 14px 14px;display:flex;flex-direction:column;gap:7px}
${_S} .wd{padding:14px}
${_S} .wdt{font-size:15px;font-weight:600;margin-bottom:10px}
${_S} .wdr{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #33415528;font-size:13px}
${_S} .wdr span:first-child{color:var(--secondary-text-color,#94a3b8)}
${_S} .stabs{display:flex;border-bottom:1px solid var(--divider-color,#334155)}
${_S} .stab{flex:1;padding:8px;background:none;border:none;border-bottom:2px solid transparent;
  cursor:pointer;color:var(--secondary-text-color,#94a3b8);font-size:13px}
${_S} .stab.act{color:#0ea5e9;border-bottom-color:#0ea5e9}
${_S} .stitle{font-size:13px;font-weight:600;color:var(--secondary-text-color,#94a3b8)}
${_S} .slist{padding:8px 14px;display:flex;flex-direction:column;gap:2px;max-height:300px;overflow-y:auto}
${_S} .srow{display:flex;align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid #33415530}
${_S} .sinfo{flex:1;min-width:0}
${_S} .sname{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
${_S} .smeta{font-size:11px;color:var(--secondary-text-color,#94a3b8);margin-top:1px}
${_S} .sadd{padding:8px 14px 14px}
</style>`;

customElements.define('freezekeeper-card', FreezekeeperCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'freezekeeper-card',
  name: 'FreezeKeeper',
  description: 'Verwaltung von Tiefkühlgut mit Etikettendruck (Brother QL-820NWBc)',
});
