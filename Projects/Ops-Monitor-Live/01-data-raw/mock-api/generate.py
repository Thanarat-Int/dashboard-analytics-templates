# -*- coding: utf-8 -*-
"""
Ops-Monitor-Live - Mock API data generator
สร้างข้อมูลจำลองให้หน้าตาเหมือน response จาก observability API จริง
(envelope: meta + pagination + data) สำหรับ archetype 02 Operational Monitor

รันครั้งเดียวเพื่อสร้าง metrics.json และ incidents.json จากนั้นเสิร์ฟด้วย serve.py

ใช้ seed คงที่ -> รันกี่ครั้งก็ได้ข้อมูลชุดเดิม (reproducible)
"""
import json
import random
from datetime import datetime, timedelta

random.seed(2026)  # คงที่เพื่อให้ผลซ้ำได้

# "ตอนนี้" ของโปรเจกต์ (ปัดลงชั่วโมง) -> ใช้เป็นจุดอ้างอิงของ window 24h
NOW = datetime(2026, 6, 14, 12, 0, 0)

# ----- services ที่ monitor -----
SERVICES = ["API Gateway", "Auth Service", "Payment", "Search", "Notification", "DB Primary"]

# ----- 1) metrics: 24 จุดต่อชั่วโมง (last 24h) -----
# โปรไฟล์ throughput รายชั่วโมง (req/min) — ดึก ๆ ต่ำ กลางวันพีค
HOURLY_SHAPE = [
    0.42, 0.36, 0.30, 0.28, 0.30, 0.40, 0.55, 0.74, 0.91, 0.97, 0.94, 0.99,
    1.00, 0.96, 0.93, 0.97, 1.00, 0.99, 0.87, 0.76, 0.66, 0.57, 0.51, 0.45,
]
PEAK_RPM = 7200

metrics = []
for i in range(24):
    ts = NOW - timedelta(hours=23 - i)          # เก่าสุด -> ใหม่สุด
    shape = HOURLY_SHAPE[ts.hour]
    jitter = random.uniform(0.94, 1.06)
    rpm = round(PEAK_RPM * shape * jitter)
    # latency แปรผกผันกับ throughput เล็กน้อย (โหลดสูง -> หน่วงขึ้น)
    load = shape * jitter
    p50 = round(150 + 120 * load + random.uniform(-12, 12))
    p95 = round(p50 * (2.0 + 0.6 * load) + random.uniform(-15, 15))
    err = round(max(0.0, 0.3 + 1.8 * (load ** 2) + random.uniform(-0.25, 0.45)), 2)
    metrics.append({
        "timestamp": ts.isoformat() + "Z",
        "throughput_rpm": rpm,
        "latency_ms_p50": p50,
        "latency_ms_p95": p95,
        "error_rate_pct": err,
    })

# ----- 2) incidents: ~12 records ในช่วง 7 วันล่าสุด -----
SEVERITIES = (["Critical"] * 2) + (["Major"] * 4) + (["Minor"] * 6)
STATUSES = (["Open"] * 3) + (["Ack"] * 3) + (["Resolved"] * 6)
MESSAGES = {
    "Critical": [
        "Latency spike >2s on checkout",
        "Payment provider timeout cascade",
        "DB Primary connection pool exhausted",
    ],
    "Major": [
        "5xx rate above threshold (>2%)",
        "Token refresh queue backlog",
        "Elevated error rate on /search",
        "Cache hit ratio degraded",
    ],
    "Minor": [
        "Index lag 40s",
        "Slow query detected",
        "Disk usage 78% on node-3",
        "Intermittent 429 on Notification",
        "Cert renewal due in 7 days",
        "Memory pressure on worker",
    ],
}

incidents = []
for n in range(12):
    sev = random.choice(SEVERITIES)
    # อายุ incident: 7 วันล่าสุด (นาที)
    age_min = random.randint(4, 7 * 24 * 60)
    opened = NOW - timedelta(minutes=age_min)
    status = random.choice(STATUSES)
    # Critical/Major ที่เพิ่งเปิดมักยัง Open/Ack
    if age_min < 60 and sev in ("Critical", "Major"):
        status = random.choice(["Open", "Ack"])
    incidents.append({
        "id": f"INC-{2026}{(n + 1):04d}",
        "opened_at": opened.isoformat() + "Z",
        "service": random.choice(SERVICES),
        "severity": sev,
        "status": status,
        "message": random.choice(MESSAGES[sev]),
        "age_min": age_min,
    })

# เรียงใหม่สุดขึ้นก่อน (age น้อย = ใหม่)
incidents.sort(key=lambda x: x["age_min"])


def envelope(data, extra_meta=None):
    meta = {
        "source": "mock",
        "domain": "observability",
        "generated_at": NOW.isoformat() + "Z",
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


with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(envelope(metrics, {"entity": "metrics", "grain": "hourly", "window": "24h"}),
              f, ensure_ascii=False, indent=2)

with open("incidents.json", "w", encoding="utf-8") as f:
    json.dump(envelope(incidents, {"entity": "incidents", "window": "7d"}),
              f, ensure_ascii=False, indent=2)

print(f"metrics.json   : {len(metrics)} hourly points")
print(f"incidents.json : {len(incidents)} incidents")
print(f"reference now  : {NOW.isoformat()}Z")
