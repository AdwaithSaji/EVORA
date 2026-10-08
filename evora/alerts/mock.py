from __future__ import annotations

from dataclasses import asdict

from evora.core.schemas import QuerySpec, Track

_ALERTS: dict[str, dict] = {}


def register(spec: QuerySpec, name: str) -> str:
    aid = f"a{len(_ALERTS) + 1:03d}"
    _ALERTS[aid] = {"id": aid, "name": name, "spec": asdict(spec)}
    return aid


def check_track(track: Track) -> list[str]:
    return []


def list_all() -> list[dict]:
    return list(_ALERTS.values())
