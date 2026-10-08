"""Cross-camera re-identification and path reconstruction. OWNER: P3.

Public API:
    link_all() -> int                      assign tracks.global_id across cameras; returns #identities
    path(track_id) -> list[PathHop]        ordered camera hops for the identity of this track

Currently backed by mock.py.
"""
from .mock import link_all, path

__all__ = ["link_all", "path"]
