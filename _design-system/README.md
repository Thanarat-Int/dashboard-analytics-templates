# Design System — Dashboard Web Templates

ระบบกลางสำหรับสร้าง web dashboard ระดับ production แบบ reusable ทุก domain/อุตสาหกรรม
แนวคิด: **ทุก dashboard = Archetype (โครง) × Skin (โทน) × Data (ข้อมูล)**

## ไฟล์ในระบบ

| ไฟล์ | หน้าที่ |
|---|---|
| `tokens.css` | ตัวแปรกลางทั้งหมด (สี/ฟอนต์/ระยะ/เงา) — แหล่งความจริงเดียว |
| `components.css` | คลาส reusable: card, kpi, chart-card, table, chip, header, grid |
| `charts.js` | framework `DS` — formatters + Chart.js helper ที่ re-render ตาม skin ได้ |
| `skins/skins.css` | 5 skin (สลับด้วย class บน `<body>`) |

## 5 Skins

| Skin (class) | โทน | เหมาะกับ |
|---|---|---|
| `skin-byd-red` | ขาว-แดง | automotive, retail, brand-driven |
| `skin-finance-dark` | navy + teal/blue | finance, executive, controlling |
| `skin-saas-violet` | ขาว + violet | SaaS, product, growth |
| `skin-luxury-gold` | ดำ + ทอง | luxury, hospitality, premium |
| `skin-command-center` | near-black + neon | operations, IT, real-time monitor |

## 13 Archetypes (ดู `../\_templates/` — gallery: `../\_templates/index.html`)

| # | Archetype | Decision | Default skin | Visual ใหม่ที่โชว์ |
|---|---|---|---|---|
| 01 | Executive Overview | monitor | byd-red (+ live switcher) | KPI + combo + donut + breakdown |
| 02 | Operational Monitor | monitor real-time | command-center | area, stacked severity, threshold bars, alert feed |
| 03 | Financial P&L | explain/diagnose | finance-dark | **waterfall** (stacked-bar trick), P&L table |
| 04 | Funnel & Conversion | diagnose | saas-violet | funnel bars, cohort retention curves |
| 05 | Geo / Distribution | compare | byd-red | **bubble map**, region rank, province table |
| 06 | Marketing Performance | diagnose | saas-violet | spend×ROAS combo, campaign table |
| 07 | Workforce Analytics | monitor | finance-dark | headcount×attrition combo (dual-axis %) |
| 08 | Inventory & Supply | monitor | command-center | aging stacked, stockout-risk pills |
| 09 | After-sales & Service | monitor | byd-red | service×CSAT combo, warranty mix, dealer scorecard |
| 10 | Customer Lifecycle / CRM | diagnose | saas-violet | ownership funnel, RFM segments, churn pills |
| 11 | Forecast & Planning | forecast | finance-dark | **forecast line + confidence band**, variance bridge, scenarios |
| 12 | Detail / Drillthrough | detail | byd-red | filter-context chips, record-level transaction table |
| 13 ★ | Executive Brief | present | finance-dark | board-ready: headline insight, KPI sparklines, 1 hero chart, "where to act" — minimal/C-suite |

> build-spec.md ครบที่ 01-04 ; 05-12 ยังไม่มี build-spec (ทำเพิ่มได้เมื่อจะเอา archetype นั้นเข้า Power BI) ; theme.json ครอบทุก archetype แล้วเพราะแยกตาม skin

> instance ที่ต่อ API จริงแล้ว: `../Projects/BYD-Overviews/` (archetype 01) และ `../Projects/Ops-Monitor-Live/` (archetype 02 ดึงจาก mock REST API พอร์ต 8010)

## วิธีรัน — DEV HUB (server เดียวเห็นทุกอย่าง)

```powershell
# ที่ root DEEPBI
python serve.py
# http://localhost:8000/                         (hub menu)
# http://localhost:8000/_templates/              (gallery 8 archetypes)
# http://localhost:8000/_templates/01-executive-overview/?skin=finance-dark
# http://localhost:8000/Projects/BYD-Overviews/web-mockup/      (ดึง /api/orders)
# http://localhost:8000/Projects/Ops-Monitor-Live/web/          (ดึง /api/metrics)
```
- `serve.py` ที่ root = static ทั้ง repo + รวม mock API ทุก project ที่ `/api/<entity>` (orders, targets, metrics, incidents) ในพอร์ตเดียว
- หน้าที่ดึง API ใช้ base แบบ **relative `/api`** → ทำงานกับ hub หรือ per-project `serve.py` ก็ได้
- ต้องเปิดผ่าน server (ไม่ใช่ double-click) เพราะ template โหลด CSS/JS ด้วย relative path
- per-project `serve.py` (ใน Projects/*/01-data-raw/mock-api/) ยังใช้ได้สำหรับรันแยกเดี่ยว ๆ

## สร้าง dashboard ใหม่ (recipe)

1. ก๊อปโฟลเดอร์ archetype ที่ใกล้โจทย์ที่สุดจาก `_templates/`
2. ใน `<head>` link 4 ไฟล์: `tokens.css`, `components.css`, `skins/skins.css`, `charts.js` (+ Chart.js CDN)
3. ตั้ง `<body class="skin-...">` เลือกโทน
4. แก้ data block (array/JSON) — โครง visual ไม่ต้องแตะ
5. chart ใช้ helper: `DS.add('canvasId', el => new Chart(el, {...DS.baseOpts(...)}))` แล้วปิดท้าย `DS.renderAll()`

### DS helper ที่ใช้บ่อย
```js
DS.fmt.num(n)            // 1,234
DS.fmt.abbr(n,'฿')       // ฿1.2M
DS.fmt.pct(n)            // +3.2%
DS.C('accent')           // อ่านค่าสี token ปัจจุบัน (ตาม skin)
DS.colors()              // [c1..c8] ของ skin ปัจจุบัน
DS.baseOpts({horizontal, stacked, dualAxis, legend, curMoney, zero})
// dualAxis แกนขวา default ฿ ; ถ้าเป็น %/x ส่ง dualAxisFmt: v=>v+'%'
DS.setSkin('finance-dark')   // สลับ skin + วาดกราฟใหม่
```

## ⚠️ กับดักที่เจอมาแล้ว (อย่าพลาดซ้ำ)

- **อย่าตั้งชื่อตัวแปร/ค่า id ทับ global สงวนของเบราว์เซอร์**: `status`, `top`, `name`, `length`, `parent`, `self`, `location`, `open`, `closed`, `event`
  - `id="status"` + `new Chart(status,…)` → ได้ `window.status` (string ว่าง) วาดไม่ขึ้น → ใช้ `getElementById`
  - `const top = [...]` → SyntaxError "already declared" (ชน `window.top`) → ทั้ง script ตาย → เปลี่ยนชื่อเป็น `leaders` ฯลฯ
- chart ต้องอ้าน `DS.C()/DS.colors()` **ตอน build** (ไม่ cache สีไว้) ไม่งั้นสลับ skin แล้วสีไม่เปลี่ยน
- เปิดผ่าน `file://` จะโดน CORS/relative-path พัง — ใช้ http server เสมอ

## เชื่อมเข้า Power BI

- **Power BI theme พร้อมใช้ 1 ไฟล์ต่อ skin**: `skins/powerbi/<skin>.json` (byd-red, finance-dark, saas-violet, luxury-gold, command-center) → View → Themes → Browse
- **build-spec.md ต่อ archetype**: อยู่ในโฟลเดอร์ template แต่ละตัว (`_templates/0X-*/build-spec.md`) — map visual → Power BI native visual + field + measure ; archetype 01-04 มีครบแล้ว
- ตัวอย่าง project จริง (ต่อ API + DAX): `../Projects/BYD-Overviews/02-build-spec/`
