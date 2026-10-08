from __future__ import annotations

from evora.core.fakes import FAKE_TRACKS, fake_path
from evora.core.schemas import PathHop


def link_all() -> int:
    return len({t.global_id for t in FAKE_TRACKS if t.global_id})


def path(track_id: str) -> list[PathHop]:
    t = next((t for t in FAKE_TRACKS if t.track_id == track_id), None)
    if t is None or t.global_id is None:
        return []
    return fake_path(t.global_id)
