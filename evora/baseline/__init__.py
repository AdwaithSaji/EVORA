"""Baseline: frame-level SigLIP embeddings + FAISS top-k on the raw query text. OWNER: P2.

Public API:
    search(text: str, k=5) -> list[Hit]

Currently backed by mock.py.
"""
from .mock import search

__all__ = ["search"]
