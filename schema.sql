CREATE TABLE IF NOT EXISTS pilgrims (
    id TEXT PRIMARY KEY,
    full_name TEXT,
    nationality TEXT,
    passport_number TEXT,
    border_number TEXT,
    age INTEGER,
    gender TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    pilgrim_id TEXT PRIMARY KEY,
    lat REAL,
    lng REAL,
    inside_geofence INTEGER,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilgrim_id TEXT,
    lat REAL,
    lng REAL,
    reason TEXT,
    timestamp TEXT
);
