"""Vercel Serverless Function — RSVP API for Gursanjh's 1st Birthday."""
import json
import time
import httpx
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

JSONBIN_URL = "https://jsonbin-zeta.vercel.app/api/bins/kxDvOOBaFD"
ADMIN_PASSWORD = "gursanjh2026"


def read_bin():
    try:
        r = httpx.get(JSONBIN_URL, timeout=10)
        return r.json()
    except Exception:
        return {"rsvps": [], "admin_password": ADMIN_PASSWORD}


def write_bin(data):
    try:
        httpx.put(JSONBIN_URL, json=data, timeout=10)
        return True
    except Exception:
        return False


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in cors_headers().items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = parsed.path.rstrip("/")

        if path == "/api/stats":
            data = read_bin()
            rsvps = data.get("rsvps", [])
            yes_rsvps = [r for r in rsvps if r.get("attending") == "yes"]
            result = {
                "total_guests": sum(r.get("num_adults", 0) + r.get("num_kids", 0) for r in yes_rsvps),
                "total_families": len(yes_rsvps),
            }
            self._respond(200, result)

        elif path == "/api/rsvps":
            password = params.get("password", [""])[0]
            if password != ADMIN_PASSWORD:
                self._respond(200, {"error": "unauthorized", "rsvps": []})
                return

            data = read_bin()
            rsvps = data.get("rsvps", [])
            yes_rsvps = [r for r in rsvps if r.get("attending") == "yes"]
            result = {
                "rsvps": sorted(rsvps, key=lambda r: r.get("created_at", ""), reverse=True),
                "total_adults": sum(r.get("num_adults", 0) for r in yes_rsvps),
                "total_kids": sum(r.get("num_kids", 0) for r in yes_rsvps),
                "total_guests": sum(r.get("num_adults", 0) + r.get("num_kids", 0) for r in yes_rsvps),
                "total_responses": len(rsvps),
            }
            self._respond(200, result)
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/rsvp":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length else {}

            data = read_bin()
            rsvps = data.get("rsvps", [])
            max_id = max((r.get("id", 0) for r in rsvps), default=0)

            new_rsvp = {
                "id": max_id + 1,
                "guest_name": body.get("guest_name", ""),
                "num_adults": body.get("num_adults", 1),
                "num_kids": body.get("num_kids", 0),
                "message": body.get("message", ""),
                "attending": body.get("attending", "yes"),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            rsvps.append(new_rsvp)
            data["rsvps"] = rsvps
            write_bin(data)

            self._respond(201, {"id": new_rsvp["id"], "status": "success"})
        else:
            self._respond(404, {"error": "not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = parsed.path.rstrip("/")

        # Extract rsvp_id from path like /api/rsvp/5
        parts = path.split("/")
        if len(parts) >= 4 and parts[1] == "api" and parts[2] == "rsvp":
            rsvp_id = int(parts[3])
            password = params.get("password", [""])[0]

            if password != ADMIN_PASSWORD:
                self._respond(200, {"error": "unauthorized"})
                return

            data = read_bin()
            data["rsvps"] = [r for r in data.get("rsvps", []) if r.get("id") != rsvp_id]
            write_bin(data)
            self._respond(200, {"deleted": rsvp_id})
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, status, body):
        self.send_response(status)
        for k, v in cors_headers().items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
