"""Paths and global settings. OWNER: P1. Override any value with an env var of the same name."""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default):
    val = os.environ.get(name)
    if val is None:
        return default
    return type(default)(val) if not isinstance(default, Path) else Path(val)


DATA_DIR: Path = _env("EVORA_DATA_DIR", REPO_ROOT / "data")
FRAMES_DIR: Path = DATA_DIR / "frames"          # data/frames/<camera_id>/<ts>.jpg
CROPS_DIR: Path = DATA_DIR / "crops"            # data/crops/<track_id>.jpg
CLIPS_DIR: Path = DATA_DIR / "clips"
THUMBS_DIR: Path = DATA_DIR / "thumbs"
INDEX_DIR: Path = DATA_DIR / "index"

EVORA_DB: Path = DATA_DIR / "evora.db"          # rebuilt by indexing
MEMORY_DB: Path = DATA_DIR / "memory.db"        # NEVER deleted by indexing (clarify-once facts)

FRAMES_FAISS: Path = INDEX_DIR / "frames.faiss"
FRAMES_IDS: Path = INDEX_DIR / "frames_ids.npy"   # faiss row -> frames.frame_id
TRACKS_FAISS: Path = INDEX_DIR / "tracks.faiss"
TRACKS_IDS: Path = INDEX_DIR / "tracks_ids.json"  # faiss row -> track_id

SAMPLE_FPS: float = _env("EVORA_SAMPLE_FPS", 2.0)

EMBED_MODEL: str = _env("EVORA_EMBED_MODEL", "google/siglip-so400m-patch14-384")
DETECT_MODEL: str = _env("EVORA_DETECT_MODEL", "yolov8x-worldv2.pt")
VERIFY_MODEL: str = _env("EVORA_VERIFY_MODEL", "google/owlv2-base-patch16-ensemble")
LLM_MODEL: str = _env("EVORA_LLM_MODEL", "qwen2.5:7b-instruct")
OLLAMA_HOST: str = _env("OLLAMA_HOST", "http://localhost:11434")

DETECT_VOCAB: list[str] = [
    "person", "car", "truck", "bus", "van", "motorcycle", "bicycle", "auto rickshaw",
    "backpack", "handbag", "suitcase", "bag", "box", "umbrella", "dog", "cat",
]

# Set to an epoch float to pin "now" for relative-time queries; None = end of footage.
_ref = os.environ.get("EVORA_REFERENCE_NOW")
REFERENCE_NOW: float | None = float(_ref) if _ref else None

# Retrieval
EVENT_MERGE_GAP_S: float = 10.0   # hits on same camera closer than this merge into one event
CLIP_PAD_BEFORE_S: float = 3.0
CLIP_PAD_AFTER_S: float = 5.0


def ensure_dirs() -> None:
    for d in (DATA_DIR, FRAMES_DIR, CROPS_DIR, CLIPS_DIR, THUMBS_DIR, INDEX_DIR):
        d.mkdir(parents=True, exist_ok=True)
