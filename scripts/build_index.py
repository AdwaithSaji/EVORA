"""Index a multi-camera manifest.   OWNER: P1
Usage:  python scripts/build_index.py --manifest data/team/manifest.yaml
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evora import index  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    h = index.build(args.manifest)
    for c in h.cameras:
        print(f"{c.camera_id:8s} {c.name:20s} {c.duration:7.1f}s")
