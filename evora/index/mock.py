from __future__ import annotations

from evora.core.fakes import fake_index
from evora.core.schemas import IndexHandle


def build(manifest_path: str) -> IndexHandle:
    return fake_index()


def load() -> IndexHandle:
    return fake_index()
