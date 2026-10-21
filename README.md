[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<div align="center">

<img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez" width="180"/>

# 🫐 Blueberry Harvest Productivity — Public Release

**Prescriptive weekly planner for greenhouse blueberry harvest.**<br/>
Python · Polars · Streamlit · Plotly · k-anonymized public dataset.

[![Streamlit](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit)](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/)
[![License](https://img.shields.io/badge/license-MIT-1B4332)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?logo=python)](requirements.txt)

*Elaborated by **Andrés Gómez** · Agri-industrial Data Analyst*

[🚀 Live Demo](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/) · [📖 Docs](docs/public/en/) · [📊 Internal spec](docs/public/en/cerebro-cosecha-public.md)

</div>

---

## Overview

This repository contains the **public anonymized release** of an operational dashboard built for a greenhouse blueberry grower. It turns the production forecast into work hours, headcount shortfalls and cost, and measures forecast accuracy week after week.

The companion internal version (not published) drives the **Thursday 9:00 am planning meeting** of the Production, Harvest and HR teams.

> **Anonymization:** every published aggregate satisfies k ≥ 5 unique workers and ≥ 10 records per cell. Client identity, worker IDs, block-level data and exact dates are omitted for confidentiality. See the [Statistical Decisions](docs/public/en/decisiones-estadisticas-cosecha-public.md) for the full spec.

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
Agri-industrial Data Analyst<br/>

[🌐 Portfolio](https://github.com/ag-agrodata) · [📧 Contact](mailto:afgomez.agroindustrial@gmail.com)

</div>
