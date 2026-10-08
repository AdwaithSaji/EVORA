"""OWNER: P3. Proves evora.reid / alerts / privacy honor the contract."""
from evora import alerts, privacy, reid
from evora.core.fakes import FAKE_TRACKS
from evora.core.schemas import PathHop, QuerySpec


def test_reid_path_is_ordered_hops():
    assert isinstance(reid.link_all(), int)
    hops = reid.path("cam01_t0002")
    assert all(isinstance(h, PathHop) for h in hops)
    assert [h.t_enter for h in hops] == sorted(h.t_enter for h in hops)


def test_reid_unknown_track():
    assert reid.path("nope_t9999") == []


def test_alerts():
    aid = alerts.register(QuerySpec(raw="anyone at gate after 8pm", object_text="person"), "gate-night")
    assert isinstance(aid, str)
    assert isinstance(alerts.check_track(FAKE_TRACKS[0]), list)
    assert any(a["id"] == aid for a in alerts.list_all())


def test_privacy_returns_paths():
    assert isinstance(privacy.blur_image("x.jpg"), str)
    assert isinstance(privacy.blur_clip("x.mp4"), str)
