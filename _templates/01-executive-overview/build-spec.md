# Executive Overview — Power BI Build Spec

Archetype 01 · monitor — KPI + trend + breakdown
คู่มือประกอบ dashboard ใน Power BI Desktop ให้ตรงกับ `index.html`
ทุก visual ด้านล่าง = **native visual ของ Power BI** (ไม่ต้องลง custom visual)

## 0. ตั้งค่าหน้า (ทำก่อนเริ่ม)

1. โหลด data (Get Data → Web หรือแหล่งจริง) แล้วสร้าง Date table + relationship
2. สร้าง measures ตามตารางข้อ 2 (เก็บชื่อเป็นภาษาอังกฤษ)
3. **View → Themes → Browse for themes** → เลือก `../../_design-system/skins/powerbi/byd-red.json` (default skin ของ archetype นี้)
   - สลับลุคได้โดย import theme ตัวอื่นจากโฟลเดอร์ `powerbi/` (finance-dark, saas-violet, luxury-gold, command-center)
4. Page size: **Canvas 16:9 (1280 × 720)** · พื้นหลังหน้าให้ theme จัดการ (`#F3F4F6`)

## 1. Layout grid (เทียบ mockup)

```
┌───────────────────────────── Header (title + YTD / As-of) ───────────────────┐
├──────────┬──────────┬──────────┬──────────┬──────────┐  ← KPI row (5 cards)
│ Revenue  │ Units    │ Target   │ Avg Sell │ Delivered│
│ (YTD)    │ Sold     │ Achiev.  │ Price    │ /Backlog │
├──────────┴──────────┴──────────┴──────┬───┴──────────┤  ← main row  (c-21)
│ Revenue & Units vs Target              │ Status Mix    │
│ (line + clustered column, 2 axes)      │ (donut)       │
├────────────────┬──────────────────┬────┴──────────────┤  ← bottom row (c-211)
│ By Category    │ Actual vs Target │ Top Performers     │
│ (clustered bar)│ by Region (col)  │ (table)            │
└────────────────┴──────────────────┴────────────────────┘
```

## 2. Visual-by-visual mapping

| # | บน mockup | Power BI visual | Fields / wells | Measure |
|---|---|---|---|---|
| 1 | KPI: Revenue (YTD) | **Card (new)** | — | `Revenue` ; trend = `Revenue YoY %` ; sub = `Revenue LY` |
| 2 | KPI: Units Sold (YTD) | **Card (new)** | — | `Units Sold` ; `Units YoY %` ; sub = `Units Sold LY` |
| 3 | KPI: Target Achievement + bar | **Card (new)** + เส้น bar | — | `Target Achievement %` ; bar = `Units Sold` / `Target Units` ; sub = `Units Sold` / `Target Units` |
| 4 | KPI: Avg Selling Price | **Card (new)** | — | `Avg Selling Price` = DIVIDE([Revenue],[Units Sold]) |
| 5 | KPI: Delivered / Backlog | **Card (new)** | — | `Delivered Units` (+ `Backlog Units` เป็น subtitle) |
| 6 | Revenue & Units vs Target | **Line and clustered column chart** | X-axis: `Date[MonthLabel]` ; Column: `Units Sold` ; Line (2nd axis): `Revenue` ; Line (1st axis, dashed): `Target Units` | — |
| 7 | Status Mix | **Donut chart** | Legend: `Orders[status]` ; Values: `Units` (count/sum) ; inner 66% ; สี Delivered = c1 / Booked = c2 / Cancelled = c6 | — |
| 8 | By Category | **Clustered bar chart** | Y-axis: `Product[Category]` ; X: `Units Sold` ; เรียงมาก→น้อย | — |
| 9 | Actual vs Target by Region | **Clustered column chart** | X-axis: `Geography[Region]` ; Values: `Units Sold` (Actual) + `Target Units` | — |
| 10 | Top Performers | **Table** หรือ **Matrix** | Rows: `Entity[name]` ; Values: `Units Sold`, `Revenue`, `Share %` ; Top N filter = 7 ; data bar บน Units | `Share % = DIVIDE([Units Sold], CALCULATE([Units Sold], ALL(Entity)))` |

## 3. หมายเหตุการตั้งค่าให้เหมือน mockup

- **Card (new):** accent bar ซ้าย = `dataColors[0]`, callout 28, label สี secondary ; delta ขึ้น = `good` / ลง = `bad`
- **Combo (#6):** column Units = c1 ; Revenue line = c2 + shaded area อ่อน ; Target line = c3 dash ; เปิด 2 แกน (Units บน Y1, Revenue บน Y2)
- **Donut (#7):** เปิด detail label เป็น % ; vendor border สี card
- **Bar/Column:** ปิด gridline แกนหมวด, เปิด data label, rounded corner ; ทุก visual background/border ให้ theme จัดการ

## 4. Interaction plan
- **Slicer:** `Date[Year]` (หรือ relative date), `Geography[Region]`, `Product[Category]`
- **Cross-filter:** คลิก category/region/entity → กรองทุก visual (เปิด default)
- **Drillthrough:** ไปหน้า detail ของ entity ที่เลือก

## 5. QA checklist
- [ ] ผลรวม By Category = ผลรวม By Region = `Units Sold` (ไม่มี fan-out)
- [ ] Cancelled ไม่ถูกนับใน `Units Sold` แต่ปรากฏใน donut
- [ ] เปลี่ยน slicer ปี → ทุก KPI/visual ขยับสอดคล้องกัน
- [ ] สีตรงกับ theme `byd-red.json` (c1 = #E2231A)
