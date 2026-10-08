"""Video decoding, frame sampling, thumbnails and clip cutting. OWNER: P1.

Public API:
    cut_clip(camera_id, t_start, t_end) -> str | None   path to an .mp4 clip (padded per config)

Currently backed by mock.py.
"""
from .mock import cut_clip

__all__ = ["cut_clip"]
