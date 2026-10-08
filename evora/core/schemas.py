"""Shared data contracts for every EVORA module.

OWNER: P1. Changing anything here = PR + ping the team (other tracks build on it).

Conventions
- Timestamps are wall-clock UNIX epoch seconds (float, UTC). Use `evora.core.timeutil` to format.
- Bounding boxes are pixel coords [x1, y1, x2, y2] in the source video's resolution.
- Polygons (zones) are normalized [[x, y], ...] with x, y in 0..1 relative to frame size.
- camera_id is a short slug like "cam01"; track_id is "<camera_id>_t<NNNN>"; global_id (re-ID) is "g<NNNN>".
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal, Optional

BBox = list[float]            # [x1, y1, x2, y2] pixels
Polygon = list[list[float]]   # [[x, y], ...] normalized 0..1


@dataclass
class Camera:
    camera_id: str
    name: str                     # human name from the manifest, e.g. "North entrance"
    video_path: str
    start_wallclock: float        # epoch seconds of the first frame
    fps: float = 0.0
    duration: float = 0.0         # seconds
    width: int = 0
    height: int = 0
    thumbnail_path: Optional[str] = None

    @property
    def end_wallclock(self) -> float:
        return self.start_wallclock + self.duration


@dataclass
class Track:
    """One object tracked within ONE camera (ByteTrack id)."""
    track_id: str
    camera_id: str
    label: str                    # detector label, e.g. "car", "person"
    t_start: float
    t_end: float
    best_crop_path: Optional[str] = None
    best_frame_path: Optional[str] = None
    best_ts: Optional[float] = None
    best_bbox: Optional[BBox] = None
    bbox_traj: list[tuple[float, BBox]] = field(default_factory=list)  # (ts, bbox), subsampled
    colors: list[str] = field(default_factory=list)       # dominant color names, e.g. ["red"]
    attributes: list[str] = field(default_factory=list)   # e.g. ["carrying bag", "large bag"]
    emb_id: Optional[int] = None  # row in tracks.faiss
    global_id: Optional[str] = None  # cross-camera identity (filled by P3 re-ID)


Action = Literal["present", "pass", "enter_zone", "exit_zone", "any"]


@dataclass
class QuerySpec:
    """Structured form of a natural-language query (produced by P4 chat.parse)."""
    raw: str
    object_text: str = ""                 # open-vocab noun phrase, e.g. "car", "person"
    attributes: list[str] = field(default_factory=list)       # e.g. ["red"], ["carrying a large bag"]
    location_aliases: list[str] = field(default_factory=list)  # phrases as the user said them: ["main gate"]
    camera_ids: Optional[list[str]] = None        # resolved cameras (None = all cameras)
    zone_polygons: Optional[dict[str, Polygon]] = None  # camera_id -> polygon, if a region was learned
    t_from: Optional[float] = None
    t_to: Optional[float] = None
    action: Action = "any"
    unresolved: list[str] = field(default_factory=list)  # aliases memory could not resolve -> must ask
    want_path: bool = False                # "where did it go" -> cross-camera path requested

    @property
    def search_text(self) -> str:
        """Phrase to embed for open-vocab search, e.g. 'red car'."""
        return " ".join([*self.attributes, self.object_text]).strip() or self.raw


@dataclass
class Hit:
    """One grounded answer: camera + time span + visual evidence."""
    camera_id: str
    t_start: float
    t_end: float
    score: float
    evidence_frame_path: Optional[str] = None
    bbox: Optional[BBox] = None
    track_id: Optional[str] = None
    clip_path: Optional[str] = None
    explanation: str = ""

    @property
    def t_center(self) -> float:
        return (self.t_start + self.t_end) / 2


@dataclass
class PathHop:
    camera_id: str
    t_enter: float
    t_exit: float
    track_id: str


@dataclass
class Location:
    """A learned referent from memory: alias -> camera (+ optional zone)."""
    alias: str                    # normalized alias, e.g. "main gate"
    camera_id: str
    polygon: Optional[Polygon] = None


@dataclass
class IndexHandle:
    cameras: list[Camera]
    db_path: str
    frames_index_path: str
    tracks_index_path: str

    def camera(self, camera_id: str) -> Camera:
        for c in self.cameras:
            if c.camera_id == camera_id:
                return c
        raise KeyError(camera_id)

    @property
    def reference_now(self) -> float:
        """'Now' for recorded footage = end of the latest camera."""
        return max((c.end_wallclock for c in self.cameras), default=0.0)


@dataclass
class Answer:
    """What the conversation engine returns to the UI for one user turn."""
    kind: Literal["answer", "clarify", "no_result"]
    text: str
    spec: Optional[QuerySpec] = None
    hits: list[Hit] = field(default_factory=list)
    path: list[PathHop] = field(default_factory=list)
    clarify_alias: Optional[str] = None   # set when kind == "clarify"
    latency_ms: float = 0.0


def to_dict(obj) -> dict:
    return asdict(obj)
