# Funnel & Conversion — Power BI Build Spec

Archetype 04 · diagnose — funnel drop-off, conversion, acquisition, retention
คู่มือประกอบ dashboard ใน Power BI Desktop ให้ตรงกับ `index.html`
ทุก visual ด้านล่าง = **native visual ของ Power BI** (ไม่ต้องลง custom visual)

## 0. ตั้งค่าหน้า (ทำก่อนเริ่ม)

1. โหลด data (events / signups / subscriptions / cohort) แล้วสร้าง Date table + relationship
2. สร้าง measures ตามตารางข้อ 2 (ชื่อภาษาอังกฤษ)
3. **View → Themes → Browse for themes** → เลือก `../../_design-system/skins/powerbi/saas-violet.json` (default skin ของ archetype นี้)
4. Page size: **Canvas 16:9 (1280 × 720)** · พื้นหลังหน้าให้ theme จัดการ (`#F7F7FB`)

## 1. Layout grid (เทียบ mockup)

```
┌───────────────────────────── Header (title + Last 30d / Channel) ────────────┐
├──────────┬──────────┬──────────┬──────────┬──────────┐  ← KPI row (5 cards)
│ Visitors │ Signups  │ Paid     │ CAC      │ Net MRR  │
│          │          │ Conv.    │          │          │
├──────────┴──────────┴──────────┴──────┬───┴──────────┤  ← main row  (c-21)
│ Acquisition Funnel — drop-off          │ Signup→Paid   │
│ (Funnel visual)                        │ by Channel    │
│                                        │ (clustered col)│
├────────────────────────┬───────────────┴──────────────┤  ← second row (c-21)
│ Weekly Cohort Retention │ Stage Conversion Detail       │
│ (line)                  │ (table)                       │
└─────────────────────────┴──────────────────────────────┘
```

## 2. Visual-by-visual mapping

| # | บน mockup | Power BI visual | Fields / wells | Measure |
|---|---|---|---|---|
| 1 | KPI: Visitors | **Card (new)** | — | `Visitors` ; `Visitors Δ%` ; sub = unique 30d |
| 2 | KPI: Signups | **Card (new)** | — | `Signups` ; `Signups Δ%` ; sub = `Signup Rate %` |
| 3 | KPI: Paid Conversion | **Card (new)** | — | `Paid Conversion %` ; Δ ppt ; sub = signup → paid |
| 4 | KPI: CAC | **Card (new)** | — | `CAC` ; `CAC Δ%` (ลด = ดี) ; sub = blended |
| 5 | KPI: Net MRR | **Card (new)** | — | `Net MRR` ; `MRR Δ%` ; sub = net new this month |
| 6 | Acquisition Funnel | **Funnel chart** (native) | Group/Category: `Stage` (Visitors→Signups→Activated→Trial→Paid) ; Values: `Users at Stage` | — |
| 7 | Signup → Paid by Channel | **Clustered column chart** | X-axis: `Channel[name]` ; Values: `Signups` + `Paid` ; สี Signups = c1 / Paid = c2 | — |
| 8 | Weekly Cohort Retention | **Line chart** | X-axis: `Week index (W0..W6)` ; Legend: `Cohort[month]` ; Values: `Retention %` ; ปิด start-at-zero | `Retention % = DIVIDE([Active in week], [Cohort size])` |
| 9 | Stage Conversion Detail | **Table** | Columns: `Stage`, `Users`, `Conv from prev %`, `Drop-off %` | `Conv from prev % = DIVIDE([Users], [Users prev stage])` ; `Drop-off % = 1 - [Conv from prev %]` |

### 2a. Funnel (#6) — ใช้ native Funnel visual
- ใน web mock เป็น horizontal bar ที่เรียงค่าลดหลั่น ; ใน Power BI ใช้ **Funnel chart (native)** ตรง ๆ
- Funnel จะคำนวณ % vs first stage และ % vs previous ให้ในตัว (ใช้แทนคอลัมน์ในตาราง #9 ได้)
- ถ้าต้องการสีไล่ตาม stage ให้ใช้ dataColors[0..4] ตามลำดับ stage

## 3. หมายเหตุการตั้งค่าให้เหมือน mockup
- **Clustered column (#7):** Signups = c1, Paid = c2, เปิด legend + data label
- **Retention line (#8):** Mar = c1, Apr = c2, May = c3 (dash) ; ปิด zero baseline ; cohort ล่าสุดที่ยังไม่ครบ week ปล่อยเป็น null (เส้นขาด)
- **Table (#9):** Drop-off แสดงเป็นสีแดง (`bad`) ผ่าน conditional font color
- ทุก visual background/border ให้ theme `saas-violet.json` จัดการ

## 4. Interaction plan
- **Slicer:** `Date` (relative last 30d), `Channel[name]`, `Cohort[month]`
- **Cross-filter:** คลิก channel ใน #7 → funnel + table กรองตาม channel
- **Drillthrough:** ไปหน้า cohort/user detail

## 5. QA checklist
- [ ] Funnel stage แรก = `Visitors` ; stage สุดท้าย = `Paid` ; ค่าลดหลั่นถูกต้อง
- [ ] `Paid Conversion %` = Paid / Signups ตรงกับ KPI #3
- [ ] Conv from prev % แต่ละ stage ตรงกับ funnel native (% of previous)
- [ ] Retention W0 = 100% ทุก cohort
- [ ] สีตรงกับ theme `saas-violet.json` (c1 = #6D5CF6)
