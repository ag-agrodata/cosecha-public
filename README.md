# 🫐 berries-cosecha · Blueberry Harvest Productivity (public, anonymized)

Operational dashboard + prescriptive weekly planner for greenhouse blueberry harvest.
Python · Polars · Streamlit · Plotly.

**Public anonymized release:** every published aggregate satisfies k ≥ 5 unique workers and
≥ 10 records per cell; no direct identifiers; no block-level data; kg/h top-coded at p99.5.
Client identity and commercial references omitted for confidentiality.

## Run locally
```bash
pip install -r requirements.txt
streamlit run src/berrix/app_cosecha_public.py
```

# Contents

- src/berrix/app_cosecha_public.py — public dashboard (7 tabs; planner in demo mode).
- src/berrix/forecaster.py — forecast zoo (mov_avg / seasonal / holt / theta) + holdout backtest.
- data/public/ — k-anonymized dataset (6 parquet tables + README + validation report).
- docs/public/ — methodology docs (ES) · docs/public/en/ (EN).

# Methodology highlights

- Crowding by variety (β): kg_h_senior(s) = max(a·(1−β·s), 0.70·a).
- Mixed productivity: kg_h_mixto = (1−s)·kg_h_senior + s·kg_h_nuevo.
- Forecast selection by holdout backtest (WMAPE) with 80% prediction intervals.
- HR comparator: hire vs overtime vs mixed, stress priced in lost hours → COP and kg.

---
Prepared by Andrés Gómez · Agri-industrial Data Analyst.
