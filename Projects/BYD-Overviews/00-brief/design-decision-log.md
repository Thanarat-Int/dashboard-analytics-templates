# BYD Overviews — Design Decision Log

> โปรเจกต์ฝึก: ออกแบบ web dashboard ระดับนำเสนอ → ใช้เป็น guide ประกอบใน Power BI
> Data: mock API (จำลอง response รถ EV ตลาดไทย) จนกว่า API จริงของ BYD จะมา

## Business intake (assumption — ยังไม่มี brief จริง)

- **Dashboard objective:** ให้ผู้บริหาร BYD เห็นภาพรวมยอดขายรถ (คัน + รายได้) เทียบเป้า ในหน้าเดียว รู้ทันทีว่าควรห่วงรุ่น/ภูมิภาค/dealer ไหน
- **Primary audience:** Executive (country head / sales director)
- **Top decision questions:**
  1. YTD ขายได้กี่คัน/กี่บาท ถึงเป้าไหม โตจากปีก่อนแค่ไหน
  2. รุ่นไหน/ภูมิภาคไหนเป็น driver และที่ไหนหลุดเป้า
  3. มี pipeline (Booked) รออยู่เท่าไร เทียบส่งมอบจริง
- **Critical KPIs:** Units Sold, Revenue, Target Achievement %, YoY %, Avg Selling Price, Delivered/Backlog

## Design decision log

```text
- Audience:            Executive (ดูเร็ว 5-10 วินาทีต่อ insight)
- Primary decision:    Monitor + Diagnose (เฝ้าผล + หา driver/จุดหลุดเป้า)
- Data grain:          Order-level (1 แถว = รถ 1 คัน) -> aggregate ได้ทุกมุม
- Recommended pages:   1 หน้า Overview (เฟสแรก) + drillthrough Dealer Detail (เฟสถัดไป)
- Visual density:      ปานกลาง — 5 KPI + 5 chart/table บนหน้าเดียว ไม่อัด
- Visual hierarchy:    KPI บนสุด -> trend (ใหญ่สุด) -> breakdown 3 ตัวล่าง
- Color mood:          BYD brand ขาว-แดง (Festival Red #D70C19 / digital #E2231A + Cool Grey #686D71) red-on-white
- Font direction:      Segoe UI / Sans Thai, ตัวเลข tabular-nums
- Interaction strategy: cross-filter + slicer (Year/Region/Model) + drillthrough dealer
- Validation risks:    two-fact grain (Orders vs Targets), Cancelled handling, YoY ช่วงเดียวกัน
```

## Scope (MoSCoW)

- **Must-have:** KPI 5 ตัว, trend vs target, by model, by region, top dealers — ครบใน mockup แล้ว
- **Should-have:** slicer, drillthrough dealer, custom tooltip
- **Could-have:** forecast, filled map ภูมิภาค, anomaly flag, after-sales/service
- **Not-now:** real-time, RLS รายภูมิภาค (รอ API จริง + นโยบายสิทธิ์)

## Open questions (ถามทีม BYD วันเริ่มงาน)

1. API auth แบบไหน (key/Bearer/OAuth2) + pagination + rate limit
2. "ยอดขาย" นับที่ booking หรือ delivery (กระทบนิยาม Units Sold)
3. Target มาจากไหน — grain เดือน×ภูมิภาค พอไหม หรือต้องลงรุ่น/ dealer
4. ผู้บริหารต้องเห็นถึงระดับ dealer/รุ่น หรือแค่ภาพรวมภูมิภาค
5. RLS — แต่ละคนเห็นเฉพาะพื้นที่ตัวเองไหม
