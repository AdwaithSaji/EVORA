"""SQLite schema for the video index (data/evora.db). OWNER: P1.

The memory DB (data/memory.db) is separate and owned by P4 in evora/memory/.
FAISS rows map to SQLite rows via config.FRAMES_IDS / config.TRACKS_IDS.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import config
from .schemas import Camera, Track

SCHEMA = """
CREATE TABLE IF NOT EXISTS cameras (
    camera_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    video_path TEXT NOT NULL,
    start_wallclock REAL NOT NULL,
    fps REAL, duration REAL, width INTEGER, height INTEGER,
    thumbnail_path TEXT
);
CREATE TABLE IF NOT EXISTS frames (
    frame_id INTEGER PRIMARY KEY,
    camera_id TEXT NOT NULL REFERENCES cameras(camera_id),
    ts REAL NOT NULL,
    frame_path TEXT NOT NULL,
    emb_id INTEGER
);
CREATE INDEX IF NOT EXISTS idx_frames_cam_ts ON frames(camera_id, ts);
CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    camera_id TEXT NOT NULL REFERENCES cameras(camera_id),
    label TEXT NOT NULL,
    t_start REAL NOT NULL,
    t_end REAL NOT NULL,
    best_crop_path TEXT,
    best_frame_path TEXT,
    best_ts REAL,
    best_bbox TEXT,        -- JSON [x1,y1,x2,y2]
    colors TEXT,           -- JSON list
    attributes TEXT,       -- JSON list
    emb_id INTEGER,
    global_id TEXT         -- written by P3 re-ID
);
CREATE INDEX IF NOT EXISTS idx_tracks_cam_t ON tracks(camera_id, t_start, t_end);
CREATE INDEX IF NOT EXISTS idx_tracks_global ON tracks(global_id);
CREATE TABLE IF NOT EXISTS detections (
    det_id INTEGER PRIMARY KEY,
    track_id TEXT REFERENCES tracks(track_id),
    camera_id TEXT NOT NULL,
    ts REAL NOT NULL,
    x1 REAL, y1 REAL, x2 REAL, y2 REAL,
    label TEXT, score REAL
);
CREATE INDEX IF NOT EXISTS idx_det_track ON detections(track_id, ts);
"""


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(path or config.EVORA_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_camera(conn: sqlite3.Connection, c: Camera) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO cameras VALUES (?,?,?,?,?,?,?,?,?)",
        (c.camera_id, c.name, c.video_path, c.start_wallclock, c.fps, c.duration,
         c.width, c.height, c.thumbnail_path),
    )


def load_cameras(conn: sqlite3.Connection) -> list[Camera]:
    return [Camera(**dict(r)) for r in conn.execute("SELECT * FROM cameras ORDER BY camera_id")]


def upsert_track(conn: sqlite3.Connection, t: Track) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO tracks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (t.track_id, t.camera_id, t.label, t.t_start, t.t_end, t.best_crop_path,
         t.best_frame_path, t.best_ts, json.dumps(t.best_bbox), json.dumps(t.colors),
         json.dumps(t.attributes), t.emb_id, t.global_id),
    )


def row_to_track(r: sqlite3.Row) -> Track:
    d = dict(r)
    for k in ("best_bbox", "colors", "attributes"):
        d[k] = json.loads(d[k]) if d[k] else ([] if k != "best_bbox" else None)
    return Track(**d)


def get_track(conn: sqlite3.Connection, track_id: str) -> Track | None:
    r = conn.execute("SELECT * FROM tracks WHERE track_id=?", (track_id,)).fetchone()
    return row_to_track(r) if r else None
