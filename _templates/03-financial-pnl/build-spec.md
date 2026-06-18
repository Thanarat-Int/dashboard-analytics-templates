# Financial P&L — Power BI Build Spec

Archetype 03 · explain/diagnose — waterfall, variance vs budget, margin trend
คู่มือประกอบ dashboard ใน Power BI Desktop ให้ตรงกับ `index.html`
ทุก visual ด้านล่าง = **native visual ของ Power BI** (ไม่ต้องลง custom visual)

## 0. ตั้งค่าหน้า (ทำก่อนเริ่ม)

1. โหลด data (GL / P&L line items + budget) แล้วสร้าง Date table + relationship
2. สร้าง measures ตามตารางข้อ 2 (ชื่อภาษาอังกฤษ)
3. **View → Themes → Browse for themes** → เลือก `../../_design-system/skins/powerbi/finance-dark.json` (default skin ของ archetype นี้)
4. Page size: **Canvas 16:9 (1280 × 720)** · พื้นหลังหน้าให้ theme จัดการ (`#0C1018`)

## 1. Layout grid (เทียบ mockup)

```
┌───────────────────────────── Header (title + FY2025 / ฿M) ───────────────────┐
├──────────┬──────────┬──────────┬──────────┬──────────┐  ← KPI row (5 cards)
│ Revenue  │ Gross    │ EBIT     │ Net      │ Budget   │
│          │ Margin   │          │ Profit   │ Variance │
├──────────┴──────────┴──────────┴──────┬───┴──────────┤  ← main row  (c-21)
│ P&L Waterfall (฿M)                     │ Operating Exp │
│ (Waterfall chart)                      │ Mix (donut)   │
├────────────────────────┬───────────────┴──────────────┤  ← bottom row (c-12)
│ Gross & Net Margin      │ P&L Statement —               │
│ Trend (line)            │ Actual vs Budget (matrix)     │
└─────────────────────────┴──────────────────────────────┘
```

## 2. Visual-by-visual mapping

| # | บน mockup | Power BI visual | Fields / wells | Measure |
|---|---|---|---|---|
| 1 | KPI: Revenue | **Card (new)** | — | `Revenue` ; `Revenue YoY %` ; sub = `Revenue LY` |
| 2 | KPI: Gross Margin | **Card (new)** | — | `Gross Margin %` ; YoY ; sub = `Gross Profit` |
| 3 | KPI: EBIT | **Card (new)** | — | `EBIT` ; YoY ; sub = `EBIT Margin %` |
| 4 | KPI: Net Profit | **Card (new)** | — | `Net Profit` ; YoY ; sub = `Net Margin %` |
| 5 | KPI: Budget Variance + bar | **Card (new)** + bar | — | `Budget Variance` ; bar = `% of Plan` ; sub = `% of Plan` |
| 6 | P&L Waterfall | **Waterfall chart** (native) | Category: `PnL[LineItem]` (เรียง Revenue → COGS → Gross → OpEx → EBIT → Tax → Net) ; Y: `Amount` | — |
| 7 | Operating Expense Mix | **Donut chart** | Legend: `OpEx[category]` ; Values: `OpEx Amount` ; inner 62% ; สี = dataColors[0..3] | — |
| 8 | Gross & Net Margin Trend | **Line chart** | X-axis: `Date[Quarter]` ; Values: `Gross Margin %` (c1, area) + `Net Margin %` (c2) ; ปิด start-at-zero | — |
| 9 | P&L Statement Actual vs Budget | **Matrix** (หรือ Table) | Rows: `PnL[LineItem]` ; Values: `Actual`, `Budget`, `Variance`, `Variance %` ; subtotal rows (Gross/EBIT/Net) ตัวหนา | `Variance = [Actual]-[Budget]` ; `Variance % = DIVIDE([Variance], ABS([Budget]))` |

### 2a. ⚠️ Waterfall (#6) — ใช้ native visual จริง
ใน web mock กราฟนี้ถูก **ปลอม** ด้วย **stacked bar 2 ชั้น** (dataset `_base` โปร่งใส + dataset `value`) เพื่อเลื่อนแท่งให้ลอย — เป็นเทคนิคของ Chart.js เท่านั้น
**ใน Power BI ไม่ต้องทำแบบนั้น** ให้ใช้ **Waterfall chart (native)** ตรง ๆ:
- Category = `PnL[LineItem]` เรียงตามลำดับงบ (Revenue, COGS, Gross Profit, OpEx, EBIT, Tax, Net Profit)
- Y = measure `Amount` (รายได้เป็นบวก, COGS/OpEx/Tax เป็นลบ)
- ตั้ง subtotal/total ที่ Gross Profit, EBIT, Net Profit ด้วย **Breakdown → exclude** หรือใช้ field "total" ของ waterfall
- สี: increase = `good`, decrease = `bad`, total = `accent` (theme ตั้ง good/bad ให้แล้ว)

### 2b. Conditional formatting — variance ในตาราง (#9)
สี font ของ Variance/Variance %: ดี = `good` / แย่ = `bad` โดยทิศ "ดี" ขึ้นกับบรรทัด — COGS/OpEx/Tax ติดลบถือว่าดี (ประหยัด) ส่วน Revenue/Gross/EBIT/Net บวกถือว่าดี (logic เดียวกับ mockup)

## 3. หมายเหตุการตั้งค่าให้เหมือน mockup
- **Donut (#7):** legend custom ใต้กราฟ (ใน PBI เปิด detail label = value ฿M)
- **Margin line (#8):** Gross % = c1 + area fill, Net % = c2, ปิด zero baseline ให้เห็น movement
- ทุก visual background/border ให้ theme `finance-dark.json` จัดการ

## 4. Interaction plan
- **Slicer:** `Date[FY]`, `Date[Quarter]`, business unit (ถ้ามี)
- **Cross-filter:** คลิก OpEx category ใน donut → ตาราง/waterfall กรองตาม
- **Drillthrough:** ไปหน้า detail ของ line item

## 5. QA checklist
- [ ] Waterfall ปิดที่ Net Profit = ค่าจริง (เช็คผลรวม Revenue − COGS − OpEx − Tax)
- [ ] subtotal Gross/EBIT/Net ตรงกับ matrix
- [ ] Variance = Actual − Budget ทุกบรรทัด ; ทิศสี (good/bad) ถูกตาม line type
- [ ] สีตรงกับ theme `finance-dark.json` (c1 = #27C2A0)
