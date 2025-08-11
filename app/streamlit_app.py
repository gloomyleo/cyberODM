import streamlit as st
import pandas as pd
from pathlib import Path
from cyberodm.compute import compute as do_compute
from cyberodm.report import build as do_build

st.set_page_config(page_title="CyberODM — Outcome-Driven Metrics", layout="wide")

st.title("CyberODM — Outcome‑Driven Metrics Dashboard")
role = st.radio("Role", ["CISO","Ops"], horizontal=True)

st.caption("Filters • Drilldowns • CSV Upload • Value Realization • OKR Progress")

base = Path(".")

with st.sidebar:
    st.header("Upload CSVs (optional)")
    upl_outcomes = st.file_uploader("outcomes.csv", type=["csv"])
    upl_kpis = st.file_uploader("kpis.csv", type=["csv"])
    upl_valmap = st.file_uploader("value_map.csv", type=["csv"])
    upl_inits = st.file_uploader("initiatives.csv", type=["csv"])

    if st.button("Use uploaded data"):
        if upl_outcomes: (base / "data" / "outcomes.csv").write_bytes(upl_outcomes.getbuffer())
        if upl_kpis: (base / "data" / "kpis.csv").write_bytes(upl_kpis.getbuffer())
        if upl_valmap: (base / "data" / "value_map.csv").write_bytes(upl_valmap.getbuffer())
        if upl_inits: (base / "data" / "initiatives.csv").write_bytes(upl_inits.getbuffer())
        st.success("Uploaded data saved. Click 'Recompute'.")

    st.header("Actions")
    if st.button("Recompute"):
        do_compute(base)
        do_build(base)
        st.success("Rebuilt metrics and report.")

# Load outputs (compute if missing)
if not (base / "outputs" / "outcome_scores.csv").exists():
    do_compute(base)
    do_build(base)

latest = pd.read_csv(base / "outputs" / "outcome_scores_latest.csv")
okr = pd.read_csv(base / "outputs" / "okr_progress.csv")
val = pd.read_csv(base / "outputs" / "value_realization.csv")
inits = pd.read_csv(base / "outputs" / "initiatives_snapshot.csv")

# Filters
cols = st.columns(3)
with cols[0]:
    outcome_filter = st.multiselect("Outcomes", options=sorted(latest["name"].unique()), default=list(sorted(latest["name"].unique())))
with cols[1]:
    rag_filter = st.multiselect("RAG", options=["Red","Amber","Green"], default=["Red","Amber","Green"])
with cols[2]:
    owner_filter = st.multiselect("Owners", options=sorted(latest["owner"].unique()), default=list(sorted(latest["owner"].unique())))

flt = latest[latest["name"].isin(outcome_filter) & latest["rag"].isin(rag_filter) & latest["owner"].isin(owner_filter)]

st.markdown("---")
if role == "CISO":
    st.subheader("CISO View — Outcomes & Value")
    st.metric("Total Value (latest period)", f"${val.groupby('period')['value_realization_usd'].sum().tail(1).values[0]:,.0f}")
    st.metric("Outcomes Green", int((latest['rag'] == 'Green').sum()))
    st.metric("At Risk (Red/Amber)", int((latest['rag'] != 'Green').sum()))
else:
    st.subheader("Ops View — KPIs & Initiatives")
    import pandas as pd
    # Pull most recent period KPIs from outputs by merging outcome_id from latest
    # (source KPIs are in data/kpis.csv)
    raw_kpis = pd.read_csv(base / 'data' / 'kpis.csv')
    most_recent = raw_kpis['period'].dropna().unique()
    most_recent = sorted(most_recent)[-1] if len(most_recent) else None
    if most_recent:
        k = raw_kpis[raw_kpis['period'] == most_recent]
        st.write(f"KPIs for {most_recent}")
        st.dataframe(k)
    st.write("Initiatives")
    st.dataframe(inits)

st.markdown('---')
st.subheader('Final View — Executive Summary')
cols = st.columns(3)
with cols[0]:
    st.image(str(base / 'outputs' / 'outcome_scores_latest.png'))
with cols[1]:
    st.image(str(base / 'outputs' / 'value_trend.png'))
with cols[2]:
    st.image(str(base / 'outputs' / 'okr_latest.png'))
st.subheader("Snapshot (Latest)")
st.dataframe(flt[["outcome_id","name","owner","outcome_score","rag","okr_progress_pct","value_realization_usd"]])

# Charts: read generated images if present
import base64

def img_tag(p: Path, caption: str):
    if p.exists():
        st.markdown(f"**{caption}**")
        st.image(str(p))
    else:
        st.info(f"Chart missing: {p.name}. Run 'Recompute' in the sidebar.")

img_tag(base / "outputs" / "outcome_scores_latest.png", "Outcome Scores")
img_tag(base / "outputs" / "value_trend.png", "Value Realization Trend")
img_tag(base / "outputs" / "okr_latest.png", "OKR Progress (Latest)")

st.subheader("Initiatives")
st.dataframe(inits)

st.markdown("---")
st.markdown("Download the full report:")
if (base / "outputs" / "report.md").exists():
    st.download_button("Download report.md", data=(base / "outputs" / "report.md").read_bytes(), file_name="report.md")
