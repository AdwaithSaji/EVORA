"""Download a time window of MEVA multi-camera footage and write an EVORA manifest. OWNER: P4.

MEVA is public (s3://mevadata-public-01, no account needed). Clips are 5-min H.264 1080p30 .avi
named like  2018-03-07.17-00-00.17-05-00.school.G330.r13.avi  (date.start.end.site.camera).
Consecutive clips of one camera are joined losslessly (ffmpeg concat, stream copy) into one .mp4.

Explore what exists:
    python data_tools/download_meva.py --date 2018-03-07 --list
Download (default: school site, 17:00-17:20, all its cameras):
    python data_tools/download_meva.py --date 2018-03-07 --site school --start 17:00 --minutes 20
    python data_tools/download_meva.py ... --cameras G330 G336 G419      # subset
    python data_tools/download_meva.py ... --dry-run                      # show plan + size only

Output: data/meva/<site>_<date>_<HHMM>/{raw/*.avi, videos/<cam>.mp4, manifest.yaml}
Stdlib only (+ ffmpeg on PATH). Re-running resumes: finished files are skipped.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

BUCKET = "https://mevadata-public-01.s3.amazonaws.com"
PREFIX = "drops-123-r13"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
NAME_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\.(?P<start>\d{2}-\d{2}-\d{2})\.(?P<end>\d{2}-\d{2}-\d{2})"
    r"\.(?P<site>[a-z]+)\.(?P<cam>G\d+)\.r13\.avi$"
)
REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_GAP_S = 3.0  # clips further apart than this are not joined (keeps timestamps honest)


@dataclass
class Clip:
    key: str
    size: int
    site: str
    cam: str
    start: datetime
    end: datetime

    @property
    def url(self) -> str:
        return f"{BUCKET}/{urllib.parse.quote(self.key)}"


def list_keys(prefix: str) -> list[tuple[str, int]]:
    out, token = [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        with urllib.request.urlopen(f"{BUCKET}/?{urllib.parse.urlencode(q)}", timeout=60) as r:
            root = ET.fromstring(r.read())
        for c in root.findall("s3:Contents", NS):
            out.append((c.find("s3:Key", NS).text, int(c.find("s3:Size", NS).text)))
        if root.findtext("s3:IsTruncated", namespaces=NS) != "true":
            return out
        token = root.findtext("s3:NextContinuationToken", namespaces=NS)


def clips_for(date: str, hours: list[int]) -> list[Clip]:
    clips = []
    for h in hours:
        for key, size in list_keys(f"{PREFIX}/{date}/{h:02d}/"):
            m = NAME_RE.search(key)
            if not m:
                continue
            d = m["date"]
            start = datetime.strptime(f"{d} {m['start']}", "%Y-%m-%d %H-%M-%S")
            end = datetime.strptime(f"{d} {m['end']}", "%Y-%m-%d %H-%M-%S")
            clips.append(Clip(key, size, m["site"], m["cam"], start, end))
    return clips


def do_list(date: str, min_mb: float) -> None:
    clips = [c for c in clips_for(date, list(range(24))) if c.size >= min_mb * 1e6]
    by = defaultdict(lambda: defaultdict(list))
    for c in clips:
        by[c.site][c.start.hour].append(c.cam)
    for site in sorted(by):
        print(f"\n{site}:")
        for h in sorted(by[site]):
            cams = sorted(set(by[site][h]))
            print(f"  {h:02d}:00  {len(cams):2d} cams, {len(by[site][h]):3d} clips  {' '.join(cams)}")


def download(clip: Clip, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size == clip.size:
        return
    part = dest.with_suffix(dest.suffix + ".part")
    have = part.stat().st_size if part.exists() else 0
    req = urllib.request.Request(clip.url, headers={"Range": f"bytes={have}-"} if have else {})
    with urllib.request.urlopen(req, timeout=120) as r, open(part, "ab" if have else "wb") as f:
        done = have
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            print(f"\r    {dest.name}  {done / 1e6:7.1f}/{clip.size / 1e6:.1f} MB", end="", flush=True)
    print()
    part.replace(dest)


def contiguous_run(clips: list[Clip]) -> list[Clip]:
    """Longest prefix of time-sorted clips with no gap > MAX_GAP_S."""
    run = [clips[0]]
    for c in clips[1:]:
        if (c.start - run[-1].end).total_seconds() > MAX_GAP_S:
            print(f"    gap before {c.key.rsplit('/', 1)[-1]} — stopping this camera here")
            break
        run.append(c)
    return run


def join(parts: list[Path], out: Path) -> None:
    if out.exists():
        return
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
           "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    lst.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default="2018-03-07")
    ap.add_argument("--list", action="store_true", help="show sites/hours/cameras for --date and exit")
    ap.add_argument("--site", default="school")
    ap.add_argument("--start", default="17:00", help="HH:MM local facility time")
    ap.add_argument("--minutes", type=int, default=20)
    ap.add_argument("--cameras", nargs="*", help="e.g. G330 G336 (default: all at the site)")
    ap.add_argument("--min-mb", type=float, default=20.0, help="skip tiny/broken clips")
    ap.add_argument("--out", type=Path, help="default data/meva/<site>_<date>_<HHMM>")
    ap.add_argument("--keep-raw", action="store_true", help="keep the 5-min .avi parts after joining")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.list:
        do_list(a.date, a.min_mb)
        return
    if not a.dry_run and shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH (needed to join clips).")

    t0 = datetime.strptime(f"{a.date} {a.start}", "%Y-%m-%d %H:%M")
    t1 = t0 + timedelta(minutes=a.minutes)
    hours = sorted({(t0 + timedelta(minutes=m)).hour for m in range(0, a.minutes + 1, 5)})
    clips = [c for c in clips_for(a.date, hours)
             if c.site == a.site and c.size >= a.min_mb * 1e6
             and c.end > t0 and c.start < t1
             and (not a.cameras or c.cam in a.cameras)]
    if not clips:
        sys.exit(f"No clips for site={a.site} {t0:%Y-%m-%d %H:%M}+{a.minutes}min. Try --list.")

    per_cam: dict[str, list[Clip]] = defaultdict(list)
    for c in sorted(clips, key=lambda c: c.start):
        per_cam[c.cam].append(c)

    out = a.out or REPO_ROOT / "data" / "meva" / f"{a.site}_{a.date}_{t0:%H%M}"
    total = sum(c.size for c in clips)
    print(f"{len(per_cam)} cameras, {len(clips)} clips, {total / 1e9:.2f} GB -> {out}")
    for cam, cs in sorted(per_cam.items()):
        print(f"  {cam}: {cs[0].start:%H:%M:%S} -> {cs[-1].end:%H:%M:%S}  ({len(cs)} clips)")
    if a.dry_run:
        return

    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "videos").mkdir(parents=True, exist_ok=True)
    entries = []
    for cam, cs in sorted(per_cam.items()):
        cs = contiguous_run(cs)
        print(f"[{cam}]")
        parts = []
        for c in cs:
            p = out / "raw" / c.key.rsplit("/", 1)[-1]
            download(c, p)
            parts.append(p)
        mp4 = out / "videos" / f"{cam.lower()}.mp4"
        join(parts, mp4)
        if not a.keep_raw:
            for p in parts:
                p.unlink(missing_ok=True)
        entries.append((cam, cs[0].start))

    lines = [f"# MEVA {a.site} {a.date} {t0:%H:%M} +{a.minutes}min — generated by data_tools/download_meva.py",
             "# start_wallclock = facility local time from the MEVA file names", "cameras:"]
    for cam, start in entries:
        lines += [f"  - camera_id: {cam.lower()}",
                  f"    name: {a.site.capitalize()} {cam}",
                  f"    file: videos/{cam.lower()}.mp4",
                  f'    start_wallclock: "{start:%Y-%m-%dT%H:%M:%S}"']
    (out / "manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nDone. Manifest: {out / 'manifest.yaml'}")
    print("Give camera names meaningful aliases later via the app's clarify-once memory, not here.")


if __name__ == "__main__":
    main()
