# BYD Overviews — Data Model

Star schema 2 fact + dimension ร่วม (conformed) — **ห้ามผูก fact-to-fact** เด็ดขาด

## Grain (สำคัญที่สุด — เช็คก่อนทำอย่างอื่น)

| ตาราง | Grain (1 แถว = อะไร) | ชนิด |
|---|---|---|
| `Orders` | 1 order = รถ 1 คัน | Fact (transaction) |
| `Targets` | 1 เป้า = เดือน × ภูมิภาค | Fact (month snapshot) |

> Orders กับ Targets อยู่คนละ grain → **เชื่อมผ่าน dimension ร่วม** (Date, Region) ไม่ใช่ผูกตรงกัน ถ้าผูก Orders↔Targets ตรง ๆ ตัวเลขจะ fan-out ผิดทันที

## ตาราง

### Fact: Orders  (จาก `GET /api/orders` → field `data`)
```
order_id, order_date (date), delivery_date (date, nullable),
model, segment, region, province, dealer_id, dealer_name,
channel, customer_type, status, unit_price, quantity, revenue, salesperson_id
```

### Fact: Targets  (จาก `GET /api/targets`)
```
month (text "YYYY-MM" → แปลงเป็น date วันที่ 1), region, target_units, target_revenue
```

### Dimension: Date  (สร้างใน Power BI ด้วย DAX — ดู measures.dax)
```
Date, Year, Quarter, MonthNo, MonthName, YearMonth, MonthYearLabel, IsCurrentYear
```
ครอบคลุม 2025-01-01 → 2026-12-31 · ตั้งเป็น Date table (Mark as date table)

### Dimension: Geography  (ดึง distinct จาก Orders หรือทำเป็นตารางแยก)
```
Region, Province
```

### Dimension: Product  (distinct จาก Orders)
```
Model, Segment
```

### Dimension: Dealer  (distinct จาก Orders)
```
dealer_id, dealer_name, Region
```

## Relationships

```
Date[Date]        1 ──< Orders[order_date]          (active, single)
Date[Date]        1 ──< Targets[month]              (active, single)   ← เชื่อม 2 fact ผ่าน Date
Geography[Region] 1 ──< Orders[region]              (single)
Geography[Region] 1 ──< Targets[region]             (single)           ← เชื่อม 2 fact ผ่าน Region
Product[Model]    1 ──< Orders[model]               (single)
Dealer[dealer_id] 1 ──< Orders[dealer_id]           (single)
```

ทิศ filter ทั้งหมด single direction (dimension → fact) — ไม่ใช้ bidirectional เพื่อกัน ambiguous path

## หมายเหตุการ clean ใน Power Query

1. `GET /api/orders` คืน JSON envelope → drill ลง record `data` → `To Table` → expand columns
2. แปลง `order_date`, `delivery_date` เป็น Date type (locale en-US)
3. `Targets.month` ("2025-01") → เติม "-01" แล้วแปลงเป็น Date เพื่อ join กับ Date table
4. ตั้ง type ให้ `unit_price`, `revenue`, `quantity`, `target_units`, `target_revenue` เป็น number
5. `delivery_date` มี null (order ที่ยัง Booked) — ปล่อยไว้ อย่า fill

> ดีไซน์ web mockup ใช้ grain order-level เดียวกับนี้เป๊ะ → ตัวเลขที่เห็นบนเว็บ = ตัวเลขที่ Power BI จะได้
