/* ============================================================
   Design System — CHARTS framework
   - formatters กลาง (number / currency / percent / abbreviate)
   - chart helper ที่อ่านสีจาก CSS tokens -> เปลี่ยน skin แล้ว re-render ได้
   ใช้:  DS.add('canvasId', el => new Chart(el, {...}))  แล้ว  DS.renderAll()
        DS.setSkin('finance-dark')   // สลับ skin + วาดใหม่
   ============================================================ */
window.DS = (function () {
  const nf = new Intl.NumberFormat('en-US');
  const root = () => getComputedStyle(document.body);
  const cssVar = n => root().getPropertyValue(n).trim();

  // ---------- formatters ----------
  const fmt = {
    num: n => nf.format(Math.round(n)),
    pct: (n, d = 1) => (n >= 0 ? '+' : '') + n.toFixed(d) + '%',
    pctPlain: (n, d = 0) => n.toFixed(d) + '%',
    abbr(n, sym = '') {
      const a = Math.abs(n);
      if (a >= 1e9) return sym + (n / 1e9).toFixed(2) + 'B';
      if (a >= 1e6) return sym + (n / 1e6).toFixed(1) + 'M';
      if (a >= 1e3) return sym + (n / 1e3).toFixed(0) + 'K';
      return sym + nf.format(Math.round(n));
    },
    cur: (n, sym = '฿') => '฿' === sym ? DS.fmt.abbr(n, '฿') : DS.fmt.abbr(n, sym),
  };

  // ---------- color helpers (อ่านจาก skin ปัจจุบัน) ----------
  const colors = () => ['--c1','--c2','--c3','--c4','--c5','--c6','--c7','--c8'].map(cssVar);
  const C = k => cssVar('--' + k); // C('accent'), C('pos') ...

  // ---------- shared chart option presets ----------
  function tooltip() {
    return {
      backgroundColor: cssVar('--card'),
      borderColor: cssVar('--line'),
      borderWidth: 1, padding: 10,
      titleColor: cssVar('--ink'), bodyColor: cssVar('--muted'),
    };
  }
  function baseOpts(o = {}) {
    const grid = cssVar('--grid'), tick = cssVar('--muted');
    const opt = {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: !!o.legend, labels: { color: tick, boxWidth: 10, font: { size: 11 } } },
        tooltip: tooltip(),
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: tick, font: { size: 11 } } },
        y: { grid: { color: grid }, ticks: { color: tick, font: { size: 11 } }, beginAtZero: o.zero !== false },
      },
    };
    if (o.horizontal) { opt.indexAxis = 'y'; opt.scales.x.grid.color = grid; opt.scales.y.grid.display = false; }
    if (o.stacked) { opt.scales.x.stacked = true; opt.scales.y.stacked = true; }
    if (o.curMoney) opt.scales.y.ticks.callback = v => DS.fmt.abbr(v, '฿');
    if (o.dualAxis) opt.scales.y1 = {
      position: 'right', grid: { display: false }, beginAtZero: true,
      // 2nd axis formatter: default ฿ ; ส่ง o.dualAxisFmt เป็น fn เมื่อแกนเป็น % / x / หน่วยอื่น
      ticks: { color: tick, font: { size: 11 }, callback: o.dualAxisFmt || (v => DS.fmt.abbr(v, '฿')) },
    };
    return opt;
  }

  // ---------- registry + render ----------
  const reg = [];               // {id, build}
  const live = {};              // id -> Chart instance
  function add(id, build) { reg.push({ id, build }); }
  function applyDefaults() {
    if (!window.Chart) return;
    Chart.defaults.color = cssVar('--muted');
    Chart.defaults.borderColor = cssVar('--grid');
    Chart.defaults.font.family = cssVar('--font') || 'Segoe UI, sans-serif';
  }
  function renderAll() {
    applyDefaults();
    reg.forEach(({ id, build }) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (live[id]) { live[id].destroy(); }      // เคลียร์ของเก่าก่อนวาดใหม่ (ตอนสลับ skin)
      live[id] = build(el);
    });
  }
  function setSkin(name) {
    document.body.className = document.body.className.replace(/\bskin-\S+/g, '').trim();
    document.body.classList.add('skin-' + name);
    renderAll();
  }

  return { fmt, colors, C, cssVar, tooltip, baseOpts, add, renderAll, setSkin, live };
})();

// ใส่ปุ่ม "หน้าหลัก" อัตโนมัติทุกหน้าที่โหลด charts.js (ลิงก์ไป hub ที่ root)
document.addEventListener('DOMContentLoaded', function () {
  if (document.querySelector('.ds-home')) return;          // มีแล้วไม่ใส่ซ้ำ
  var home = document.createElement('a');
  home.className = 'chip ds-home';
  // คำนวณ root ของไซต์จาก path จริง -> รองรับทั้ง local (อยู่ที่ /) และ GitHub Pages (อยู่ใต้ /<repo>/)
  var m = location.pathname.match(/^(.*?\/)(?:_templates|_moodboard|Projects)\//);
  var root = m ? m[1] : './';
  var inTemplates = location.pathname.indexOf('/_templates/') !== -1;
  home.href = inTemplates ? root + '_templates/' : root;   // template -> gallery ; อื่น ๆ -> hub
  home.innerHTML = inTemplates ? '← Template Gallery' : '← ⌂ หน้าหลัก';
  var ctx = document.querySelector('.ds-header .ctx');
  if (ctx) { ctx.insertBefore(home, ctx.firstChild); }
  else { home.style.cssText = 'position:fixed;top:16px;left:16px;z-index:60'; document.body.appendChild(home); }
});
