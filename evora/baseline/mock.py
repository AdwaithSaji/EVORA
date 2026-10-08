from __future__ import annotations

from evora.core.fakes import FAKE_TRACKS, track_to_hit
from evora.core.schemas import Hit


def search(text: str, k: int = 5) -> list[Hit]:
    return [track_to_hit(t, 0.5 - 0.01 * i, "mock baseline") for i, t in enumerate(FAKE_TRACKS)][:k]
