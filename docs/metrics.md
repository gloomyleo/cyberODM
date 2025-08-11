# Data Model & Scoring

## outcomes.csv
- outcome_id, name, owner, weight (0–1), okr_target_pct (0–100)

## kpis.csv
- outcome_id, kpi_id, kpi_name, period (YYYY-Qn), kind (leading|lagging),
  value, target, direction (up_is_good|down_is_good)
- Examples: MTTD (down_is_good), MTTR (down_is_good), Incident_Count (down_is_good),
  Coverage_Pct (up_is_good), Effectiveness_Pct (up_is_good), SLA_Pct (up_is_good)

## value_map.csv
- kpi_id, hypothesis (avoidance|efficiency|revenue_protect), unit_value_usd
- Converts KPI movement vs. baseline/target into $ value for the period

## initiatives.csv
- init_id, outcome_id, name, owner, start, end, status (planned|active|done), expected_value_usd

## Scoring
- Normalize KPI to 0–1 toward its target (respecting direction).
- Outcome Score per period = mean( leading KPIs, lagging KPIs ) × outcome weight
- OKR progress per outcome = averaged ratio(actual vs target) × 100

**RAG thresholds** (configurable)
- Red < 0.5, Amber 0.5–0.75, Green ≥ 0.75
