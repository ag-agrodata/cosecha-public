"""
Pronosticador mejorado (Paso 3a)
================================
Zoológico pequeño y explicable de pronóstico semanal en NumPy puro,
elegido por backtest holdout por grupo. Serie semanal densa (con ceros
en semanas sin cosecha) alineada por ordinal de semana real.

Métodos: mov_avg (baseline), seasonal, holt, theta.
Intervalos: ± z·σ·√h (σ de residuos in-sample).

Uso CLI (prueba sin UI):
    uv run python -m berrix.forecaster
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
KEYS = ["fundo_predio", "bloque_invernadero", "sistema_cultivo", "tipo_variedad"]
SEASON = 52
METODOS = ["mov_avg", "seasonal", "holt", "theta"]


# ─────────────────────────── MÉTODOS ───────────────────────────
def f_mov_avg(y, h, k=6):
    y = np.asarray(y, float)
    if y.size == 0:
        return [0.0] * h
    base = y[-k:].mean()
    return [base] * h


def f_seasonal(y, h, season=SEASON, r=4):
    y = np.asarray(y, float)
    n = y.size
    if n < season + r:
        return f_mov_avg(y, h)
    recent = y[-r:].mean()
    past = y[n - season - r:n - season].mean()
    ratio = recent / past if past > 0 else 1.0
    out = []
    for i in range(h):
        idx = n - season + i
        base = y[idx] if 0 <= idx < n else (y[n - season] if n >= season else recent)
        out.append(max(base * ratio, 0.0))
    return out


def f_holt(y, h, alpha=0.3, beta=0.1):
    y = np.asarray(y, float)
    if y.size == 0:
        return [0.0] * h
    if y.size == 1:
        return [float(y[0])] * h
    level = y[0]
    trend = (y[-1] - y[0]) / (y.size - 1)
    for v in y[1:]:
        prev = level
        level = alpha * v + (1 - alpha) * (level + trend)
        trend = beta * (level - prev) + (1 - beta) * trend
    return [max(level + (i + 1) * trend, 0.0) for i in range(h)]


def f_theta(y, h, alpha=0.3):
    y = np.asarray(y, float)
    n = y.size
    if n < 3:
        return f_mov_avg(y, h)
    x = np.arange(n, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    ses = y[0]
    for v in y[1:]:
        ses = alpha * v + (1 - alpha) * ses
    out = []
    for i in range(h):
        lin = intercept + slope * (n + i)
        sesline = ses + slope * (i + 1)
        out.append(max(0.5 * lin + 0.5 * sesline, 0.0))
    return out


FUNCS = {"mov_avg": f_mov_avg, "seasonal": f_seasonal, "holt": f_holt, "theta": f_theta}


# ─────────────────────────── INTERVALOS Y BACKTEST ───────────────────────────
def sigma_resid(y, metodo, warm=6):
    y = np.asarray(y, float)
    fn = FUNCS[metodo]
    res = [y[t] - fn(y[:t], 1)[0] for t in range(warm, y.size)]
    return float(np.std(res)) if len(res) > 1 else 0.0


def forecast(y, h, metodo, z=1.28):
    """Pronóstico puntual a h semanas + intervalo 80%."""
    pts = FUNCS[metodo](y, h)
    s = sigma_resid(y, metodo)
    bands = [(max(p - z * s * np.sqrt(i + 1), 0.0), p + z * s * np.sqrt(i + 1))
             for i, p in enumerate(pts)]
    return pts, bands


def backtest_combo(y, h_hold=4, min_train=10):
    """WMAPE holdout por método para una combinación. Devuelve (errs, denom) o None."""
    y = np.asarray(y, float)
    n = y.size
    if n < min_train + h_hold:
        return None
    tr, te = y[:n - h_hold], y[n - h_hold:]
    denom = float(np.abs(te).sum())
    if denom <= 0:
        return None
    errs = {m: float(np.abs(np.array(FUNCS[m](tr, h_hold)) - te).sum()) for m in METODOS}
    return errs, denom


def seleccionar_metodos(dense: dict, grupo_de: dict, h_hold=4):
    """Elige el método con menor WMAPE agrupado. Devuelve {grupo: (metodo, wmape_por_metodo)}."""
    acc: dict = {}
    for combo, y in dense.items():
        r = backtest_combo(y, h_hold)
        if not r:
            continue
        errs, denom = r
        g = grupo_de.get(combo, "global")
        a = acc.setdefault(g, {m: [0.0, 0.0] for m in METODOS})
        for m in METODOS:
            a[m][0] += errs[m]
            a[m][1] += denom
    out = {}
    for g, a in acc.items():
        wmape = {m: (a[m][0] / a[m][1] if a[m][1] > 0 else np.inf) for m in METODOS}
        out[g] = (min(wmape, key=wmape.get), wmape)
    return out


# ─────────────────────────── SERIE DENSA ───────────────────────────
def construir_dense(model: pl.DataFrame):
    """Serie semanal densa por combinación (0 en semanas sin cosecha) + ordinal de semana."""
    s = (
        model.group_by(["ano", "semana_numero", "week_start"] + KEYS)
        .agg(pl.col("peso_numerico").sum().alias("kg"))
    )
    min_ws = s["week_start"].min()
    s = s.with_columns(((pl.col("week_start") - min_ws).dt.total_days() // 7).alias("ord"))
    buckets: dict = {}
    for row in s.select(KEYS + ["ord", "kg"]).iter_rows(named=True):
        combo = tuple(row[k] for k in KEYS)
        buckets.setdefault(combo, {})[row["ord"]] = row["kg"]
    dense = {}
    ords_ini = {}
    for combo, d in buckets.items():
        ords = sorted(d)
        if not ords:
            continue
        dense[combo] = np.array([d.get(o, 0.0) for o in range(ords[0], ords[-1] + 1)], float)
        ords_ini[combo] = ords[0]
    cur_ord = int(s["ord"].max())
    return dense, ords_ini, cur_ord


def pronosticar_para_semana(dense, ords_ini, combo, target_ord, h, metodo):
    """Entrena con semanas < target_ord y pronostica h semanas desde target_ord."""
    arr = dense.get(combo)
    if arr is None:
        return None
    idx = target_ord - ords_ini[combo]
    if idx <= 6:
        return None
    y_train = arr[:idx]
    return forecast(y_train, h, metodo)


# ─────────────────────────── PRUEBA CLI ───────────────────────────
if __name__ == "__main__":
    model = pl.read_parquet(DATA / "cosecha_model.parquet")
    dense, ords_ini, cur_ord = construir_dense(model)
    grupo_de = {c: c[3] for c in dense}  # agrupar por variedad

    sel = seleccionar_metodos(dense, grupo_de, h_hold=4)
    print("=== Método ganador por variedad (WMAPE holdout 4 semanas) ===")
    for g in sorted(sel):
        metodo, wmape = sel[g]
        detalle = " · ".join(f"{m}:{w:.0%}" for m, w in sorted(wmape.items(), key=lambda kv: kv[1]))
        print(f"  {g:>12} → {metodo if False else metodo:>8}  |  {detalle}")

    print("\n=== Ejemplo: pronóstico 6 semanas (método del grupo) con intervalo 80% ===")
    ejemplo = max(dense, key=lambda c: dense[c].sum())
    metodo = sel[grupo_de[ejemplo]][0]
    res = pronosticar_para_semana(dense, ords_ini, ejemplo, cur_ord + 1, 6, metodo)
    if res:
        pts, bands = res
        print(f"  Combinación: {ejemplo} · método: {metodo}")
        for i, (p, (lo, hi)) in enumerate(zip(pts, bands), start=1):
            print(f"    S+{i}: {p:8,.0f} kg   [80%: {lo:,.0f} – {hi:,.0f}]")
