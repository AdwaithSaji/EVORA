"""Natural-language query parsing + the conversation engine. OWNER: P4.

Public API:
    parse(text, memory) -> QuerySpec
        Fills location_aliases; resolved ones go into camera_ids / zone_polygons,
        unknown ones into spec.unresolved.
    Engine(memory=None, index=None)
        .ask(text) -> Answer                   kind="clarify" if spec.unresolved, else runs retrieval
        .clarify(alias, camera_id, polygon=None) -> Answer
                                               learns the fact, then re-runs the pending query

Currently backed by mock.py (regex parser, no LLM yet).
"""
from .mock import Engine, parse

__all__ = ["parse", "Engine"]
