"""Privacy: face blurring on evidence frames / clips. All inference is local. OWNER: P3.

Public API:
    blur_image(path) -> str   path of blurred copy
    blur_clip(path) -> str    path of blurred copy

Currently backed by mock.py (returns the input unchanged).
"""
from .mock import blur_clip, blur_image

__all__ = ["blur_image", "blur_clip"]
