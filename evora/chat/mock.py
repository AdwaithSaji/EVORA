from __future__ import annotations

import re
import time

from evora import index, reid, retrieval
from evora.core.schemas import Answer, QuerySpec
from evora.core.timeutil import fmt_span
from evora.memory import Memory

_LOC = re.compile(r"\b(?:through|at|near|in|by|from|entered|enter|enters)\s+(?:the\s+)?([a-z ]+?(?:gate|door|entrance|exit|lobby|parking|lot|road|corridor|hall))\b")
_LAST = re.compile(r"last\s+(\d+)?\s*(minute|min|hour|hr)s?")
_COLORS = {"red", "blue", "green", "white", "black", "yellow", "grey", "gray", "silver", "orange"}
_OBJECTS = ["person", "man", "woman", "car", "truck", "bus", "bike", "bicycle", "motorcycle", "bag", "van"]


def parse(text: str, memory: Memory, now: float | None = None) -> QuerySpec:
    low = text.lower()
    spec = QuerySpec(raw=text)
    spec.object_text = next((o for o in _OBJECTS if re.search(rf"\b{o}\b", low)), "")
    spec.attributes = [c for c in _COLORS if re.search(rf"\b{c}\b", low)]
    if "bag" in low and spec.object_text != "bag":
        spec.attributes.append("carrying a bag")
    spec.want_path = bool(re.search(r"where did|which way|path|go after", low))
    if m := _LAST.search(low):
        n = int(m.group(1) or 1)
        secs = n * (3600 if m.group(2).startswith("h") else 60)
        if now is not None:
            spec.t_from, spec.t_to = now - secs, now
    for m in _LOC.finditer(low):
        alias = m.group(1).strip()
        spec.location_aliases.append(alias)
        loc = memory.resolve(alias)
        if loc is None:
            spec.unresolved.append(alias)
        else:
            spec.camera_ids = (spec.camera_ids or []) + [loc.camera_id]
            if loc.polygon:
                spec.zone_polygons = {**(spec.zone_polygons or {}), loc.camera_id: loc.polygon}
    return spec


class Engine:
    def __init__(self, memory: Memory | None = None, idx=None):
        self.memory = memory or Memory()
        self.index = idx or index.load()
        self._pending: str | None = None

    def ask(self, text: str) -> Answer:
        t0 = time.perf_counter()
        spec = parse(text, self.memory, now=self.index.reference_now)
        if spec.unresolved:
            self._pending = text
            alias = spec.unresolved[0]
            return Answer("clarify", f"Which camera is '{alias}'? Pick it below.", spec,
                          clarify_alias=alias)
        hits = retrieval.search(spec, k=5)
        ms = (time.perf_counter() - t0) * 1000
        if not hits:
            return Answer("no_result", "No matching event found.", spec, latency_ms=ms)
        top = hits[0]
        cam = self.index.camera(top.camera_id)
        path = reid.path(top.track_id) if spec.want_path and top.track_id else []
        return Answer("answer", f"Yes — {cam.name} at {fmt_span(top.t_start, top.t_end)}.",
                      spec, hits, path, latency_ms=ms)

    def clarify(self, alias: str, camera_id: str, polygon=None) -> Answer:
        self.memory.learn(alias, camera_id, polygon, utterance=self._pending or "")
        pending, self._pending = self._pending, None
        return self.ask(pending) if pending else Answer("answer", f"Got it: '{alias}' is {camera_id}.")
