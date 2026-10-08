"""EVORA chat UI. OWNER: P4.   Run:  streamlit run app/main.py

Skeleton that already works end-to-end against the mocks; P4 grows it
(thumbnails grid, region drawing, path timeline, baseline toggle, memory sidebar).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from evora.chat import Engine  # noqa: E402
from evora.core.timeutil import fmt, fmt_span  # noqa: E402

st.set_page_config(page_title="EVORA", layout="wide")

if "engine" not in st.session_state:
    st.session_state.engine = Engine()
    st.session_state.history = []
eng: Engine = st.session_state.engine

with st.sidebar:
    st.header("Memory")
    facts = eng.memory.all()
    for loc in facts:
        st.write(f"**{loc.alias}** → {eng.index.camera(loc.camera_id).name}"
                 + (" (zone)" if loc.polygon else ""))
    if not facts:
        st.caption("Nothing learned yet.")


def render(ans):
    st.markdown(ans.text)
    for h in ans.hits[:3]:
        cam = eng.index.camera(h.camera_id)
        st.caption(f"{cam.name} · {fmt_span(h.t_start, h.t_end)} · score {h.score:.2f}")
        if h.evidence_frame_path and Path(h.evidence_frame_path).exists():
            st.image(h.evidence_frame_path)
        if h.clip_path and Path(h.clip_path).exists():
            st.video(h.clip_path)
    if ans.path:
        st.markdown(" → ".join(f"{eng.index.camera(p.camera_id).name} {fmt(p.t_enter)}" for p in ans.path))


for role, payload in st.session_state.history:
    with st.chat_message(role):
        if role == "assistant":
            render(payload)
        else:
            st.markdown(payload)

pending = st.session_state.history[-1][1] if st.session_state.history and st.session_state.history[-1][0] == "assistant" else None
if pending is not None and pending.kind == "clarify":
    cols = st.columns(len(eng.index.cameras))
    for col, cam in zip(cols, eng.index.cameras):
        with col:
            if cam.thumbnail_path and Path(cam.thumbnail_path).exists():
                st.image(cam.thumbnail_path)
            if st.button(cam.name, key=f"pick_{cam.camera_id}"):
                st.session_state.history.append(("user", f"'{pending.clarify_alias}' is {cam.name}"))
                st.session_state.history.append(("assistant", eng.clarify(pending.clarify_alias, cam.camera_id)))
                st.rerun()

if q := st.chat_input("Ask about the footage…"):
    st.session_state.history.append(("user", q))
    st.session_state.history.append(("assistant", eng.ask(q)))
    st.rerun()
