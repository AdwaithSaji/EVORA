"""Standing queries / real-time alerts ("notify me if anyone enters this zone after 8pm"). OWNER: P3.

Public API:
    register(spec: QuerySpec, name: str) -> str     store a standing query, returns its id
    check_track(track: Track) -> list[str]           ids of standing queries this new track triggers
    list_all() -> list[dict]

Currently backed by mock.py.
"""
from .mock import check_track, list_all, register

__all__ = ["register", "check_track", "list_all"]
