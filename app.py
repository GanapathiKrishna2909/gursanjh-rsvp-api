"""Flask API for Gursanjh's 1st Birthday RSVP — Render-compatible."""
import json
import time
import os
import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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


@app.route("/api/stats", methods=["GET"])
def get_stats():
    data = read_bin()
    rsvps = data.get("rsvps", [])
    yes_rsvps = [r for r in rsvps if r.get("attending") == "yes"]
    return jsonify({
        "total_guests": sum(r.get("num_adults", 0) + r.get("num_kids", 0) for r in yes_rsvps),
        "total_families": len(yes_rsvps),
    })


@app.route("/api/rsvps", methods=["GET"])
def get_rsvps():
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "unauthorized", "rsvps": []})

    data = read_bin()
    rsvps = data.get("rsvps", [])
    yes_rsvps = [r for r in rsvps if r.get("attending") == "yes"]
    return jsonify({
        "rsvps": sorted(rsvps, key=lambda r: r.get("created_at", ""), reverse=True),
        "total_adults": sum(r.get("num_adults", 0) for r in yes_rsvps),
        "total_kids": sum(r.get("num_kids", 0) for r in yes_rsvps),
        "total_guests": sum(r.get("num_adults", 0) + r.get("num_kids", 0) for r in yes_rsvps),
        "total_responses": len(rsvps),
    })


@app.route("/api/rsvp", methods=["POST"])
def create_rsvp():
    body = request.get_json(force=True, silent=True) or {}

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

    return jsonify({"id": new_rsvp["id"], "status": "success"}), 201


@app.route("/api/rsvp/<int:rsvp_id>", methods=["DELETE"])
def delete_rsvp(rsvp_id):
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "unauthorized"})

    data = read_bin()
    data["rsvps"] = [r for r in data.get("rsvps", []) if r.get("id") != rsvp_id]
    write_bin(data)
    return jsonify({"deleted": rsvp_id})


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "gursanjh-rsvp-api"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
