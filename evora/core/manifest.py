"""Load a multi-camera manifest (also the format for judges' footage). OWNER: P1.

manifest.yaml:
    cameras:
      - camera_id: cam01
        name: North entrance
        file: videos/cam01.mp4          # relative to the manifest's folder
        start_wallclock: "2026-10-08T09:00:00"   # local time; optional
      - ...

If start_wallclock is missing it stays None; ingest then uses DEFAULT_START so all
cameras share a common zero (assumes the recordings started together). Provide it when you can.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_START = 1767258000.0  # 2026-01-01 09:00:00 UTC


@dataclass
class ManifestEntry:
    camera_id: str
    name: str
    file: Path
    start_wallclock: float | None


def _parse_time(v) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, datetime):
        return v.timestamp()
    return datetime.fromisoformat(str(v)).timestamp()


def load_manifest(path: str | Path) -> list[ManifestEntry]:
    import yaml  # local import so core stays importable without pyyaml

    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries = []
    for c in data["cameras"]:
        f = Path(c["file"])
        if not f.is_absolute():
            f = (path.parent / f).resolve()
        entries.append(ManifestEntry(
            camera_id=str(c["camera_id"]),
            name=str(c.get("name", c["camera_id"])),
            file=f,
            start_wallclock=_parse_time(c.get("start_wallclock")),
        ))
    return entries
