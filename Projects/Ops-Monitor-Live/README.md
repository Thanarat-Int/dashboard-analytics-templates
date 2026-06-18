# Ops-Monitor-Live

Operational monitoring dashboard (real-time control room) — **web mockup ดึงข้อมูลจาก mock REST API จริง**
อิง archetype **02 Operational Monitor** จาก `_templates/` + skin `command-center`

สถานะ: ✅ mock API + web dashboard (ดึงจาก API) เสร็จ · ⏳ รอ observability API จริง · ⏳ ยังไม่ประกอบใน Power BI

## โครงสร้างโฟลเดอร์

```
Ops-Monitor-Live/
├─ 01-data-raw/
│   └─ mock-api/   generate.py, serve.py, metrics.json, incidents.json   ← Mock REST API
├─ web/            index.html, preview.png   ← dashboard (fetch จาก API, same-origin)
└─ README.md
```

`web/index.html` เป็นสำเนาของ `_templates/02-operational-monitor/index.html`
ต่างกันที่: แทน inline demo arrays ด้วยการ `fetch` จาก API + แก้ relative path ของ design system

> **Relative-path depth:** หน้าเว็บอยู่ที่ `Projects/Ops-Monitor-Live/web/`
> ดังนั้น path ไป `_design-system/` คือ `../../../_design-system/`
> (`web/` → `Ops-Monitor-Live/` → `Projects/` → root DEEPBI) — ลึกกว่า template ใน `_templates/` 1 ชั้น
>
> **เพราะ `_design-system/` อยู่นอกโฟลเดอร์โปรเจกต์** (ใช้ร่วมกันทุกโปรเจกต์ — ต้องคงไว้ generic)
> `serve.py` จึงตั้ง document root = **root DEEPBI** ไม่ใช่โฟลเดอร์ `Ops-Monitor-Live/`
> เพื่อให้ `../../../_design-system/` เข้าถึงได้ผ่าน HTTP (ไม่ทะลุออกนอก root)
> ด้วยเหตุนี้ URL ของ dashboard จึงเป็น `/Projects/Ops-Monitor-Live/web/`
> ส่วน API ยัง same-origin ที่ `http://localhost:8010/api/...`

## วิธีรัน (2 ขั้น)

```powershell
# 1) สร้างข้อมูล (รันครั้งเดียว; idempotent เพราะ seed คงที่)
cd 01-data-raw/mock-api
python generate.py

# 2) สตาร์ท mock API (serve ทั้ง API + ไฟล์ static จาก project root)
python serve.py

# 3) เปิด dashboard ในเบราว์เซอร์
#    http://localhost:8010/Projects/Ops-Monitor-Live/web/
```

หน้าเว็บโหลดแบบ same-origin (เสิร์ฟจาก root DEEPBI) จึง fetch `http://localhost:8010/api/...` ได้โดยไม่ติด CORS
ถ้ายังไม่ได้สตาร์ท serve.py หน้าเว็บจะขึ้นข้อความบอกให้รันเซิร์ฟเวอร์ก่อน

## Endpoints

- `http://localhost:8010/api/metrics` — 24 จุดรายชั่วโมง (last 24h): `timestamp, throughput_rpm, latency_ms_p50, latency_ms_p95, error_rate_pct`
  - รองรับ `?page=&page_size=` เพื่อซ้อม pagination เช่น `?page=1&page_size=12`
- `http://localhost:8010/api/incidents` — ~12 incident records (7d): `id, opened_at, service, severity, status, message, age_min`
- ทุก response เป็น envelope: `meta` (source/domain/generated_at/version) + `pagination` + `data`
- การ rollup severity แบบ 7 วัน (stacked bar) คำนวณบนหน้าเว็บจาก `incidents.data`

## Mapping visual → API

| Visual | Source | หมายเหตุ |
|---|---|---|
| KPI tiles | metrics + incidents | SLA = 100 − avg(error_rate_pct), throughput ล่าสุด/พีค, latency p50/p95 ล่าสุด, จำนวน incident ที่ยัง Open/Ack |
| Throughput (line, 24h) | `metrics.throughput_rpm` | |
| Incidents by Severity (stacked bar, 7d) | `incidents` → rollup ตาม day-of-week × severity | |
| Latency p50 / p95 (line, 24h) | `metrics.latency_ms_p50/p95` | |
| Active Alert Feed (table) | `incidents` (ใหม่สุดก่อน) | |

ทุก chart อ่านสีจาก `DS.C()/DS.colors()` ตอน build → สลับ skin แล้วสีเปลี่ยนตาม (รองรับ `?skin=` ด้วย)

## เปลี่ยนไปใช้ API จริง

- web: แก้ค่าตัวแปร `API` ใน `web/index.html` ให้ชี้ base URL ของ source จริง
- Power BI: Get Data → Web → endpoint จริง + เพิ่ม auth header
  (`Web.Contents(url,[Headers=[Authorization="Bearer ..."]])`)
- โครง visual / mapping **ไม่ต้องรื้อ** ถ้า field ต้นทางหน้าตาเหมือน mock (envelope `data[]`)
