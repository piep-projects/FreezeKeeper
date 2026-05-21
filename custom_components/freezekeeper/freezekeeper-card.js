// FreezeKeeper Lovelace Card  v0.3.0
// Dashboard-Widget — volle UI im HA-Panel /freezekeeper

class FreezekeeperCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._entityId = 'sensor.freezekeeper';
  }

  connectedCallback() {
    this.addEventListener('click', e => this._onClick(e));
  }

  setConfig(config) {
    this._entityId = config.entity || 'sensor.freezekeeper';
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 3; }

  _render() {
    const s = this._hass?.states[this._entityId];
    const d = s?.attributes;
    const { green = 0, orange = 0, red = 0, total = 0 } = d || {};
    const noSensor = !d
      ? `<div class="no-sensor">Sensor <code>${_esc(this._entityId)}</code> nicht gefunden.</div>`
      : '';
    this.innerHTML = _CSS + `<div class="card">
      <div class="header">
        <span class="title">❄️ FreezeKeeper</span>
        <button class="ibtn" data-a="add"      title="Neu einfrieren">＋</button>
        <button class="ibtn" data-a="withdraw" title="Entnehmen">↑</button>
        <button class="ibtn" data-a="settings" title="Einstellungen">⚙</button>
      </div>
      ${noSensor}
      <div class="circles">
        <button class="circle green"  data-a="inv" data-f="green">
          <span class="cn">${green}</span><span class="cl">haltbar</span>
        </button>
        <button class="circle orange" data-a="inv" data-f="orange">
          <span class="cn">${orange}</span><span class="cl">bald ablaufend</span>
        </button>
        <button class="circle red"    data-a="inv" data-f="red">
          <span class="cn">${red}</span><span class="cl">abgelaufen</span>
        </button>
        <button class="circle dark"   data-a="inv" data-f="all">
          <span class="cn">${total}</span><span class="cl">gesamt</span>
        </button>
      </div>
      <div class="hint">Tippen zum Öffnen der Übersicht</div>
    </div>`;
  }

  _onClick(e) {
    const btn = e.target.closest('[data-a]');
    if (!btn) return;
    const viewMap = { add: 'add', withdraw: 'withdraw', settings: 'settings', inv: 'inventory' };
    const view = viewMap[btn.dataset.a];
    if (!view) return;
    if (btn.dataset.f) sessionStorage.setItem('fk_filter', btn.dataset.f);
    sessionStorage.setItem('fk_view', view);
    history.pushState(null, '', '/freezekeeper');
    window.dispatchEvent(new CustomEvent('location-changed', {
      bubbles: true,
      detail: { replace: false },
    }));
  }
}

function _esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

const _CSS = `<style>
freezekeeper-card *,freezekeeper-card *::before,freezekeeper-card *::after{box-sizing:border-box;margin:0;padding:0}
freezekeeper-card .card{background:var(--card-background-color,#1e293b);border-radius:12px;overflow:hidden;
  font-family:var(--primary-font-family,system-ui,sans-serif);font-size:14px;
  color:var(--primary-text-color,#f1f5f9)}
freezekeeper-card .no-sensor{padding:16px;color:#ef4444;font-size:13px}
freezekeeper-card .header{display:flex;align-items:center;gap:6px;padding:10px 14px 9px;
  border-bottom:1px solid var(--divider-color,#334155);
  background:linear-gradient(90deg,#0ea5e918 0%,transparent 100%)}
freezekeeper-card .title{flex:1;font-weight:600;font-size:15px}
freezekeeper-card .ibtn{background:none;border:none;cursor:pointer;
  color:var(--secondary-text-color,#94a3b8);font-size:17px;padding:3px 5px;border-radius:5px;line-height:1}
freezekeeper-card .ibtn:hover{background:var(--divider-color,#334155);color:var(--primary-text-color,#f1f5f9)}
freezekeeper-card .circles{display:flex;justify-content:space-around;padding:18px 8px 6px}
freezekeeper-card .circle{display:flex;flex-direction:column;align-items:center;justify-content:center;
  width:78px;height:78px;border-radius:50%;border:none;cursor:pointer;
  transition:transform .15s,box-shadow .15s}
freezekeeper-card .circle:hover{transform:scale(1.07);box-shadow:0 4px 16px #0005}
freezekeeper-card .circle.green {background:#22c55e}
freezekeeper-card .circle.orange{background:#f97316}
freezekeeper-card .circle.red   {background:#ef4444}
freezekeeper-card .circle.dark  {background:#4b5563}
freezekeeper-card .cn{font-size:21px;font-weight:700;color:#fff;line-height:1}
freezekeeper-card .cl{font-size:9px;color:#ffffffbb;text-align:center;margin-top:2px}
freezekeeper-card .hint{text-align:center;font-size:10px;
  color:var(--disabled-text-color,#475569);padding:4px 0 10px}
</style>`;

customElements.define('freezekeeper-card', FreezekeeperCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'freezekeeper-card',
  name: 'FreezeKeeper',
  description: 'Tiefkühlverwaltung — Dashboard-Widget (volle UI im Panel)',
});
