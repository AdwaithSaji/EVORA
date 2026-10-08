"""Build / load the searchable index (SQLite + FAISS). OWNER: P1.

Public API (keep signatures stable — see evora/core/schemas.py):
    build(manifest_path) -> IndexHandle   decode, detect, track, embed, store
    load() -> IndexHandle                 open an existing index (fast, no GPU)

Currently backed by mock.py. Swap the import below to the real module when ready.
"""
from .mock import build, load

__all__ = ["build", "load"]
