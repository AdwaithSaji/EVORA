from __future__ import annotations

from evora.core.fakes import FAKE_TRACKS, track_to_hit
from evora.core.schemas import Hit, QuerySpec


def search(spec: QuerySpec, k: int = 5, options: dict | None = None) -> list[Hit]:
    words = spec.search_text.lower().split()
    hits = []
    for t in FAKE_TRACKS:
        if spec.camera_ids and t.camera_id not in spec.camera_ids:
            continue
        if spec.t_from is not None and t.t_end < spec.t_from:
            continue
        if spec.t_to is not None and t.t_start > spec.t_to:
            continue
        text = " ".join([t.label, *t.colors, *t.attributes])
        score = sum(w in text for w in words) / max(len(words), 1)
        if score > 0:
            hits.append(track_to_hit(t, score, f"mock match on '{text}'"))
    return sorted(hits, key=lambda h: -h.score)[:k]
