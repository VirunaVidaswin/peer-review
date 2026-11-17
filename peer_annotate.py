"""
MARC: Peer Annotation App
Streamlit app for the peer annotator (blinded — no framework/mode labels).

Run with:
    pip install streamlit pandas
    streamlit run peer_annotate.py

NOTE: This app reads peer_traces.jsonl from the same folder.
      Saves annotations to peer_answers.csv in the same folder.

Author: Viruna (RGU 2331420 / IIT 20231903)
Project: MARC — Multi-Agent Realignment and Correction
"""

import json
import os
import sys
import datetime
import csv
from pathlib import Path

import streamlit as st
import pandas as pd

# ─── Paths (all relative to this script's location) ───────────────────────────
HERE = Path(__file__).parent.resolve()
JSONL_PATH  = HERE / "peer_traces.jsonl"
ANSWERS_CSV = HERE / "peer_answers.csv"

ANSWER_COLS = ["code", "failure_occurred", "failure_mode", "onset_turn", "notes"]

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MARC Peer Annotation",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.goal-box {
    background: #1a3a2a;
    border-left: 4px solid #22c55e;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0 16px 0;
    color: #dcfce7;
    font-size: 0.9em;
    line-height: 1.5;
}
.peer-header {
    background: #0f2d1a;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
}
.status-done       { color: #22c55e; }
.status-inprogress { color: #f59e0b; }
.status-untouched  { color: #6b7280; }
.save-info { font-size: 0.75em; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

STATUS_ICON = {"done": "✅", "inprogress": "🟡", "untouched": "⬜"}

# ─── Load peer traces ─────────────────────────────────────────────────────────
@st.cache_data
def load_peer_traces():
    if not JSONL_PATH.exists():
        return None
    records = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

# ─── Load / init answers CSV ──────────────────────────────────────────────────
def load_answers():
    if not ANSWERS_CSV.exists():
        return {}
    try:
        df = pd.read_csv(ANSWERS_CSV, encoding="utf-8", dtype=str)
        return {row["code"]: row.to_dict() for _, row in df.iterrows()}
    except Exception:
        return {}

def save_answers(answers_map):
    rows = []
    for code, row in answers_map.items():
        rows.append({col: row.get(col, "") for col in ANSWER_COLS})
    df = pd.DataFrame(rows, columns=ANSWER_COLS)
    df.to_csv(ANSWERS_CSV, index=False, encoding="utf-8")

def get_peer_status(answers_map, code):
    row = answers_map.get(code, {})
    fo   = str(row.get("failure_occurred", "")).strip()
    fm   = str(row.get("failure_mode", "")).strip()
    ons  = str(row.get("onset_turn", "")).strip()
    filled = sum([
        fo not in ("", "nan", "NaN"),
        fm not in ("", "nan", "NaN"),
        ons not in ("", "nan", "NaN"),
    ])
    if filled >= 3:
        return "done"
    elif filled > 0:
        return "inprogress"
    else:
        return "untouched"

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    st.title("📝 MARC — Peer Annotation")

    # Load traces
    traces = load_peer_traces()
    if traces is None:
        st.error("❌ `peer_traces.jsonl` not found in this folder.")
        st.info("Please ensure `peer_traces.jsonl` is in the same directory as this script.")
        st.stop()

    # Load existing answers
    answers_map = load_answers()

    # Session state
    if "current_idx" not in st.session_state:
        st.session_state.current_idx = 0
    if "last_saved" not in st.session_state:
        st.session_state.last_saved = None

    # Statuses
    statuses = [get_peer_status(answers_map, t["code"]) for t in traces]
    done_count = statuses.count("done")

    # Progress bar
    st.markdown(f"**Progress: {done_count} / {len(traces)} complete**")
    st.progress(done_count / max(len(traces), 1))

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 📝 Peer Annotator")
        st.markdown("""
> ⚠️ **Please do NOT** discuss your annotations with the author until all annotation is complete.
        """)
        st.markdown("---")

        # Filters
        status_filter = st.multiselect(
            "Filter by status",
            ["done", "inprogress", "untouched"],
            default=["done", "inprogress", "untouched"],
        )
        filtered_indices = [i for i, t in enumerate(traces) if statuses[i] in status_filter]

        st.markdown("---")
        st.markdown("### Jump to Trace")
        jump = st.number_input("Index (0–15)", min_value=0, max_value=len(traces)-1,
                               value=st.session_state.current_idx, step=1)
        if st.button("Go"):
            st.session_state.current_idx = int(jump)
            st.rerun()

        st.markdown("---")
        st.markdown("### ⌨️ Keyboard Shortcuts")
        st.info("Streamlit does not support custom keyboard shortcuts.\n\nUse the Previous / Next buttons below the form.")

        st.markdown("---")
        st.markdown("### Trace List")
        for i in filtered_indices:
            t    = traces[i]
            code = t["code"]
            icon = STATUS_ICON[statuses[i]]
            if st.button(f"{icon} {code}", key=f"nav_{i}"):
                st.session_state.current_idx = i
                st.rerun()

        st.markdown("---")
        st.markdown("### Export & Backup")
        # Direct CSV download button (vital for Cloud deployment!)
        rows_dl = []
        for c_code, r_row in answers_map.items():
            rows_dl.append({col: r_row.get(col, "") for col in ANSWER_COLS})
        df_dl = pd.DataFrame(rows_dl, columns=ANSWER_COLS)
        csv_bytes = df_dl.to_csv(index=False, encoding="utf-8").encode("utf-8")

        st.download_button(
            label="📥 Download answers (.csv)",
            data=csv_bytes,
            file_name="peer_answers.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )

        st.markdown("---")
        st.markdown("### Resume Progress")
        uploaded_file = st.file_uploader("📤 Upload previous peer_answers.csv", type=["csv"])
        if uploaded_file is not None:
            try:
                up_df = pd.read_csv(uploaded_file, encoding="utf-8", dtype=str)
                for _, u_row in up_df.iterrows():
                    answers_map[u_row["code"]] = u_row.to_dict()
                save_answers(answers_map)
                st.success("Uploaded answers loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")

        if st.session_state.last_saved:
            st.markdown(f'<span class="save-info">Last local save: {st.session_state.last_saved}</span>', unsafe_allow_html=True)

    # ── Guard ──────────────────────────────────────────────────────────────────
    if not filtered_indices:
        st.info("No traces match current filter.")
        st.stop()

    idx = st.session_state.current_idx
    if idx not in filtered_indices:
        idx = filtered_indices[0]
        st.session_state.current_idx = idx

    trace    = traces[idx]
    code     = trace["code"]
    goal     = trace.get("goal", "")
    turns    = trace.get("turns", [])
    existing = answers_map.get(code, {})

    # ── Header (blinded — only T-code) ───────────────────────────────────────
    fi       = filtered_indices.index(idx)
    st.markdown(f"""
<div class="peer-header">
<strong>Trace {fi+1} of {len(filtered_indices)} (filtered)</strong><br>
🏷️ <strong>Code: {code}</strong> &nbsp;|&nbsp;
💬 <strong>Turns: {len(turns)}</strong>
</div>
""", unsafe_allow_html=True)

    # ── Goal box ──────────────────────────────────────────────────────────────
    st.markdown("**🎯 Task Goal:**")
    st.markdown(f'<div class="goal-box">{goal}</div>', unsafe_allow_html=True)

    # ── Turns ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 Conversation Turns")

    if not turns:
        st.warning("No turns in this trace.")
    else:
        for t in turns:
            n       = t.get("turn_id", "?")
            speaker = t.get("speaker", "Agent")
            content = t.get("content", "")
            char_n  = len(content)
            label   = f"Turn {n} — **{speaker}** ({char_n:,} chars)"

            if char_n > 500:
                with st.expander(label, expanded=False):
                    st.markdown(content)
            else:
                st.markdown(f"**Turn {n} — {speaker}**")
                st.markdown(content)
                st.markdown('<hr style="border:0;border-top:1px solid #2d3748;margin:4px 0">', unsafe_allow_html=True)

    # ── Annotation form ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✏️ Your Annotation")

    ex_fo   = str(existing.get("failure_occurred", "")).strip()
    ex_fm   = str(existing.get("failure_mode", "")).strip()
    ex_ons  = str(existing.get("onset_turn", "")).strip()
    ex_note = str(existing.get("notes", "")).strip()

    if ex_fo in ("nan", "NaN", ""):   ex_fo   = ""
    if ex_fm in ("nan", "NaN", ""):   ex_fm   = ""
    if ex_ons in ("nan", "NaN", ""):  ex_ons  = ""
    if ex_note in ("nan", "NaN", ""): ex_note = ""

    fo_options  = ["", "Yes", "No", "Not sure"]
    fm_options  = ["", "FM-2.3", "FM-2.4", "FM-2.6", "None / Not sure"]

    fo_idx = fo_options.index(ex_fo)  if ex_fo in fo_options  else 0
    fm_idx = fm_options.index(ex_fm)  if ex_fm in fm_options  else 0

    max_turn = max(len(turns) - 1, 0)
    try:
        ex_ons_int = int(float(ex_ons)) if ex_ons else 0
    except:
        ex_ons_int = 0

    with st.form(key=f"peer_form_{idx}"):
        col1, col2 = st.columns(2)
        with col1:
            new_fo = st.selectbox("Did a failure occur?", fo_options, index=fo_idx)
        with col2:
            new_fm = st.selectbox("What type of failure?", fm_options, index=fm_idx)

        new_onset = st.number_input(
            "At which turn did the failure first become visible? (0 if none/unsure)",
            min_value=0,
            max_value=max(max_turn, 0),
            value=min(ex_ons_int, max(max_turn, 0)),
            step=1,
        )
        new_note = st.text_area("Notes (optional)", value=ex_note, height=90,
                                 placeholder="Brief description of what you observed…")

        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            prev_btn = st.form_submit_button("⬅ Previous", use_container_width=True)
        with btn_col2:
            save_btn = st.form_submit_button("💾 Save & next", use_container_width=True, type="primary")
        with btn_col3:
            skip_btn = st.form_submit_button("⏭ Skip →", use_container_width=True)

    # ── Form actions ──────────────────────────────────────────────────────────
    fi = filtered_indices.index(idx)

    if save_btn:
        answers_map[code] = {
            "code":             code,
            "failure_occurred": new_fo,
            "failure_mode":     new_fm,
            "onset_turn":       str(int(new_onset)),
            "notes":            new_note.strip(),
        }
        save_answers(answers_map)
        st.session_state.last_saved = datetime.datetime.now().strftime("%H:%M:%S")
        if fi + 1 < len(filtered_indices):
            st.session_state.current_idx = filtered_indices[fi + 1]
        st.rerun()

    if skip_btn:
        if fi + 1 < len(filtered_indices):
            st.session_state.current_idx = filtered_indices[fi + 1]
        st.rerun()

    if prev_btn:
        if fi > 0:
            st.session_state.current_idx = filtered_indices[fi - 1]
        st.rerun()


if __name__ == "__main__":
    main()
