# Eval query format (`queries_<split>.jsonl`, one JSON per line)

| field | meaning |
|---|---|
| `id` | unique id |
| `query` | natural-language question exactly as a judge would type it |
| `answers` | list of `{camera_id, offset_start, offset_end}` — **seconds from the start of that camera's video** (what you read off the player while scrubbing). Any one match counts as correct. |
| `memory` | optional `{alias: camera_id}` facts pre-loaded before running (for queries that use "main gate" etc.) |
| `type` | `open-vocab`, `object+location+time`, `path`, `zone`, … (for per-type breakdown) |
| `needs_memory` | true if the query uses a location alias |
| `path` (path queries) | optional ordered list of `camera_id` the subject visits |

Splits: `dev` (tune on it freely), `heldout` (written by P3/P4, **P2 never opens it while tuning**).
`scripts/run_eval.py` converts offsets to wall-clock using each camera's `start_wallclock`.
