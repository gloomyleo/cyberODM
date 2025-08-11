from __future__ import annotations
import pandas as pd
import yaml
from pathlib import Path
from .utils import norm_toward_target, rag

def load_inputs(base: Path):
    cfg = yaml.safe_load((base / "config.yml").read_text())
    outcomes = pd.read_csv(base / "data" / "outcomes.csv")
    kpis = pd.read_csv(base / "data" / "kpis.csv")
    valmap = pd.read_csv(base / "data" / "value_map.csv")
    inits = pd.read_csv(base / "data" / "initiatives.csv")
    return cfg, outcomes, kpis, valmap, inits

def compute(base: Path):
    cfg, outcomes, kpis, valmap, inits = load_inputs(base)
    red = cfg["rag_thresholds"]["red"]
    amber = cfg["rag_thresholds"]["amber"]

    # Normalize KPI toward target (respecting direction)
    kpis["score_norm"] = [
        norm_toward_target(v, t, d) for v, t, d in zip(kpis["value"], kpis["target"], kpis["direction"])
    ]
    # Leading/Lagging split per outcome & period
    agg = kpis.groupby(["outcome_id","period","kind"])["score_norm"].mean().reset_index()
    pivot = agg.pivot_table(index=["outcome_id","period"], columns="kind", values="score_norm", fill_value=0).reset_index()
    if "leading" not in pivot.columns: pivot["leading"] = 0.0
    if "lagging" not in pivot.columns: pivot["lagging"] = 0.0

    # Combine using weights
    w_lead = cfg["weights"]["leading"]
    w_lag = cfg["weights"]["lagging"]
    pivot["kpi_score"] = w_lead*pivot["leading"] + w_lag*pivot["lagging"]

    # Join outcome weights & OKR targets
    outw = outcomes[["outcome_id","name","owner","weight","okr_target_pct"]]
    combined = pivot.merge(outw, on="outcome_id", how="left")
    combined["outcome_score"] = combined["kpi_score"] * combined["weight"]
    combined["rag"] = [rag(s, red, amber) for s in combined["outcome_score"]]

    # OKR progress: average (actual/target) of KPIs marked with target; approximate using kpi_score toward 100%
    combined["okr_progress_pct"] = (combined["kpi_score"] * 100).clip(0, 100)

    # Value realization: compare KPI to target and translate delta into $ using value_map
    # Simple model: benefit = unit_value_usd * (improvement_ratio)
    kmerge = kpis.merge(valmap, on="kpi_id", how="left")
    def improvement_ratio(row):
        v, t, dirn = row["value"], row["target"], row["direction"]
        if pd.isna(row["unit_value_usd"]): return 0.0
        if dirn == "up_is_good":
            if t == 0: return 0.0
            return max(0.0, (v - (t if v>t else v)) / t)  # benefit only when exceeding target? keep simple
        else:  # down_is_good
            if v <= t: return (t - v) / (t+1e-9)  # improvement below target
            return 0.0
    kmerge["improve_ratio"] = kmerge.apply(improvement_ratio, axis=1)
    kmerge["benefit_usd"] = (kmerge["unit_value_usd"].fillna(0) * kmerge["improve_ratio"]).fillna(0)
    val = kmerge.groupby(["outcome_id","period"])["benefit_usd"].sum().reset_index().rename(columns={"benefit_usd":"value_realization_usd"})

    combined = combined.merge(val, on=["outcome_id","period"], how="left").fillna({"value_realization_usd":0})

    # Latest snapshot per outcome
    latest = (combined.sort_values("period")
                     .groupby("outcome_id")
                     .tail(1))

    # Save outputs
    out = base / "outputs"
    out.mkdir(exist_ok=True)
    combined.to_csv(out / "outcome_scores.csv", index=False)
    latest.to_csv(out / "outcome_scores_latest.csv", index=False)

    okr = combined[["outcome_id","period","okr_progress_pct"]].copy()
    okr.to_csv(out / "okr_progress.csv", index=False)

    val.to_csv(out / "value_realization.csv", index=False)

    # Also keep initiatives as-is for reporting
    inits.to_csv(out / "initiatives_snapshot.csv", index=False)

    return {
        "combined": combined,
        "latest": latest,
        "okr": okr,
        "value": val,
        "inits": inits
    }
