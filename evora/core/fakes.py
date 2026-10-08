"""Deterministic fake data used by every track's mock until the real thing lands. OWNER: P1."""
from __future__ import annotations

from .schemas import Camera, Hit, IndexHandle, PathHop, Track

T0 = 1767258000.0  # 2026-01-01 09:00:00 UTC, fixed so tests/eval agree across machines

FAKE_CAMERAS = [
    Camera("cam01", "Camera 1", "videos/cam01.mp4", T0, 30.0, 1800.0, 1920, 1080),
    Camera("cam02", "Camera 2", "videos/cam02.mp4", T0, 30.0, 1800.0, 1920, 1080),
    Camera("cam03", "Camera 3", "videos/cam03.mp4", T0, 30.0, 1800.0, 1920, 1080),
    Camera("cam04", "Camera 4", "videos/cam04.mp4", T0, 30.0, 1800.0, 1920, 1080),
]

FAKE_TRACKS = [
    Track("cam01_t0001", "cam01", "car", T0 + 840, T0 + 846, best_ts=T0 + 843,
          best_bbox=[600, 400, 1100, 700], colors=["red"]),
    Track("cam01_t0002", "cam01", "person", T0 + 845, T0 + 860, best_ts=T0 + 850,
          best_bbox=[900, 300, 1050, 800], colors=["blue"], attributes=["carrying bag", "large bag"],
          global_id="g0001"),
    Track("cam02_t0007", "cam02", "person", T0 + 960, T0 + 985, best_ts=T0 + 970,
          best_bbox=[500, 250, 650, 750], colors=["blue"], attributes=["carrying bag", "large bag"],
          global_id="g0001"),
    Track("cam04_t0003", "cam04", "person", T0 + 1320, T0 + 1340, best_ts=T0 + 1330,
          best_bbox=[300, 280, 450, 760], colors=["blue"], attributes=["carrying bag", "large bag"],
          global_id="g0001"),
]


def fake_index() -> IndexHandle:
    return IndexHandle(FAKE_CAMERAS, "data/evora.db", "data/index/frames.faiss", "data/index/tracks.faiss")


def track_to_hit(t: Track, score: float, why: str = "") -> Hit:
    return Hit(t.camera_id, t.t_start, t.t_end, score, t.best_frame_path, t.best_bbox,
               t.track_id, None, why)


def fake_path(global_id: str = "g0001") -> list[PathHop]:
    return [PathHop(t.camera_id, t.t_start, t.t_end, t.track_id)
            for t in sorted(FAKE_TRACKS, key=lambda t: t.t_start) if t.global_id == global_id]
