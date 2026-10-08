from __future__ import annotations

import re

from evora.core.schemas import Location, Polygon


def normalize_alias(text: str) -> str:
    t = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    t = re.sub(r"\b(the|a|an|our|my)\b", " ", t)
    return " ".join(t.split())


class Memory:
    def __init__(self, path=None):
        self._facts: dict[str, Location] = {}

    def resolve(self, alias: str) -> Location | None:
        return self._facts.get(normalize_alias(alias))

    def learn(self, alias: str, camera_id: str, polygon: Polygon | None = None,
              utterance: str = "") -> Location:
        loc = Location(normalize_alias(alias), camera_id, polygon)
        self._facts[loc.alias] = loc
        return loc

    def forget(self, alias: str) -> None:
        self._facts.pop(normalize_alias(alias), None)

    def all(self) -> list[Location]:
        return list(self._facts.values())
