# DEEPBI Project Instructions

Use `/senior-bi-analytics-th` for all Power BI, DAX, Power Query, data modeling, dashboard visualization design, QA, and presentation tasks.

Default response language: Thai.
Keep DAX, table names, column names, and measure names in English unless asked otherwise.

## Web dashboard design system

ทุกงาน dashboard ทำเป็น web mockup (พิมพ์เขียว) ก่อน แล้วค่อยประกอบใน Power BI โดย:
- ใช้ `_design-system/` (tokens.css + components.css + charts.js + skins/skins.css) เป็นรากฐาน — อย่าเขียน CSS ใหม่จากศูนย์
- ทุก dashboard = **Archetype × Skin × Data** ; archetype ต้นแบบอยู่ที่ `_templates/` (01 executive, 02 operational, 03 financial, 04 funnel) ; 5 skins: byd-red, finance-dark, saas-violet, luxury-gold, command-center
- วิธีสร้างใหม่ + กับดัก (reserved globals: `status`/`top`/`name` ฯลฯ ห้ามตั้งเป็นชื่อตัวแปร) อยู่ใน `_design-system/README.md`
- เปิด preview ผ่าน **`python serve.py` ที่ root** (DEV HUB พอร์ต 8000 เดียว — เสิร์ฟ static ทั้ง repo + รวม mock API ทุก project ที่ `/api/<entity>`) ไม่ใช่ double-click ; หน้าที่ดึง API ใช้ base แบบ relative `/api`
- ทุก visual บน web ต้อง map กับ Power BI native visual ได้ ; ส่งมอบพร้อม `theme.json` + `build-spec.md` (ตัวอย่าง: `Projects/BYD-Overviews/02-build-spec/`)