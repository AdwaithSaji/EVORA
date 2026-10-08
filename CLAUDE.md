# EVORA — Claude instructions (shared, read by every teammate's Claude)

Hackathon project (24h, team of 4): multi-camera CCTV video intelligence with conversational query.
User asks "did a red car pass through the main gate in the last hour?" → system answers with
**camera + timestamp + evidence frame + clip**. Unknown places ("main gate") are asked about ONCE,
stored in `data/memory.db`, and never asked again (even after restart). Must beat a baseline
(frame-level SigLIP + FAISS) on held-out queries, with an ablation.

## Read first
- `evora/core/schemas.py` — the data contracts (Camera, Track, QuerySpec, Hit, PathHop, Location, IndexHandle, Answer).
- The `__init__.py` docstring of the package you are working in — it states its public API.
- If a `CLAUDE.local.md` exists, it says which person/track you are. **Stay in that lane.**

## Pipeline
```
manifest.yaml → [P1 ingest/detect/index] → data/evora.db + data/index/{frames,tracks}.faiss
user text → [P4 chat.parse + memory] → QuerySpec → [P2 retrieval] → list[Hit] → [P3 reid.path] → [P4 app]
```

## Directory ownership — only edit files you own
| Track | Owns |
|---|---|
| P1 Ingest & Index | `evora/core/`, `evora/ingest/`, `evora/detect/`, `evora/index/`, `scripts/build_index.py`, `requirements/base.txt`, `README.md` |
| P2 Retrieval & Research | `evora/retrieval/`, `evora/baseline/`, `scripts/run_eval.py`, `eval/*.py`, `requirements/retrieval.txt` |
| P3 Re-ID, Bonuses, Write-up | `evora/reid/`, `evora/alerts/`, `evora/privacy/`, `evora/live/`, `docs/writeup.md`, `requirements/reid.txt` |
| P4 Data, Chat & Memory | `data_tools/`, `eval/queries_*.jsonl`, `evora/chat/`, `evora/memory/`, `app/`, `requirements/app.txt` |

Each owner also owns their file in `tests/contracts/`.

## Rules
- Never edit another track's directory or `evora/core/`. If you need a contract change, write the
  proposed diff in your reply so the human can raise a PR to P1. Don't work around a contract by duplicating it.
- Public API signatures in each package `__init__.py` are frozen; add new functions rather than changing old ones.
- Each package starts with a `mock.py`. Build the real implementation in new modules, then switch the
  import in your own `__init__.py`. Keep `tests/contracts/` passing: `python -m pytest tests -q`.
- Timestamps = wall-clock epoch seconds (float). Bboxes = pixel `[x1,y1,x2,y2]`. Zone polygons = normalized 0..1.
- Paths come from `evora/core/config.py` — never hardcode `data/...`.
- Never commit data: videos, frames, `*.db`, `*.faiss`, weights are gitignored (share via Google Drive).
- Git: work on your branch (`p1-ingest`, `p2-retrieval`, `p3-reid`, `p4-chat`), small PRs to `main`, rebase often.
- Python 3.11 (3.10–3.12 OK). Windows + Linux laptops: use `pathlib`, no shell-specific code in Python.
- All inference is local (privacy bonus): no cloud vision/LLM APIs. LLM = Ollama.
