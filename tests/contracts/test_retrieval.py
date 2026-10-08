"""OWNER: P2. Proves evora.retrieval / evora.baseline honor the contract."""
from evora import baseline, retrieval
from evora.core.schemas import Hit, QuerySpec


def _check_hits(hits, k):
    assert isinstance(hits, list) and len(hits) <= k
    assert all(isinstance(h, Hit) for h in hits)
    assert all(h.t_start <= h.t_end for h in hits)
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_retrieval_search():
    spec = QuerySpec(raw="red car", object_text="car", attributes=["red"])
    _check_hits(retrieval.search(spec, k=5), 5)


def test_retrieval_respects_camera_filter():
    spec = QuerySpec(raw="person", object_text="person", camera_ids=["cam02"])
    assert all(h.camera_id == "cam02" for h in retrieval.search(spec, k=5))


def test_retrieval_accepts_ablation_options():
    spec = QuerySpec(raw="red car", object_text="car", attributes=["red"])
    opts = dict(use_filters=False, use_tracks=False, use_frames=True, use_verify=False, use_merge=False)
    _check_hits(retrieval.search(spec, k=3, options=opts), 3)


def test_baseline_search():
    _check_hits(baseline.search("red car", k=5), 5)
