[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<div align="center">

<img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez/Agrodata" width="180"/>

# 🫐 Blueberry Harvest Productivity · Berrix
### Public Release

**Prescriptive weekly planner for greenhouse blueberry harvest.**<br/>
Python · Polars · Streamlit · Plotly · k-anonymized public dataset.

[![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/) [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/) [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)

*Elaborated by **Andrés Gómez** · Agribusiness Data Analyst*

[🚀 Live Demo](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/) · [📖 Docs](docs/public/en/) · [📊 Internal spec](docs/public/en/cerebro-cosecha-public.md)

</div>

---

## 2-Minute Summary

A prescriptive weekly planner that translates blueberry harvest forecasts into work hours, headcount gaps, and operational costs. It turns historical productivity data into actionable forecasts and measures accuracy week over week. Built on real anonymized data (k ≥ 5 workers, ≥ 10 records per cell), with a public demo and documented statistical methodology.

> **Legal notice:** Published aggregates meet strict k-anonymity standards. They do not allow the identification of individual workers, specific blocks, or the client's identity. See the [Statistical Decisions](docs/public/en/decisiones-estadisticas-cosecha-public.md) for the full spec.

## The Problem

Production and HR teams in agribusiness often plan harvests using static averages, underestimating the effects of the learning curve, accumulated fatigue, and seasonality. When planning is reactive, it leads to unplanned overtime costs, operational stress, and productivity losses.

The question this project answers: How do we turn historical operational data into a prescriptive, fair, and efficient harvest plan?

## What this project demonstrates

- **Modeling operational reality:** Translating agronomic concepts (learning curve, crowding effect) into executable mathematical formulas in Python and Polars.
- **Explainable forecasting over "black boxes":** Implementing a "forecast zoo" (moving average, seasonal, Holt, Theta) that compete on WMAPE, prioritizing interpretability over ML complexity.
- **Decision-making under uncertainty:** Calculating 80% confidence intervals and break-even scenarios (overtime vs. hiring) to back HR decisions with data, not intuition.
- **Rigorous governance and anonymization:** Applying k-anonymity, suppression, and top-coding to publish sensitive operational data without compromising worker privacy.
- **End-to-end data lifecycle:** From ERP record extraction to an interactive Streamlit dashboard with an ES/EN toggle and lineage documentation.

## Recommendations and Impact

> **Transparency note:** Impact figures (costs, kg, hours) are presented as estimated ranges under NDA. Exact figures are confidential and must be validated internally before use in presentations.

### 1 · Optimize workforce mix (Mixed vs. Overtime)
The HR comparator identifies the break-even point where hiring new staff accumulates less cost than paying fatigued overtime. The recommendation is to use this threshold to approve temporary hiring requests before the hour gap becomes unsustainable.

### 2 · Early intervention in newcomer cohorts
The "Learning curve" view identifies when a cohort stagnates. The operational recommendation is to assign mentors or adjust workloads within the first 4 weeks, before productivity drops below 70% of the senior target.

### 3 · Dynamic goal adjustment by seasonality
The seasonality view reveals peaks of operational stress. The recommendation is to adjust expected kg/hour targets during critical floral or climatic windows, avoiding penalizing the team for unmodeled external factors.

## Live Demo

**🔗 [Open the public dashboard →](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/)**

Seven tabs, ES/EN toggle, all data k-anonymized:

| Tab | Audience | What it shows |
|-----|----------|---------------|
| 00 · Methodology | Analyst | Governance, anonymization rules, data lineage |
| 01 · Capacity | Production | kg/h by farm × system × variety (monthly) |
| 02 · Crowding | HR / Analyst | Effect of newcomers on experienced workers (β) |
| 03 · Learning curve | HR | Cohort-based progression to senior |
| 04 · Seasonality | Production | Weekly rhythm, harvest frequency, stress risk |
| 05 · Planner *(demo)* | Production / HR | Prescriptive planner with synthetic base team |
| 06 · Models & Backtest | Analyst | Forecast zoo + holdout selection + intervals |

## Methodology Highlights

### Productivity model
- **Crowding by variety (β):** `kg_h_senior(s) = max(a·(1−β·s), 0.70·a)`
- **Mixed productivity:** `kg_h_mixed = (1−s)·kg_h_senior + s·kg_h_new`
- The newcomer share `s` is an **output** of the current state, never an input.

### Forecast zoo (Step 3a)
Four explainable methods compete on holdout WMAPE over the last 4 weeks:

| Method | Captures | Requires |
|--------|----------|----------|
| `mov_avg` | Baseline | 6 observations |
| `seasonal` | Annual shape | 52 + 4 observations |
| `holt` | Trend | ≥ 2 |
| `theta` | Trend + smoothed level | ≥ 3 |

80% prediction intervals: `ŷ ± 1.28·σ·√h`.

### HR comparator (Step 3b)
For each farm with an hours gap, three options compared side by side:

- **A · Overtime** (fatigue = 95%)
- **B · Hire N people** (stress priced in lost hours → COP and kg)
- **C · Mixed** (overtime to cap + hire the remainder)

Break-even: week from which hiring accumulates less cost than overtime for the same kg.

## Repository Structure

```
cosecha-public/
├── src/berrix/
│   ├── app_cosecha_public.py     # Streamlit dashboard (ES/EN)
│   ├── forecaster.py             # Forecast zoo + holdout backtest
│   └── assets/ag6.svg            # Brand logo
├── data/public/                  # k-anonymized dataset (6 parquet tables)
│   ├── hechos_semana.parquet
│   ├── hechos_mes_variedad.parquet
│   ├── curva_public.parquet
│   ├── crowding_public.parquet
│   ├── params_public.parquet
│   ├── estacionalidad_public.parquet
│   ├── README.md
│   └── validacion.txt
├── docs/public/                  # ES methodology docs
│   ├── cerebro-cosecha-public.md
│   ├── decisiones-estadisticas-cosecha-public.md
│   ├── guia-comite-cosecha-public.html
│   └── en/                       # EN translations
├── .streamlit/config.toml
└── requirements.txt
```
> 👨🏻‍💻 **Technical note:** `berrix` is the internal package name (a contraction of berries + *analytics) that houses the analytical engine and forecasting modules for this project suite. It is kept as a namespace to maintain architectural coherence with the companion repository (berries-dashboard).

## Run Locally

```bash
git clone https://github.com/ag-agrodata/cosecha-public.git
cd cosecha-public
pip install -r requirements.txt
streamlit run src/berrix/app_cosecha_public.py
```

Open `http://localhost:8501`. The toggle **ES | EN** is at the top-right of the dashboard.

## Anonymization Rules

Every published cell satisfies:

1. **k ≥ 5** unique workers per cell
2. **≥ 10** records (hours) per cell
3. **No direct identifiers** (worker IDs and names removed)
4. **No indirect identifiers** (blocks aggregated to farm level)
5. **Temporal jittering** (dates rounded to ISO week)
6. **Top-coding** at p99.5 for kg/h
7. **No NDA correlation** (commercial/financial domains excluded)

Validation report: [`data/public/validacion.txt`](data/public/validacion.txt).

## Data Lineage

- Source: operational ERP records, anonymized at origin by the client.
- Coverage: 2022-12 → 2025-05, 118,329 hourly records.
- Processing: Polars pipelines → k-anonymized parquet tables.

The internal pipelines (`build_public.py`, `validar_public.py`) are **not** part of this release, as they require access to the granular (non-public) data.

## Companion project: End-to-End Agribusiness Analytics

This repository is part of a broader ecosystem. It pairs with [berries-dashboard](https://github.com/ag-agrodata/berries-dashboard) to cover the full business cycle: while this tool solves operational bottlenecks (yield, labor, and cost), `berries-dashboard` translates B2B sales data into strategic actions for the commercial committee.

## Tech Stack

- **Language:** Python 3.12 / 3.13
- **Data:** [Polars](https://pola.rs/) (lightning-fast DataFrames)
- **UI:** [Streamlit](https://streamlit.io/) (dashboard + interactive widgets)
- **Charts:** [Plotly](https://plotly.com/python/) (interactive Plotly Express + Graph Objects)
- **Forecasting:** custom NumPy implementations (no ML dependencies)
- **Hosting:** Streamlit Community Cloud

## License

This project uses a **dual license**:

- **Code** (`src/`, `.streamlit/`, `requirements.txt`): [MIT License](LICENSE).
- **Data** (`data/public/`): [Data Use Agreement](LICENSE) — non-commercial,
  no re-identification, attribution required.
- **Documentation** (`docs/`, READMEs): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> ⚠️ The k-anonymized datasets are released for demonstration purposes.
> Any attempt to re-identify individuals or link the data to a specific
> organization is expressly prohibited. See the [LICENSE](LICENSE) file
> for full terms.

---

<div align="center">

**Andrés Gómez**<br/>
Agribusiness Data Analyst<br/>
"I turn the complexity of the field into data-driven decisions."

[🌐 Portfolio](https://github.com/ag-agrodata) · [📧 Contact](mailto:afgomez.agroindustrial@gmail.com)

</div>
