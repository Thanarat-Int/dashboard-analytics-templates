# BYD Overviews

Dashboard ภาพรวมยอดขายรถ BYD (ตลาดไทย) สำหรับผู้บริหาร — **web mockup → guide → Power BI**

สถานะ: ✅ mockup + build spec เสร็จ · ⏳ รอ API จริง · ⏳ ยังไม่ประกอบใน Power BI

## โครงสร้างโฟลเดอร์

```
BYD-Overviews/
├─ 00-brief/        design-decision-log.md   ← objective, scope, design log, open questions
├─ 01-data-raw/
│   └─ mock-api/    generate.py, serve.py, orders.json, targets.json   ← Mock REST API
├─ 02-build-spec/   build-spec.md, theme.json, measures.dax, data-model.md  ← คู่มือประกอบ Power BI
├─ web-mockup/      index.html               ← dashboard ตัวอย่าง (ดึงจาก API จริง)
└─ README.md
```

## วิธีรัน (2 ขั้น)

```powershell
# 1) สตาร์ท mock API
python "01-data-raw/mock-api/serve.py"

# 2) เปิด dashboard ในเบราว์เซอร์
#    http://localhost:8000/web-mockup/
```

Endpoints:
- `http://localhost:8000/api/orders`  — 2,914 orders (envelope: meta + pagination + data)
- `http://localhost:8000/api/targets` — 108 เป้า (เดือน × ภูมิภาค)
- รองรับ `?page=&page_size=` เพื่อซ้อม pagination

## ขั้นต่อไปใน Power BI

1. Get Data → Web → `http://localhost:8000/api/orders` (และ `/targets`)
2. ทำตาม `02-build-spec/data-model.md` (clean + relationship)
3. วาง measures จาก `02-build-spec/measures.dax`
4. Import `02-build-spec/theme.json`
5. ประกอบ visual ตาม `02-build-spec/build-spec.md` (visual-by-visual)
6. รัน QA checklist — ตัวเลขต้องตรง mockup (Units 1,009 / Achievement 96% / YoY +32.9%)

## เปลี่ยนไปใช้ API จริงของ BYD

- web mockup: แก้ค่า `API` ใน `index.html`
- Power BI: แก้ base URL ใน Power Query + เพิ่ม auth header (`Web.Contents(url,[Headers=[Authorization="Bearer ..."]])`)
- โครง model / measure / visual **ไม่ต้องรื้อ** ถ้า field ต้นทางหน้าตาเหมือน mock
