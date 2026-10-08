"""OWNER: P1. Proves evora.index / evora.ingest honor the contract."""
from evora import index, ingest
from evora.core.schemas import Camera, IndexHandle


def test_load_returns_handle():
    h = index.load()
    assert isinstance(h, IndexHandle)
    assert h.cameras and all(isinstance(c, Camera) for c in h.cameras)
    assert h.reference_now >= max(c.start_wallclock for c in h.cameras)
    assert h.camera(h.cameras[0].camera_id) is h.cameras[0]


def test_cut_clip_signature():
    h = index.load()
    c = h.cameras[0]
    out = ingest.cut_clip(c.camera_id, c.start_wallclock + 10, c.start_wallclock + 12)
    assert out is None or isinstance(out, str)
