"""Evaluate baseline vs ours on a query split.   OWNER: P2
Usage:  python scripts/run_eval.py --split dev --system ours [--no-verify ...]

Query file format: eval/queries_<split>.jsonl, see eval/queries_example.jsonl.
TODO(P2): Hit@1/Hit@5/MRR, camera acc, temporal hit (|dt|<=5s or tIoU>=0.3), latency p50/p95,
          memory-dependent queries (pre-load memory facts from the "memory" field), CSV + markdown out.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evora import baseline, index, retrieval  # noqa: E402
from evora.chat import parse  # noqa: E402
from evora.memory import Memory  # noqa: E402

TOL_S = 5.0


def correct(hit, answers, idx) -> bool:
    for a in answers:
        if hit.camera_id != a["camera_id"]:
            continue
        t0 = idx.camera(a["camera_id"]).start_wallclock
        if hit.t_start - TOL_S <= t0 + a["offset_end"] and hit.t_end + TOL_S >= t0 + a["offset_start"]:
            return True
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="example")
    ap.add_argument("--system", choices=["baseline", "ours"], default="ours")
    ap.add_argument("-k", type=int, default=5)
    args = ap.parse_args()

    idx = index.load()
    rows = [json.loads(line) for line in Path(f"eval/queries_{args.split}.jsonl").read_text().splitlines() if line.strip()]
    h1 = h5 = 0
    lat = []
    for r in rows:
        mem = Memory()
        for alias, cam in r.get("memory", {}).items():
            mem.learn(alias, cam)
        t0 = time.perf_counter()
        if args.system == "baseline":
            hits = baseline.search(r["query"], k=args.k)
        else:
            hits = retrieval.search(parse(r["query"], mem, now=idx.reference_now), k=args.k)
        lat.append((time.perf_counter() - t0) * 1000)
        h1 += bool(hits) and correct(hits[0], r["answers"], idx)
        h5 += any(correct(h, r["answers"], idx) for h in hits)
    n = max(len(rows), 1)
    lat.sort()
    print(f"{args.system}: n={len(rows)} Hit@1={h1/n:.2f} Hit@{args.k}={h5/n:.2f} p50={lat[len(lat)//2] if lat else 0:.1f}ms")
