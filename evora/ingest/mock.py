from __future__ import annotations


def cut_clip(camera_id: str, t_start: float, t_end: float) -> str | None:
    return None  # real version writes data/clips/<camera_id>_<t_start>.mp4 via ffmpeg
