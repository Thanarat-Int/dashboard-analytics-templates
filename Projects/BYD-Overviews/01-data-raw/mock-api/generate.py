# -*- coding: utf-8 -*-
"""
BYD Overviews - Mock API data generator
สร้างข้อมูลจำลองให้หน้าตาเหมือน response จาก API จริง (มี envelope: meta + pagination + data)
รันครั้งเดียวเพื่อสร้าง orders.json และ targets.json จากนั้นเสิร์ฟด้วย serve.py

ใช้ seed คงที่ -> รันกี่ครั้งก็ได้ข้อมูลชุดเดิม (reproducible)
"""
import json
import random
from datetime import date, timedelta

random.seed(2026)  # คงที่เพื่อให้ผลซ้ำได้

# ----- พารามิเตอร์ช่วงเวลา -----
START = date(2025, 1, 1)
END = date(2026, 6, 8)   # ตรงกับ "วันนี้" ของโปรเจกต์

# ----- รุ่นรถ BYD + ช่วงราคา (THB) + segment -----
MODELS = [
    # model,      segment,  price_min, price_max, น้ำหนักความนิยม
    ("Dolphin",   "B-Hatch", 569900,   699900,   22),
    ("Atto 3",    "C-SUV",   899900,  1099900,   20),
    ("Seal",      "D-Sedan", 1199900, 1599900,   16),
    ("Seal U",    "C-SUV",   1099000, 1299000,   12),
    ("Sealion 6", "C-SUV",   1099000, 1249000,   10),
    ("M6",        "MPV",      829900,  949900,    10),
    ("Han",       "E-Sedan", 1899900, 1899900,     5),
    ("Tang",      "E-SUV",   1899900, 1899900,     5),
]
MODEL_WEIGHTS = [m[4] for m in MODELS]

# ----- ภูมิภาค + จังหวัด -----
REGIONS = {
    "Central":   ["Bangkok", "Nonthaburi", "Pathum Thani", "Samut Prakan"],
    "East":      ["Chonburi", "Rayong"],
    "North":     ["Chiang Mai", "Chiang Rai", "Phitsanulok"],
    "Northeast": ["Khon Kaen", "Nakhon Ratchasima", "Udon Thani"],
    "South":     ["Phuket", "Surat Thani", "Songkhla"],
    "West":      ["Nakhon Pathom", "Ratchaburi"],
}
REGION_WEIGHTS = {"Central": 38, "East": 18, "North": 13, "Northeast": 14, "South": 11, "West": 6}

# ----- dealers -----
DEALERS = [
    ("D01", "BYD Rama III",   "Central",   "Bangkok"),
    ("D02", "BYD Bangna",     "Central",   "Samut Prakan"),
    ("D03", "BYD Ratchayothin","Central",  "Bangkok"),
    ("D04", "BYD Nonthaburi", "Central",   "Nonthaburi"),
    ("D05", "BYD Pattaya",    "East",      "Chonburi"),
    ("D06", "BYD Rayong",     "East",      "Rayong"),
    ("D07", "BYD Chiang Mai", "North",     "Chiang Mai"),
    ("D08", "BYD Phitsanulok","North",     "Phitsanulok"),
    ("D09", "BYD Khon Kaen",  "Northeast", "Khon Kaen"),
    ("D10", "BYD Korat",      "Northeast", "Nakhon Ratchasima"),
    ("D11", "BYD Phuket",     "South",     "Phuket"),
    ("D12", "BYD Hatyai",     "South",     "Songkhla"),
    ("D13", "BYD Nakhon Pathom","West",    "Nakhon Pathom"),
]
DEALER_BY_REGION = {}
for d in DEALERS:
    DEALER_BY_REGION.setdefault(d[2], []).append(d)

CHANNELS = (["Showroom"] * 6) + (["Online"] * 2) + (["Fleet/Corporate"] * 2)
CUSTOMER_TYPES = (["Individual"] * 8) + (["Corporate/Fleet"] * 2)
# สถานะ: ส่วนใหญ่ส่งมอบแล้ว, บางส่วนจองอยู่, ส่วนน้อยยกเลิก
STATUS_POOL = (["Delivered"] * 78) + (["Booked"] * 16) + (["Cancelled"] * 6)


def daterange_months(start, end):
    y, m = start.year, start.month
    while (y < end.year) or (y == end.year and m <= end.month):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def monthly_volume(y, m):
    """จำนวน order ต่อเดือน: มี trend โตขึ้น + ฤดูกาล (ปลายไตรมาส/ปลายปีพีค)"""
    idx = (y - 2025) * 12 + (m - 1)          # 0,1,2,...
    base = 110 + idx * 6                       # trend โตเดือนละ ~6 คัน
    seasonal = {3: 1.18, 6: 1.22, 9: 1.15, 12: 1.30}.get(m, 1.0)  # ปลายไตรมาส
    return int(base * seasonal)


def pick_region():
    regions = list(REGION_WEIGHTS.keys())
    weights = list(REGION_WEIGHTS.values())
    return random.choices(regions, weights=weights, k=1)[0]


orders = []
order_no = 0
for y, m in daterange_months(START, END):
    vol = monthly_volume(y, m)
    # เดือนสุดท้าย (มิ.ย. 2026) ยังไม่จบเดือน -> ลดปริมาณตามสัดส่วนวันที่ผ่าน
    if y == END.year and m == END.month:
        vol = int(vol * (END.day / 30.0))
    for _ in range(vol):
        order_no += 1
        # วันสั่งซื้อภายในเดือน
        if y == END.year and m == END.month:
            day = random.randint(1, END.day)
        else:
            # หาวันสุดท้ายของเดือน
            nxt = date(y + (m // 12), (m % 12) + 1, 1)
            last = (nxt - timedelta(days=1)).day
            day = random.randint(1, last)
        order_date = date(y, m, day)

        model, segment, pmin, pmax, _w = random.choices(MODELS, weights=MODEL_WEIGHTS, k=1)[0]
        unit_price = random.randrange(pmin, pmax + 1, 100) if pmax > pmin else pmin

        region = pick_region()
        province = random.choice(REGIONS[region])
        dealer = random.choice(DEALER_BY_REGION[region])
        channel = random.choice(CHANNELS)
        cust = random.choice(CUSTOMER_TYPES)
        status = random.choice(STATUS_POOL)

        # delivery_date: เฉพาะที่ส่งมอบแล้ว
        delivery_date = None
        if status == "Delivered":
            dd = order_date + timedelta(days=random.randint(10, 45))
            if dd <= END:
                delivery_date = dd.isoformat()
            else:
                status = "Booked"  # ยังส่งไม่ทัน -> ถือว่ายังจอง

        revenue = unit_price if status != "Cancelled" else 0

        orders.append({
            "order_id": f"BYD-{y}-{order_no:06d}",
            "order_date": order_date.isoformat(),
            "delivery_date": delivery_date,
            "model": model,
            "segment": segment,
            "region": region,
            "province": province,
            "dealer_id": dealer[0],
            "dealer_name": dealer[1],
            "channel": channel,
            "customer_type": cust,
            "status": status,
            "unit_price": unit_price,
            "quantity": 1,
            "revenue": revenue,
            "salesperson_id": f"SP{random.randint(1, 60):03d}",
        })

# ----- targets: เป้าต่อเดือนต่อภูมิภาค (อิงยอดจริง + buffer) -----
# รวมยอด delivered/booked จริงต่อเดือน/ภูมิภาค แล้วตั้งเป้าให้ใกล้ ๆ (ท้าทายเล็กน้อย)
agg = {}
for o in orders:
    if o["status"] == "Cancelled":
        continue
    ym = o["order_date"][:7]
    key = (ym, o["region"])
    a = agg.setdefault(key, {"units": 0, "rev": 0})
    a["units"] += 1
    a["rev"] += o["revenue"]

targets = []
for (ym, region), a in sorted(agg.items()):
    # เป้า = ยอดจริง * ตัวคูณคงที่ตามภูมิภาค (บางที่ตั้งสูงไป บางที่ทำได้เกิน)
    factor = {"Central": 1.05, "East": 0.98, "North": 1.10,
              "Northeast": 1.02, "South": 1.08, "West": 0.95}[region]
    targets.append({
        "month": ym,
        "region": region,
        "target_units": round(a["units"] * factor),
        "target_revenue": round(a["rev"] * factor / 1000) * 1000,
    })


def envelope(data, extra_meta=None):
    meta = {
        "source": "mock",
        "market": "Thailand",
        "currency": "THB",
        "generated_at": END.isoformat(),
        "version": "1.0",
    }
    if extra_meta:
        meta.update(extra_meta)
    return {
        "meta": meta,
        "pagination": {
            "page": 1,
            "page_size": len(data),
            "total_records": len(data),
            "total_pages": 1,
        },
        "data": data,
    }


with open("orders.json", "w", encoding="utf-8") as f:
    json.dump(envelope(orders, {"entity": "orders"}), f, ensure_ascii=False, indent=2)

with open("targets.json", "w", encoding="utf-8") as f:
    json.dump(envelope(targets, {"entity": "targets", "grain": "month x region"}), f,
              ensure_ascii=False, indent=2)

print(f"orders.json  : {len(orders)} records")
print(f"targets.json : {len(targets)} records")
print(f"period       : {START} -> {END}")
