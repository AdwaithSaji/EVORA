"""Our retriever: structured filters + track/frame search + verification + event merging. OWNER: P2.

Public API:
    search(spec: QuerySpec, k=5, options: dict | None = None) -> list[Hit]

`options` carries ablation toggles, all default True:
    use_filters, use_tracks, use_frames, use_verify, use_merge

Currently backed by mock.py.
"""
from .mock import search

__all__ = ["search"]
