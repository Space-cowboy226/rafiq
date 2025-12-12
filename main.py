from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os
import sqlite3
import math
from datetime import datetime

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"]
)

   # Allow requests from frontend

DB = "rafiq.db"

# ============================
# JSON-BASED PILGRIM VERIFY + LOGS (your old part)
# ============================

def load_data():
    with open("pilgrims.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_log(entry):
    logs = []
    if os.path.exists("logs.json"):
        with open("logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append(entry)
    with open("logs.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

@app.route("/verify")
def verify():
    pid = request.args.get("id")

    # 1️⃣ Check the SQLite pilgrims table first
    db_rows = query("SELECT * FROM pilgrims WHERE id = ?", (pid,))
    if db_rows:
        pilgrim = db_rows[0]  # row as dict

        save_log({
            "id": pid,
            "result": "OK (DB)",
            "location": "N/A",
            "time": datetime.utcnow().isoformat()
        })

        return jsonify({
            "found": True,
            "data": {
                "name": pilgrim["full_name"],
                "nationality": pilgrim["nationality"],
                "housing": "غير مسجل",
                "campaign": "غير مسجل",
                "status": "OK"
            }
        })

    # 2️⃣ Fallback to JSON file (your original behavior)
    data = load_data()
    if pid in data:
        save_log({
            "id": pid,
            "result": "OK (JSON)",
            "location": "N/A",
            "time": datetime.utcnow().isoformat()
        })
        return jsonify({"found": True, "data": data[pid]})

    # 3️⃣ Not found anywhere
    return jsonify({"found": False}), 404


@app.route("/logs")
def get_logs():
    if os.path.exists("logs.json"):
        with open("logs.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify([])


@app.route("/")
def home():
    return "Rafiq Backend API is running on PythonAnywhere 🚀"


# ============================
# DB HELPERS (SQLite)
# ============================

def query(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def execute(sql, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


# ============================
# LIVE TRACKING + GEOFENCE
# ============================

# Geofence Setup (Mina-ish example)
GEOFENCE_CENTER = (21.4167, 39.9000)  # lat, lng
GEOFENCE_RADIUS_METERS = 700          # allowed movement radius

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000  # Earth radius in meters

    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def inside_geofence(lat, lng):
    distance = haversine(lat, lng, GEOFENCE_CENTER[0], GEOFENCE_CENTER[1])
    return distance <= GEOFENCE_RADIUS_METERS


# ============================================================
# 1️⃣  IoT-style Location Update (DB-backed)
#     POST /api/update-location
# ============================================================
@app.route("/api/update-location", methods=["POST"])
def update_location():
    data = request.get_json()

    pid = data.get("id")
    lat = data.get("lat")
    lng = data.get("lng")

    if not pid or lat is None or lng is None:
        return jsonify({"error": "Missing id/lat/lng"}), 400

    lat = float(lat)
    lng = float(lng)

    inside = inside_geofence(lat, lng)
    ts = datetime.utcnow().isoformat()

    # Upsert latest location into DB
    execute("""
        INSERT INTO locations (pilgrim_id, lat, lng, inside_geofence, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(pilgrim_id)
        DO UPDATE SET
          lat = excluded.lat,
          lng = excluded.lng,
          inside_geofence = excluded.inside_geofence,
          timestamp = excluded.timestamp
    """, (pid, lat, lng, 1 if inside else 0, ts))

    # If outside geofence, add alert row
    if not inside:
        execute("""
            INSERT INTO alerts (pilgrim_id, lat, lng, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (pid, lat, lng, "OUT_OF_GEOFENCE", ts))

    # 🔁 keep same response shape you had before
    return jsonify({
        "ok": True,
        "inside_geofence": inside
    })


# ============================================================
# 2️⃣  Get all latest locations (from DB)
#     GET /api/locations
# ============================================================
@app.route("/api/locations")
def get_locations():
    rows = query("""
        SELECT pilgrim_id AS id, lat, lng, inside_geofence, timestamp
        FROM locations
    """)
    # Convert inside_geofence from 0/1 to bool
    for r in rows:
        r["inside_geofence"] = bool(r["inside_geofence"])
    return jsonify(rows)


# ============================================================
# 3️⃣  Get alerts (latest 30, from DB)
#     GET /api/alerts
# ============================================================
@app.route("/api/alerts")
def get_alerts():
    rows = query("""
        SELECT pilgrim_id AS id, lat, lng, reason, timestamp
        FROM alerts
        ORDER BY timestamp DESC
        LIMIT 30
    """)
    return jsonify(rows)


# ============================
# Local run (ignored on PythonAnywhere WSGI)
# ============================
if __name__ == "__main__":
    app.run(debug=True)
