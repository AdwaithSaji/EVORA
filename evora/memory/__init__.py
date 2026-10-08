"""Clarify-once knowledge base (data/memory.db, separate from the index). OWNER: P4.

Public API:
    Memory(path=config.MEMORY_DB)
        .resolve(alias) -> Location | None
        .learn(alias, camera_id, polygon=None, utterance="") -> Location
        .forget(alias) -> None
        .all() -> list[Location]
    normalize_alias(text) -> str

Rules: resolve() is ALWAYS checked before asking; learn() commits immediately so the fact
survives a restart. Currently backed by mock.py (in-memory, NOT persistent yet).
"""
from .mock import Memory, normalize_alias

__all__ = ["Memory", "normalize_alias"]
