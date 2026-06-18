# -*- coding: utf-8 -*-
"""
Ops-Monitor-Live - Mock API server
จำลอง REST API จาก metrics.json / incidents.json เพื่อให้ทั้ง web mockup และ Power BI
ดึงข้อมูลจาก endpoint เดียวกัน -> ซ้อม workflow จริงก่อน observability API จะมา

วิธีรัน:
    python serve.py
แล้วเปิด:
    http://localhost:8010/Projects/Ops-Monitor-Live/web/   -> web dashboard (mockup)
    http://localhost:8010/api/metrics                 -> 24 จุดรายชั่วโมง (envelope เต็ม)
    http://localhost:8010/api/metrics?page=1&page_size=12  -> แบ่งหน้า
    http://localhost:8010/api/incidents               -> incident records (7d)

ใน Power BI:  Get Data -> Web -> http://localhost:8010/api/metrics
"""
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))      # โฟลเดอร์ Ops-Monitor-Live
# เสิร์ฟจาก root DEEPBI เพื่อให้หน้าเว็บเข้าถึง _design-system/ (อยู่นอกโฟลเดอร์โปรเจกต์) ได้ผ่าน HTTP
# หน้าเว็บอยู่ที่ /Projects/Ops-Monitor-Live/web/  -> ../../../_design-system/ resolve เป็น /_design-system/
SERVE_ROOT = os.path.abspath(os.path.join(PROJECT_DIR, "..", ".."))  # root DEEPBI
WEB_PATH = "/Projects/Ops-Monitor-Live/web/"
PORT = 8010

with open(os.path.join(HERE, "metrics.json"), encoding="utf-8") as f:
    METRICS = json.load(f)
with open(os.path.join(HERE, "incidents.json"), encoding="utf-8") as f:
    INCIDENTS = json.load(f)


def paginate(env, page, page_size):
    data = env["data"]
    total = len(data)
    start = (page - 1) * page_size
    chunk = data[start:start + page_size]
    return {
        "meta": env["meta"],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
        "data": chunk,
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_ROOT, **kwargs)

    def _send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")  # ให้ file:// / Power BI ยิงได้
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        qs = parse_qs(parsed.query)

        if path == "/api/metrics":
            page = int(qs.get("page", [1])[0])
            page_size = int(qs.get("page_size", [len(METRICS["data"])])[0])
            return self._send_json(paginate(METRICS, page, page_size))

        if path == "/api/incidents":
            return self._send_json(INCIDENTS)

        # อื่น ๆ -> เสิร์ฟไฟล์ static (web mockup) จาก root โปรเจกต์
        return super().do_GET()

    def end_headers(self):
        # static file ก็ใส่ CORS ด้วย
        if not self.path.startswith("/api/"):
            self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("  ", fmt % args)


if __name__ == "__main__":
    print(f"Ops-Monitor-Live mock API  ->  http://localhost:{PORT}")
    print(f"  dashboard : http://localhost:{PORT}{WEB_PATH}")
    print(f"  metrics   : http://localhost:{PORT}/api/metrics")
    print(f"  incidents : http://localhost:{PORT}/api/incidents")
    print("  (Ctrl+C เพื่อหยุด)")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
