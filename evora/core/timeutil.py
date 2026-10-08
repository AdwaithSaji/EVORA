"""Time helpers shared by all tracks. OWNER: P1."""
from __future__ import annotations

from datetime import datetime


def fmt(ts: float, with_date: bool = False) -> str:
    """Epoch seconds -> local 'HH:MM:SS' (or 'YYYY-MM-DD HH:MM:SS')."""
    d = datetime.fromtimestamp(ts)
    return d.strftime("%Y-%m-%d %H:%M:%S" if with_date else "%H:%M:%S")


def fmt_span(t0: float, t1: float) -> str:
    return fmt(t0) if abs(t1 - t0) < 1 else f"{fmt(t0)}–{fmt(t1)}"
