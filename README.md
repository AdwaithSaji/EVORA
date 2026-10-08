# EVORA — Multi-Stream Video Intelligence with Conversational Query

Plug in multiple recorded CCTV streams, ask in plain English ("did a red car pass through the main gate
in the last hour?") and get back **which camera, when, and the visual evidence**. Unknown places are
asked about once and remembered forever.

## Team setup (do this once)
```bash
git clone https://github.com/AdwaithSaji/EVORA.git && cd EVORA
git checkout -b p1-ingest            # p2-retrieval / p3-reid / p4-chat
cp docs/lanes/P1.md CLAUDE.local.md  # your lane: P1..P4 (gitignored, tells Claude your scope)

py -3.11 -m venv .venv               # Windows (3.10–3.12 OK);  Linux/mac: python3.11 -m venv .venv
.venv\Scripts\activate               # Linux/mac: source .venv/bin/activate

# GPU tracks (P1, P2, P3): CUDA torch first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements/base.txt -r requirements/<your-track>.txt   # retrieval | reid | app

# P4 / anyone running the UI or parser
pip install -r requirements/app.txt
ollama pull qwen2.5:7b-instruct      # or qwen2.5:3b-instruct on CPU

python -m pytest tests -q            # contract tests must pass on every branch
streamlit run app/main.py            # works now against mocks
```

## Layout
| Path | What | Owner |
|---|---|---|
| `evora/core/` | contracts: schemas, config, db, manifest, fakes | P1 |
| `evora/ingest/`, `detect/`, `index/` | decode → YOLO-World+ByteTrack → SigLIP → FAISS/SQLite | P1 |
| `evora/retrieval/`, `baseline/`, `scripts/run_eval.py` | search, verification, ablations, eval | P2 |
| `evora/reid/`, `alerts/`, `privacy/`, `live/`, `docs/writeup.md` | cross-camera paths, alerts, blur, live | P3 |
| `evora/chat/`, `memory/`, `app/`, `data_tools/`, `eval/queries_*.jsonl` | parser, clarify-once KB, UI, data | P4 |

Every package exposes its API in `__init__.py`, backed by `mock.py` until the real module lands.

## Data
Never committed. Put footage in `data/<dataset>/` with a `manifest.yaml`
(format: `evora/core/manifest.py`) and share via Google Drive. Index:
```bash
python scripts/build_index.py --manifest data/team/manifest.yaml
python scripts/run_eval.py --split dev --system baseline
python scripts/run_eval.py --split dev --system ours
```

## Rules
See `CLAUDE.md`. Only edit your own directories; `evora/core/` changes go through a PR to P1.
