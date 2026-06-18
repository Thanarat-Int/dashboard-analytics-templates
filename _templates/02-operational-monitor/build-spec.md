# Operational Monitor — Power BI Build Spec

Archetype 02 · monitor real-time — SLA, throughput, incidents, utilization
คู่มือประกอบ dashboard ใน Power BI Desktop ให้ตรงกับ `index.html`
ทุก visual ด้านล่าง = **native visual ของ Power BI** (ไม่ต้องลง custom visual)

## 0. ตั้งค่าหน้า (ทำก่อนเริ่ม)

1. โหลด data (metrics / incidents / utilization feed) แล้วสร้าง Date/Time table + relationship
2. สร้าง measures ตามตารางข้อ 2
3. **View → Themes → Browse for themes** → เลือก `../../_design-system/skins/powerbi/command-center.json` (default skin ของ archetype นี้)
4. Page size: **Canvas 16:9 (1280 × 720)** · พื้นหลังหน้าให้ theme จัดการ (`#070A0F`)
5. ตั้ง **Page refresh** (Auto page refresh) สำหรับโหมด live ถ้าแหล่งข้อมูล DirectQuery รองรับ

## 1. Layout grid (เทียบ mockup)

```
┌───────────────────────────── Header (title + LIVE / 24h) ────────────────────┐
├──────────┬──────────┬──────────┬──────────┬──────────┐  ← KPI row (5 cards)
│ SLA      │ Active   │ Through- │ Avg      │ Uptime   │
│ Attain.  │ Incidents│ put      │ Latency  │ (30d)    │
├──────────┴──────────┴──────────┴──────┬───┴──────────┤  ← main row  (c-21)
│ Throughput (req/min · 24h)             │ Incidents by  │
│ (area line)                            │ Severity (7d) │
│                                        │ (stacked col) │
├────────────────────────┬───────────────┴──────────────┤  ← bottom row (c-12)
│ Service Utilization     │ Active Alert Feed             │
│ (clustered bar +        │ (table)                       │
│  conditional color)     │                               │
└─────────────────────────┴──────────────────────────────┘
```

## 2. Visual-by-visual mapping

| # | บน mockup | Power BI visual | Fields / wells | Measure |
|---|---|---|---|---|
| 1 | KPI: SLA Attainment + bar | **Card (new)** + bar | — | `SLA Attainment %` ; bar = `SLA Attainment %` ; sub = target ; delta vs target |
| 2 | KPI: Active Incidents | **Card (new)** | — | `Active Incidents` (+ breakdown critical/major เป็น subtitle) |
| 3 | KPI: Throughput | **Card (new)** | — | `Throughput rpm` ; `Throughput Δ%` ; peak เป็น sub |
| 4 | KPI: Avg Latency | **Card (new)** | — | `Avg Latency ms` ; `Latency Δ%` ; p95 เป็น sub |
| 5 | KPI: Uptime (30d) + bar | **Card (new)** + bar | — | `Uptime % 30d` ; SLO เป็น sub |
| 6 | Throughput 24h | **Line chart** (area fill) | X-axis: `Time[Hour]` ; Y: `Throughput rpm` ; เปิด area / shade ด้วย `--accent-soft` | — |
| 7 | Incidents by Severity (7d) | **Stacked column chart** | X-axis: `Date[Day]` ; Legend: `Incident[severity]` ; Values: `Incident Count` ; สี Critical = c5 / Major = c3 / Minor = c2 | — |
| 8 | Service Utilization | **Clustered bar chart** | Y-axis: `Service[name]` ; X: `Utilization %` ; **Conditional formatting (rules)** บนสี bar | `Utilization %` |
| 9 | Active Alert Feed | **Table** | Columns: `Time`, `Service`, `Severity`, `Message`, `Age` ; sort ตาม time ล่าสุด | — |

### 2a. Conditional formatting — Service Utilization (#8)
ตั้ง **Data colors → Format by → Rules** บน measure `Utilization %` (ตรงกับ threshold ใน mockup):

| เงื่อนไข | สี |
|---|---|
| `>= 85` | `bad` / c5 (`#FF5C7A`) — overload |
| `>= 70` และ `< 85` | c3 (`#FFC857`) — warning |
| `< 70` | c1 (`#19E3C4`) — healthy |

> ทำแบบเดียวกันบน Severity pill ในตาราง Alert Feed ได้ด้วย conditional font color: Critical = bad, Major = c3, Minor = neutral.

## 3. หมายเหตุการตั้งค่าให้เหมือน mockup
- **Throughput area (#6):** line c1, fill โปร่งบาง, ปิด point marker, smooth
- **Stacked column (#7):** เปิด legend, ปิด gridline แกนหมวด
- ทุก visual background/border/มุมโค้ง ให้ theme `command-center.json` จัดการ (radius 10)

## 4. Interaction plan
- **Slicer:** `Service[name]`, `Date` window (relative: last 24h / 7d / 30d)
- **Cross-filter:** คลิก service ใน utilization → กรอง alert feed + incidents
- **Auto page refresh** สำหรับโหมด LIVE

## 5. QA checklist
- [ ] Utilization สีเปลี่ยนตาม threshold (85 / 70) ถูกต้อง
- [ ] Active Incidents = จำนวน incident ที่ status เปิดอยู่จริง
- [ ] Stacked column รวมทุก severity = total incidents ต่อวัน
- [ ] สีตรงกับ theme `command-center.json` (c1 = #19E3C4)
