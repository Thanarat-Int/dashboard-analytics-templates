# BYD Overviews — Power BI Build Spec

คู่มือประกอบ dashboard ใน Power BI Desktop ให้ตรงกับ `web-mockup/index.html`
ทุก visual ด้านล่าง = **native visual ของ Power BI** (ไม่ต้องลง custom visual)

## 0. ตั้งค่าหน้า (ทำก่อนเริ่ม)

1. **Get Data → Web** → `http://localhost:8000/api/orders` → drill `data` → expand (ดู data-model.md)
2. ทำซ้ำกับ `http://localhost:8000/api/targets`
3. สร้าง Date table + measures จาก `measures.dax`, ตั้ง relationship ตาม `data-model.md`
4. **View → Themes → Browse for themes** → เลือก `theme.json`
5. Page size: **Canvas 16:9 (1280 × 720)** · พื้นหลังหน้า `#0A0E1A`

## 1. Layout grid (เทียบ mockup)

```
┌───────────────────────────── Header (title + as-of) ──────────────────────────┐
├──────────┬──────────┬──────────┬──────────┬──────────┐  ← KPI row (5 cards)
│ Units    │ Revenue  │ Target   │ Avg Sell │ Delivered│
│ Sold     │ (YTD)    │ Achiev.  │ Price    │ /Backlog │
├──────────┴──────────┴──────────┴──────────┼──────────┤  ← main row
│ Monthly Units & Revenue vs Target          │ Order     │
│ (line + clustered column, 2 axes)          │ Status    │
│                                            │ (donut)   │
├──────────────────┬──────────────────┬──────┴──────────┤  ← bottom row
│ Units by Model   │ Actual vs Target │ Top Dealers      │
│ (clustered bar)  │ by Region (col)  │ (table)          │
└──────────────────┴──────────────────┴──────────────────┘
```

## 2. Visual-by-visual mapping

| # | บน mockup | Power BI visual | Fields / wells | Measure |
|---|---|---|---|---|
| 1 | KPI: Units Sold | **Card (new)** | — | `Units Sold` ; callout LY = `Units Sold LY` ; trend = `Units YoY %` |
| 2 | KPI: Revenue | **Card (new)** | — | `Revenue` ; `Revenue YoY %` |
| 3 | KPI: Target Achievement | **Card (new)** + bar | — | `Target Achievement %` ; bg/บาร์ใช้ `Achievement Color` (conditional) |
| 4 | KPI: Avg Selling Price | **Card (new)** | — | `Avg Selling Price` |
| 5 | KPI: Delivered/Backlog | **Card (new)** | — | `Delivered Units` (+ `Backlog Units` เป็น subtitle) |
| 6 | Monthly trend | **Line and clustered column chart** | X-axis: `Date[MonthYearLabel]` ; Column: `Units Sold` ; Line: `Revenue` (2nd axis) + `Target Units` (1st axis, dashed) | — |
| 7 | Order Status donut | **Donut chart** | Legend: `Orders[status]` ; Values: `Units Sold` (หรือ count) | สี: Delivered เขียว / Booked น้ำเงิน / Cancelled แดง |
| 8 | Units by Model | **Clustered bar chart** | Y-axis: `Product[Model]` ; X: `Units Sold` ; เรียงจากมาก→น้อย | — |
| 9 | Actual vs Target by Region | **Clustered column chart** | X: `Geography[Region]` ; Values: `Units Sold` + `Target Units` | — |
| 10 | Top Dealers | **Table** หรือ **Matrix** | Rows: `Dealer[dealer_name]` ; Values: `Units Sold`, `Revenue`, `% of total` ; Top N filter = 7 ; data bar บน Units | — |

> **% of total** ใน table: เพิ่ม measure `Dealer Share % = DIVIDE([Units Sold], CALCULATE([Units Sold], ALL(Dealer)))`

## 3. การตั้งค่าที่ทำให้ "เหมือน mockup" (ธีม BYD ขาว-แดง)

สีแบรนด์ทางการ: **Festival Red `#D70C19`** / digital red `#E2231A`–`#E91B21` · **Cool Grey `#686D71`** · White (red-on-white ตาม guideline)

- **Card (new):** accent bar ซ้ายสีแดง `#E2231A`, callout font 28 สี `#171A1F`, label `#697079` ; KPI delta ใช้เขียว `#12875A` (ขึ้น) / แดง `#E2231A` (ลง)
- **Combo chart:** column units = `#E2231A`, revenue line = charcoal `#2B2F36` เปิด shaded area อ่อน, target line = grey `#8A9099` dash
- **Donut:** inner 66%, Delivered `#E2231A` / Booked `#2B2F36` / Cancelled `#D4D8DD`
- **Units by Model:** ไล่โทนแดง→เทา (top = `#E2231A` ลงไปเป็นเทา) ไม่ใช้สีรุ้ง
- **Actual vs Target by Region:** Actual `#E2231A` / Target `#CBD0D6`
- **Bar/Column:** ปิด gridline แกนหมวด, เปิด data label, rounded corner
- **ทุก visual:** background `#FFFFFF`, border `#E7E9ED` radius 12, page `#F3F4F6` (theme จัดให้แล้ว)

## 4. Interaction plan

- **Slicer:** `Date[Year]` (หรือ relative date), `Geography[Region]`, `Product[Model]` — วางเป็นแถบบน/ซ้าย
- **Cross-filter:** คลิก model/region/dealer → ทุก visual กรองตาม (เปิด default)
- **Drillthrough:** จากหน้านี้ → หน้า "Dealer Detail" โดยส่ง `dealer_name`
- **Tooltip:** custom tooltip page โชว์ trend mini ของ dealer/model ที่ hover

## 5. QA checklist (ทำก่อนส่ง)

- [ ] `Units Sold` (YTD 2026) = **1,009** ตรงกับ mockup
- [ ] `Revenue` = **฿1.12B** · `Achievement` = **96%** · `YoY` = **+32.9%**
- [ ] ผลรวม Units by Model = ผลรวม Units by Region = 1,009 (ไม่มี fan-out)
- [ ] Targets ไม่ทำให้ Orders เบิ้ล (เช็ค grain — ดู data-model.md)
- [ ] Cancelled ไม่ถูกนับใน Units Sold แต่ปรากฏใน donut
- [ ] เปลี่ยน slicer ปี → ทุก KPI/visual ขยับสอดคล้องกัน
