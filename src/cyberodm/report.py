from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def chart_outcome_heatmap(latest: pd.DataFrame, out: Path):
    # Bar chart per outcome (acts as heatmap proxy)
    plt.figure()
    latest.plot(x="name", y="outcome_score", kind="bar")
    plt.title("Outcome Scores (latest)")
    plt.xlabel("Outcome")
    plt.ylabel("Score (0..1)")
    plt.tight_layout()
    plt.savefig(out / "outcome_scores_latest.png")
    plt.close()

def chart_value_trend(val: pd.DataFrame, out: Path):
    # Target line: approximate using mean target for KPIs named like Availability or SLA if present
    import pandas as _pd
    _base = out.parent
    _kpis = _pd.read_csv(_base / 'data' / 'kpis.csv') if (_base / 'data' / 'kpis.csv').exists() else None
    _sla = None
    if _kpis is not None and 'kpi_name' in _kpis.columns:
        _sla = _kpis[_kpis['kpi_name'].str.contains('SLA|Availability', case=False, na=False)]
    _target_series = None
    if _sla is not None and not _sla.empty:
        _target_series = _sla.groupby('period')['target'].mean().reset_index().rename(columns={'target':'target_mean'})

    trend = val.groupby("period")["value_realization_usd"].sum().reset_index()
    if _sla is not None and _target_series is not None:
        trend = trend.merge(_target_series, on='period', how='left')
    plt.figure()
    plt.plot(trend["period"], trend["value_realization_usd"], marker="o")
    if 'target_mean' in trend.columns:
        plt.plot(trend['period'], trend['target_mean'], linestyle='--')
    plt.title("Value Realization Trend ($)")
    plt.xlabel("Period")
    plt.ylabel("USD")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out / "value_trend.png")
    plt.close()

def chart_okr_progress(okr: pd.DataFrame, outcomes: pd.DataFrame, out: Path):
    latest = (okr.sort_values("period").groupby("outcome_id").tail(1))
    latest = latest.merge(outcomes[["outcome_id","name"]], on="outcome_id", how="left")
    plt.figure()
    latest.plot(x="name", y="okr_progress_pct", kind="bar")
    plt.title("OKR Progress (latest %)")
    plt.xlabel("Outcome")
    plt.ylabel("%")
    plt.tight_layout()
    plt.savefig(out / "okr_latest.png")
    plt.close()

def write_report(base: Path):
    out = base / "outputs"
    combined = pd.read_csv(out / "outcome_scores.csv")
    latest = pd.read_csv(out / "outcome_scores_latest.csv")
    okr = pd.read_csv(out / "okr_progress.csv")
    val = pd.read_csv(out / "value_realization.csv")
    inits = pd.read_csv(out / "initiatives_snapshot.csv")

    chart_outcome_heatmap(latest, out)
    chart_value_trend(val, out)
    # Need outcomes for names in okr chart
    outcomes = latest[["outcome_id","name"]].drop_duplicates()
    chart_okr_progress(okr, outcomes, out)

    # Top gaps: lowest outcome scores
    top_gaps = latest.sort_values("outcome_score").head(5)

    lines = []
    lines.append("# CyberODM — Outcome‑Driven Metrics Report\n")
    lines.append("## Snapshot (latest)\n")
    lines.append(latest[["outcome_id","name","owner","outcome_score","rag","okr_progress_pct","value_realization_usd"]].to_markdown(index=False))
    lines.append("\n## Value Realization (by period)\n")
    lines.append(val.to_markdown(index=False))
    lines.append("\n## Top 5 Gaps\n")
    lines.append(top_gaps[["outcome_id","name","owner","outcome_score","okr_progress_pct"]].to_markdown(index=False))
    lines.append("\n## Charts\n")
    lines.append("![Outcome Scores](outcome_scores_latest.png)")
    lines.append("![Value Trend](value_trend.png)")
    lines.append("![OKR Progress](okr_latest.png)\n")
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")

def build(base: Path):
    write_report(base)


def chart_sla_overlay(out: Path):
    import pandas as pd
    base = out.parent
    if not (base / 'data' / 'kpis.csv').exists():
        return
    k = pd.read_csv(base / 'data' / 'kpis.csv')
    k = k[k['kpi_name'].str.contains('SLA|Availability', case=False, na=False)]
    if k.empty:
        return
    agg = k.groupby('period')[['value','target']].mean().reset_index()
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(agg['period'], agg['value'], marker='o')
    plt.plot(agg['period'], agg['target'], linestyle='--')
    plt.title('SLA/SLO Overlay')
    plt.xlabel('Period')
    plt.ylabel('Percent')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out / 'sla_overlay.png')
    plt.close()
