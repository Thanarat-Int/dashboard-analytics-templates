# -*- coding: utf-8 -*-
"""
DeepBI DEV HUB — server เดียวเห็นทุกอย่าง
- เสิร์ฟ static ทั้ง repo (gallery, ทุก archetype, design-system, ทุก project)
- รวม mock API ของทุก project ไว้ในพอร์ตเดียว (route /api/<entity>)
- CORS + pagination

รัน:  python serve.py        (ที่ root DEEPBI)
เปิด: http://localhost:8000/                 -> หน้า hub (เมนูรวม)
      http://localhost:8000/_templates/      -> gallery 8 archetypes
      http://localhost:8000/Projects/BYD-Overviews/web-mockup/   -> BYD (ดึง /api/orders)
      http://localhost:8000/Projects/Ops-Monitor-Live/web/       -> Ops (ดึง /api/metrics)

API (flat namespace — ชื่อ entity ไม่ชนกัน):
      /api/orders  /api/targets        (BYD)
      /api/metrics /api/incidents      (Ops)
"""
import json
import os
import re
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8000

# entity -> ไฟล์ JSON (envelope: meta+pagination+data)
SOURCES = {
    "orders":    "Projects/BYD-Overviews/01-data-raw/mock-api/orders.json",
    "targets":   "Projects/BYD-Overviews/01-data-raw/mock-api/targets.json",
    "metrics":   "Projects/Ops-Monitor-Live/01-data-raw/mock-api/metrics.json",
    "incidents": "Projects/Ops-Monitor-Live/01-data-raw/mock-api/incidents.json",
}

API = {}
for name, rel in SOURCES.items():
    path = os.path.join(ROOT, rel)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            API[name] = json.load(f)
    else:
        print(f"  ! ข้าม /api/{name} — ไม่พบไฟล์ {rel} (รัน generate.py ของ project นั้นก่อน)")


def paginate(env, page, size):
    data = env.get("data", [])
    total = len(data)
    start = (page - 1) * size
    return {
        "meta": env.get("meta", {}),
        "pagination": {"page": page, "page_size": size, "total_records": total,
                       "total_pages": (total + size - 1) // size if size else 1},
        "data": data[start:start + size],
    }


IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif")


def _load_json(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (ValueError, OSError):
            return {}
    return {}


def moodboard_list():
    """สแกน _moodboard/img/ -> รายการรูป + meta (title/tags/category/starred/order)
    meta.json = ตัวหลัก (เขียนผ่าน /api/moodboard/meta) ; captions.json = fallback ของ title/tags"""
    base = os.path.join(ROOT, "_moodboard")
    img_dir = os.path.join(base, "img")
    caps = _load_json(os.path.join(base, "captions.json"))
    meta = _load_json(os.path.join(base, "meta.json"))
    items = []
    if os.path.isdir(img_dir):
        for fn in os.listdir(img_dir):
            if not fn.lower().endswith(IMG_EXT):
                continue
            m = meta.get(fn, {})
            c = caps.get(fn, {})
            title = m.get("title") or c.get("title") or \
                os.path.splitext(fn)[0].replace("-", " ").replace("_", " · ")
            items.append({
                "file": fn,
                "url": "/_moodboard/img/" + fn,
                "title": title,
                "tags": m.get("tags") or c.get("tags") or [],
                "category": m.get("category", ""),
                "starred": bool(m.get("starred", False)),
                "order": m.get("order"),
            })

    def sort_key(it):
        o = it.get("order")
        return (0, o) if isinstance(o, (int, float)) else (1, it["file"])
    items.sort(key=sort_key)
    return {"meta": {"source": "moodboard"},
            "pagination": {"total_records": len(items)},
            "data": items}


def safe_img_name(raw):
    """sanitize ชื่อไฟล์: basename + อักขระปลอดภัย + ต้องเป็นนามสกุลรูปเท่านั้น (กัน path traversal)"""
    raw = os.path.basename((raw or "").replace("\\", "/"))
    raw = re.sub(r"[^A-Za-z0-9._-]", "-", raw).strip("-.")
    root, ext = os.path.splitext(raw)
    if ext.lower() not in IMG_EXT:
        return None
    return (root[:80] or "image") + ext.lower()


def dedupe_name(img_dir, name):
    if not os.path.exists(os.path.join(img_dir, name)):
        return name
    root, ext = os.path.splitext(name)
    i = 1
    while os.path.exists(os.path.join(img_dir, "%s-%d%s" % (root, i, ext))):
        i += 1
    return "%s-%d%s" % (root, i, ext)


class DualStackServer(ThreadingHTTPServer):
    """ฟังทั้ง IPv4 + IPv6 (localhost บนเครื่องนี้ resolve เป็น ::1) + ไม่ค้างเมื่อมีหลาย request พร้อมกัน"""
    address_family = socket.AF_INET6
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        super().server_bind()


class Hub(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def _json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            entity = parsed.path[len("/api/"):].strip("/")
            if entity == "moodboard":
                return self._json(moodboard_list())
            if entity not in API:
                return self._json({"error": f"unknown entity '{entity}'",
                                   "available": list(API.keys())}, 404)
            qs = parse_qs(parsed.query)
            env = API[entity]
            if "page" in qs or "page_size" in qs:
                page = int(qs.get("page", [1])[0])
                size = int(qs.get("page_size", [len(env.get("data", []))])[0])
                return self._json(paginate(env, page, size))
            return self._json(env)
        return super().do_GET()  # static

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/moodboard/upload":
            qs = parse_qs(parsed.query)
            name = safe_img_name(qs.get("name", ["image.png"])[0])
            if not name:
                return self._json({"ok": False, "error": "ชื่อไฟล์ไม่ถูกต้อง หรือไม่ใช่ไฟล์รูป"}, 400)
            length = int(self.headers.get("Content-Length", 0) or 0)
            if length <= 0 or length > 25 * 1024 * 1024:
                return self._json({"ok": False, "error": "ไฟล์ว่าง หรือใหญ่เกิน 25MB"}, 400)
            data = self.rfile.read(length)
            img_dir = os.path.join(ROOT, "_moodboard", "img")
            os.makedirs(img_dir, exist_ok=True)
            name = dedupe_name(img_dir, name)
            with open(os.path.join(img_dir, name), "wb") as fh:
                fh.write(data)
            return self._json({"ok": True, "file": name, "url": "/_moodboard/img/" + name})

        if parsed.path == "/api/moodboard/delete":
            length = int(self.headers.get("Content-Length", 0) or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                payload = {}
            base = os.path.join(ROOT, "_moodboard")
            img_dir = os.path.join(base, "img")
            meta = _load_json(os.path.join(base, "meta.json"))
            deleted = 0
            for raw in (payload.get("files") or []):
                nm = safe_img_name(raw)
                if not nm:
                    continue
                p = os.path.join(img_dir, nm)
                if os.path.isfile(p):
                    try:
                        os.remove(p)
                        meta.pop(nm, None)
                        deleted += 1
                    except OSError:
                        pass
            with open(os.path.join(base, "meta.json"), "w", encoding="utf-8") as fh:
                json.dump(meta, fh, ensure_ascii=False, indent=2)
            return self._json({"ok": True, "deleted": deleted})

        if parsed.path == "/api/moodboard/meta":
            length = int(self.headers.get("Content-Length", 0) or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                payload = {}
            patch = payload.get("meta") or {}
            base = os.path.join(ROOT, "_moodboard")
            cur = _load_json(os.path.join(base, "meta.json"))
            n = 0
            for fn, fields in patch.items():
                nm = safe_img_name(fn)
                if not nm or not isinstance(fields, dict):
                    continue
                cur.setdefault(nm, {})
                cur[nm].update(fields)
                n += 1
            os.makedirs(base, exist_ok=True)
            with open(os.path.join(base, "meta.json"), "w", encoding="utf-8") as fh:
                json.dump(cur, fh, ensure_ascii=False, indent=2)
            return self._json({"ok": True, "updated": n})

        return self._json({"error": "not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *a):
        print("  ", fmt % a)


if __name__ == "__main__":
    print(f"DeepBI DEV HUB  ->  http://localhost:{PORT}")
    print(f"  hub menu  : http://localhost:{PORT}/")
    print(f"  gallery   : http://localhost:{PORT}/_templates/")
    print(f"  BYD       : http://localhost:{PORT}/Projects/BYD-Overviews/web-mockup/")
    print(f"  Ops       : http://localhost:{PORT}/Projects/Ops-Monitor-Live/web/")
    print(f"  API ready : {', '.join('/api/'+k for k in API)}")
    print("  (Ctrl+C เพื่อหยุด)")
    DualStackServer(("::", PORT), Hub).serve_forever()
