# CyberODM — Outcome‑Driven Metrics

![Banner](assets/cyberodm-banner.png)

**CyberODM** turns cybersecurity into business outcomes. Define outcomes (e.g., **Risk Reduction**, **Regulatory Confidence**, **Operational Resilience**), map KPIs and initiatives to those outcomes, and generate executive‑ready reports: **outcome scores**, **value realization**, **OKR progress**, **trends**, and **gap heatmaps**.

## Highlights
- Outcome model with **weights**, **targets**, **value hypotheses** (cost avoidance, revenue protection, efficiency)
- Metrics ingestion for **leading & lagging indicators** (MTTD, MTTR, incidents, coverage, control effectiveness, SLA)
- Rollups: **Outcome Score**, **Value Realization $**, **OKR progress %**
- Charts: outcome heatmap, value trend, OKR progress, initiative burndown, benefit waterfall
- CLI: `cyberodm compute` → compute scores; `cyberodm report` → charts & Markdown summary

## Quickstart
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -e .

cyberodm compute --config config.yml
cyberodm report
```
See `outputs/` for CSVs, charts (PNG), and `report.md`.

## Inputs
- `data/outcomes.csv` — list of outcomes with weights & OKR targets
- `data/kpis.csv` — metrics per period (leading/lagging) & mapping to outcomes
- `data/initiatives.csv` — initiatives with planned benefits & status
- `data/value_map.csv` — value hypothesis & $/unit for each KPI
- `config.yml` — thresholds, periods, scoring weights

## Outputs
- `outputs/outcome_scores.csv` — score per outcome & period
- `outputs/value_realization.csv` — benefit $ per outcome & period
- `outputs/okr_progress.csv` — OKR completion by outcome
- Charts: heatmap, value trend, OKR progress, waterfall
- `outputs/report.md` — exec summary, top gaps, calls to action

MIT License.


## Dashboard (Streamlit)
```bash
pip install -e .
streamlit run app/streamlit_app.py
```

## Export to PowerPoint
```bash
pip install python-pptx
python scripts/export_pptx.py --title "CyberODM Exec Update Q2 2025" --out outputs/CyberODM-Exec-Report.pptx
```

## GitHub Action — Auto Rebuild & Release
A workflow (`.github/workflows/release-on-data-change.yml`) rebuilds charts whenever `data/` changes on `main`, and publishes a tagged release with artifacts.
