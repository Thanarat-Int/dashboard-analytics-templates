# -*- coding: utf-8 -*-
"""
BYD Overviews - Mock API server
จำลอง REST API จาก orders.json / targets.json เพื่อให้ทั้ง web mockup และ Power BI
ดึงข้อมูลจาก endpoint เดียวกัน -> ซ้อม workflow จริงก่อน API ของ BYD จะมา

วิธีรัน:
    python serve.py
แล้วเปิด:
    http://localhost:8000/                      -> web dashboard (mockup)
    http://localhost:8000/api/orders            -> ข้อมูล order (envelope เต็ม)
    http://localhost:8000/api/orders?page=1&page_size=500   -> แบ่งหน้า
    http://localhost:8000/api/targets           -> เป้ารายเดือน/ภูมิภาค

ใน Power BI:  Get Data -> Web -> http://localhost:8000/api/orders
"""
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # โฟลเดอร์ BYD-Overviews
PORT = 8000

with open(os.path.join(HERE, "orders.json"), encoding="utf-8") as f:
    ORDERS = json.load(f)
with open(os.path.join(HERE, "targets.json"), encoding="utf-8") as f:
    TARGETS = json.load(f)


def paginate(envelope, page, page_size):
    data = envelope["data"]
    total = len(data)
    start = (page - 1) * page_size
    chunk = data[start:start + page_size]
    return {
        "meta": envelope["meta"],
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
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

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

        if path == "/api/orders":
            page = int(qs.get("page", [1])[0])
            page_size = int(qs.get("page_size", [len(ORDERS["data"])])[0])
            return self._send_json(paginate(ORDERS, page, page_size))

        if path == "/api/targets":
            return self._send_json(TARGETS)

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
    print(f"BYD Overviews mock API  ->  http://localhost:{PORT}")
    print(f"  dashboard : http://localhost:{PORT}/web-mockup/")
    print(f"  orders    : http://localhost:{PORT}/api/orders")
    print(f"  targets   : http://localhost:{PORT}/api/targets")
    print("  (Ctrl+C เพื่อหยุด)")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
