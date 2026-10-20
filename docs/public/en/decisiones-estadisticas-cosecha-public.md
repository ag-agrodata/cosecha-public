# Statistical Decisions and Mathematical Component · Harvest Operations
> **Public anonymized version** · no client identifiers · Prepared by Andrés Gómez · Agri-industrial Data Analyst.
> Mathematical transparency document for the Cosecha (operations) project.
> Basis for the public anonymized release.
> Strictly separate from any commercial engagement under NDA.

---

## 1 · Productivity model

### 1.1 Learning curve
A new harvester's kg/h rises with active weeks until reaching an asymptote.
The asymptote is defined as the median kg/h of top performers (company rule).

**Operational threshold for "new" (S08):** ≤ 4 active weeks.

### 1.2 Crowding (β effect) — Decision D01
The effect of newcomers on seniors **depends on the variety**, not on the farm.

**Senior kg/h formula given a newcomer hour-share s:**

$$
kg\_h_{senior}(s) = \max\bigl(a \cdot (1 - \beta \cdot s),\; 0.70 \cdot a\bigr)
$$

Where:
- `a` = senior kg/h with no newcomers (per-variety parameter).
- `β` = crowding sensitivity (0 for tolerant, up to 0.38 for sensitive).
- `s` = share of hours worked by new harvesters (an **output** of the current state).
- Floor `0.70·a` = protection against extreme drops.

**Empirical classification (D01):**
- Tolerant (β = 0): varieties 16, 19, 1, 20, 10, 24.
- Sensitive: Variety_9 (0.38), Variety_4 (0.26), Variety_15 (0.13).

### 1.3 Mixed formula (full model)
Combines the learning curve and crowding:

$$
kg\_h_{mixed}(s) = (1 - s) \cdot kg\_h_{senior}(s) \;+\; s \cdot kg\_h_{new}
$$

Where `kg_h_new` is a newcomer's kg/h in their first week (per-variety parameter).

**Interpretation:** share s=1.0 (newcomers only) returns `kg_h_new` (novice pace).
Share s=0.0 (seniors only) returns `kg_h_senior(0) = a`.

### 1.4 Derived metrics
- **Effective kg/h:** `kg_h_mixed(s)`, with a configurable floor (default 3.5 for combinations without a model).
- **% difficulty:** drop of the effective kg/h relative to the senior ideal.

$$
\%\;difficulty = 1 - \frac{kg\_h_{mixed}}{a}
$$

0% = performs like a senior. 30% = performs 30% below due to newcomers + β.

---

## 2 · Kilogram forecasting (Step 3a)

### 2.1 Dense weekly series
For each combination, a continuous weekly series is built (ordinal from `week_start`)
with `0` in weeks without harvest. This respects biweekly patterns and avoids
moving-average bias at turning points.

### 2.2 Method zoo
| Method | Description | Requires |
|---|---|---|
| `mov_avg` | Moving average of the last 6 harvests (baseline) | 6 observations |
| `seasonal` | Seasonal naive: same week previous year × recent level ratio | 52 + 4 observations |
| `holt` | Double exponential smoothing (level + trend, α=0.3, β=0.1) | ≥ 2 |
| `theta` | Average of a linear-trend line and a sloped SES line | ≥ 3 |

### 2.3 Selection by holdout backtest
For each group (variety / block / farm), models are trained on data up to the cut and
evaluated by WMAPE over the last 4 weeks (holdout). The method with the lowest pooled WMAPE wins.

$$
WMAPE = \frac{\sum |forecast_t - actual_t|}{\sum |actual_t|}
$$

### 2.4 Prediction intervals (80%)

$$
[ \hat{y}_{t+h} \pm z \cdot \sigma \cdot \sqrt{h} ]
$$

- `z = 1.28` (90th percentile for an 80% band).
- `σ` = standard deviation of in-sample residuals.
- Lower bound truncated at 0 (kg cannot be negative).

### 2.5 Recalibration factors
Per group, after comparing forecasts against actuals:

$$
factor = \frac{\sum actual}{\sum forecast}
$$

Factor < 1 → the method overestimates; > 1 → it underestimates. Used to adjust the next forecast.

### 2.6 ISO Thursday rule (Tab 06)
Each ISO week is assigned to the month/year of its corresponding **Thursday**.
Avoids cross-year week artifacts and keeps historical navigation consistent.

---

## 3 · Planner engine (Tab 05)

### 3.1 Per programmed combination
$$
hours\_needed = \frac{kg\_projected}{kg\_h_{mixed}(s)}
$$

### 3.2 Per farm
$$
hours\_available = active\_team \times ordinary\_weekly\_hours
$$
$$
gap = hours\_needed - hours\_available
$$

### 3.3 Overtime (D04, an output)
$$
overtime\_hours = \min(gap,\; active\_team \times overtime\_cap)
$$

Legal cap: Art. 167 CST = 12 h/week/person. Configurable operational cap (default 10 h).

### 3.4 Headcount shortfall
$$
remaining\_gap = gap - overtime\_hours
$$
$$
headcount\_shortfall = \lceil remaining\_gap \,/\, ordinary\_weekly\_hours \rceil
$$

---

## 4 · HR comparator (Step 3b, D09)

### 4.1 Option A — Overtime
$$
kg_A = overtime\_hours \times kg\_h_{farm} \times fatigue
$$
$$
cost_A = overtime\_hours \times rate \times 1.25
$$

- `fatigue` = 0.95 (S04, configurable).
- `rate` = farm's average ordinary hourly cost.

### 4.2 Option B — Hire N people
$$
N = \lceil gap \,/\, ordinary\_weekly\_hours \rceil
$$
$$
kg_{B,w1} = N \times ordinary\_hours \times kg\_h_{new}
$$
$$
cost_B = N \times ordinary\_hours \times rate \times (1 + surcharge)
$$

- `surcharge` = 0.15 (S05, configurable; staffing-agency administration and equipment).

**Stress priced in lost hours:**

$$
s_{new} = \frac{s_{current} \cdot base\_hours + new\_hours}{total\_hours}
$$

$$
lost\_h = \max\bigl(0,\; kg_{farm} \cdot (\tfrac{1}{kg\_h_{mixed}(s_{new})} - \tfrac{1}{kg\_h_{mixed}(s_{current})})\bigr)
$$

$$
stress\_COP = lost\_h \times rate \qquad stress\_kg = lost\_h \times kg\_h_{mixed}(s_{new})
$$

Stress decomposition:
- **Learning:** loss because `kg_h_new < kg_h_senior` (always present).
- **Crowding:** additional loss from β>0 when the newcomer share rises (sensitive varieties only).

### 4.3 Option C — Mixed
Overtime up to the cap + hire the remainder. Cost and stress proportional to the hired fraction.

### 4.4 Break-even (S07)
Projection over a `horizon` of weeks (default 8). For each week w, cost and kg are accumulated
for A and B. `break_even` = first week where B accumulates less cost than A for the same kg.

If the `gap` is transient (≤ 2 weeks), A wins. If structural (≥ horizon), B wins.

---

## 5 · Backtest (accuracy)

### 5.1 Metrics
- **WMAPE per method:** robust to small weeks.
- **Bias:** `mean(forecast − actual)`. Positive = over-projection.
- **Operational classification:**
  - Hit: planned and harvested.
  - Over-projection: planned but not harvested.
  - Not planned but harvested: backlog fruit (*látigo*).
  - Correctly not planned.

### 5.2 Explicit-zero grid
To classify "over-projection" and "correctly not planned" properly, the actuals grid includes
**all** combinations × target weeks, with `kg_actual = 0` where no harvest occurred.
This avoids the bias of only considering weeks with kg > 0.

---

## 6 · Seasonality and frequency

### 6.1 Weekly seasonality
Peak/valley amplitude = **7.3×**. Actual peak: week 18 (April). Valley: week 1 (January).

**Note:** Jan–Apr is based on 2025 only, due to capture gaps in 2023-2024.

### 6.2 Harvest frequency
- **Weekly (≥90%):** System_3.
- **Biweekly (45-89%):** System_10.
- A block can contain weekly and biweekly combinations; hence the operational unit is the
  combination, not the block (D10).

### 6.3 Actual coverage per harvest event
- Systems: 44% average per event.
- Varieties: 66% average per event.
- Only 3% of events harvest the entire block.

**Conclusion:** "every block is always harvested" holds **cumulatively across the week**
(multiple visits), not per single event.

---

## 7 · Anonymization rules (public version)

For the public release, every aggregate must satisfy:

1. **k ≥ 5:** any group aggregate must contain ≥5 unique workers. Smaller groups are
   suppressed or merged with sibling groups.
2. **Cells ≥ 10:** cross-tab cells with count <10 are suppressed.
3. **No direct identifiers:** worker IDs and names removed; only cohort/category aggregates.
4. **No indirect identifiers:** small blocks (<5 workers) aggregated to farm level.
5. **Temporal jittering:** exact achievement dates rounded to the week.
6. **Top-coding:** extreme values (p99.5+) truncated.
7. **No NDA correlation:** all analysis is restricted to the operational scope (harvest
   productivity); commercial and financial domains are excluded.

---

## 8 · Limitations and unmodeled assumptions

- **No ripeness data:** fruit postponed for immaturity is detected by absence of harvest plus
  agronomic criteria, not by sensor.
- **No climate impact:** greenhouse cultivation, negligible impact.
- **Future turnover not predictable:** 57% of drop-offs coincide with flowering windows of the
  competing flower industry; seasonal but not predictable at the individual level.
- **Capture gaps:** Jan–Apr 2023-2024 corrected with 2025 data; any trend analysis over that
  range must be taken with caution.

---

## 9 · References

- **Dataset:** anonymized history 2022-12 → 2025-05, 118,329 records.
- **Labor framework:** Law 2101 of 2021 (progressive workweek reduction).
- **Art. 167 CST:** overtime cap.
- **Validated work grid:** 48h (Dec-22→Jun-23) → 47h (Jul-23→Jun-24) → 46h (Jul-24→May-25).
