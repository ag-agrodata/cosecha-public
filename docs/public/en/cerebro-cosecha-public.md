# Harvest Brain · Operations
> **Public anonymized version** · no client identifiers · Prepared by Andrés Gómez · Agri-industrial Data Analyst.
> Single source of truth for the operational harvest-productivity project.
> Strictly separate from any commercial engagement under NDA.
> Last update: close of Step 3 (forecaster + HR comparator) + Tab 06 (budget & KPIs).

## 0 · Project identity
- **Name:** Cosecha (Operations).
- **Type:** Operational dashboard + prescriptive harvest planner for blueberries.
- **Client:** Colombian grower (source data anonymized at origin).
- **Stack:** Python 3.13 · uv · Polars · Streamlit 1.65 · Plotly · NumPy.
- **Confidentiality:** the dataset is anonymized; the dashboard never singles out or profiles
  workers (all talent aggregates are reported by cohort or category). Client identity and
  commercial references are omitted from all public artifacts.

## 1 · Business context
- Greenhouse blueberry cultivation; climate impact is negligible (controlled environment).
- Two farms (`Predio_1`, `Predio_2`); 28 blocks/greenhouses; multiple growing systems and
  varieties coexisting within a block.
- Harvest is the critical operation: ripe fruit does not wait; backlog fruit (*látigo*)
  degrades quality and shelf life.
- Operational policy: "every block is always harvested", fulfilled **cumulatively across the
  week** (multiple visits), not in a single event.

## 2 · Weekly operational flow
1. **Wednesday:** close of harvest tracking.
2. **Thursday 9:00 am:** planning meeting (Production + Harvest). Inputs: pending fruit,
   last-harvest date per block, harvest frequency by variety, backlog, available labor,
   projected vs. harvested kg.
3. **Day by day:** route review; postponements due to ripeness (Agronomy informs) or labor
   shortage (re-prioritized FIFO).
4. **Saturday:** estimate of pending fruit; if applicable, Saturday/Sunday overtime and
   priority handling in packing/dispatch.

## 3 · Roles and audiences
| Role | Uses | Purpose |
|---|---|---|
| Production / Harvest | Tabs 04, 05 | Route, kg projection, compliance |
| HR | Tab 05 (Sections 4, 7) | Shortfalls, hire-vs-overtime, stress costing |
| Management / Direction | Tab 06 | Budget, cost, strategic alerts |
| Analyst | Tabs 00–03, backtest | Data quality, capacity, crowding, learning curve |

## 4 · Data sources and lineage
- **Primary input:** ERP CSV (20 base columns). No APIs or connectors: manual download →
  Streamlit upload.
- **History:** `data/processed/cosecha_model.parquet` (38 columns, 2022-12 → 2025-05).
- **Aggregates:** capacity, crowding (+binned), crowding correlation, learning curve,
  achievement history, variety betas, variety simulator parameters, new→senior threshold,
  monthly & weekly seasonality, harvest frequency, frequency-vs-stress.
- **Plan ledger:** `data/plans/*.parquet` (saved plans with metadata; never touches the
  operational base).
- **Diagnostics:** block-structure diagnostic; demo ERP CSV for testing.

## 5 · Operational glossary
- **Combination:** block × growing system × variety. The minimum planning unit.
- **Base team:** fixed headcount per farm, mobile across blocks (D02: 43 workers with ≥25%
  attendance).
- **New / Senior:** new = ≤4 active weeks (S08); senior = reaches the learning-curve asymptote.
- **Newcomer share (s):** fraction of **hours** worked by new harvesters in a combination.
  It is an **output** of the current state, never an input.
- **Crowding (β):** the drag that newcomers impose on seniors in sensitive varieties (D01).
- **Backlog (*látigo*):** ripe fruit left unharvested beyond its window; re-prioritized FIFO.
- **FTE:** full-time equivalent = hours ÷ ordinary weekly hours.
- **Hour types:** ORDINARY / OVERTIME / SUNDAY, with legal surcharges (daytime overtime 125%,
  Sunday 200%).

## 6 · Consolidated decisions
| ID | Decision | Rationale |
|---|---|---|
| D01 | Crowding depends on the **variety**, not the farm. Tolerant β=0 (16,19,1,20,10,24); sensitive 9 (0.38), 4 (0.26), 15 (0.13). Formula `kg_h_senior(s)=a·(1−β·s)`, floor `0.70·a` | Statistical evidence F4c |
| D02 | Base group = 43 workers, mobile across farms | F5b |
| D03 | Budget = 2,000 kg/week (empirical rounding of 100 t/year) | Business criterion |
| D04 | Overtime is an **output** of the simulator, not an input | Avoids planning bias |
| D07 | Variety_4 is delicate (pests / over-softening on plant); its low kg/h is agronomic | Agronomic context |
| D09 | HR comparator (hire vs overtime vs mixed) with stress priced in lost hours → COP and kg | Step 3 close |
| D10 | Operational unit = combination (block×system×variety), not the whole block | F6a: real coverage 44–66% per event |
| D11 | Team fixed per farm, mobile across blocks; cross-farm moves only exceptional | Operational interview |
| D12 | Newcomer share = output of the current state | Avoids assuming headcount composition |
| D13 | Disabling an element applies from the chosen week onward; history is preserved | Traceability |
| D14 | Forecast chosen by backtest over a zoo (mov_avg / seasonal / holt / theta) | Step 3a |

> Note: IDs D05, D06 and D08 were reserved/retired in earlier iterations and are not reused.

## 7 · Assumptions and limitations
| ID | Assumption | Value |
|---|---|---|
| S04 | Overtime yield (fatigue) | 95%, configurable |
| S05 | Staffing-agency surcharge on hiring | +15%, configurable |
| S06 | Overtime split | Daytime only (125%) by default |
| S07 | Break-even horizon | 8 weeks, configurable |
| S08 | "New" threshold | ≤4 active weeks |
| S09 | Default kg/h for combinations without history | 3.5, configurable |

- **Known limitations:** no ripeness data; no climate impact (greenhouse); capture gaps
  Jan–Apr 2023-2024 (corrected with 2025); future turnover not predictable (57% of drop-offs
  coincide with flowering windows of competing flower industry, F5d).

## 8 · Data quality (governance)
| Inconsistency | Status |
|---|---|
| Records dated 2027–2033 (manual additions) | ✅ Corrected (year set to 2025) |
| Midnight records (Android 12-h clock) | ✅ Corrected (+12 h) |
| `costo_hora_registro = 0` on ordinary hours | ✅ Imputed by hour type |
| 2023 Sunday surcharge = 2.0426 (expected 2.00) | 📋 Reported to HR; accepted |
| Capture gaps Jan–Apr 2023-2024 | ⚠️ Corrected with 2025 data (F5f) |

## 9 · Dashboard map
| Tab | Purpose | Audience |
|---|---|---|
| 00 Governance | Data quality, labor grid, headcount structure | Analyst |
| 01 Capacity | kg/h by farm × system × variety | Analyst / Production |
| 02 Crowding | Effect of newcomers on seniors | Analyst / HR |
| 03 Learning curve | New→senior progression, achievements | HR |
| 04 Seasonality | Weekly rhythm, harvest frequency, stress risk | Production |
| 05 Planner | Projection, shortfall engine, HR comparator, backtest | Production / HR |
| 06 Budget | Annual/monthly/weekly compliance, cost, alerts | Management |

## 10 · Code modules
- `app_cosecha_v2.py` (internal dashboard), `app_cosecha_public.py` (public dashboard),
  `plan_ledger.py` (plan ledger), `backtest.py` (accuracy), `forecaster.py` (forecast zoo),
  `comparador_rrhh.py` (hire-vs-overtime), `build_public.py` / `validar_public.py`
  (anonymization + validation), `build_docs_public.py` (doc anonymization),
  `exportar_csv_demo.py` (test fixtures).

## 11 · Roadmap
1. **Git:** initialize repository + initial commit (pending).
2. **Documentation:** this Brain + Committee Guide + Statistical decisions (in progress),
   with ES/EN public translations.
3. **Public version:** anonymization k≥5 / cells≥10 (done), i18n ES/EN (in progress),
   Streamlit Cloud deploy.
4. **Not planned:** APIs/connectors (manual CSV remains), ripeness module.
