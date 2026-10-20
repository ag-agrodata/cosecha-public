"""
app_cosecha_public.py · Versión PÚBLICA anonimizada + i18n ES/EN (final)
=======================================================================
Lee EXCLUSIVAMENTE de data/public/. Toggle de idioma visible arriba a la derecha.
Sin menciones a clientes (confidencialidad). Logo AG v6.
Planificador en MODO DEMO: el share de nuevos es OUTPUT (composición de curvas
convivientes + decisión de contratar), no un slider.

Uso: uv run streamlit run src/berrix/app_cosecha_public.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
import streamlit as st


def _resolve_pub() -> Path:
    here = Path(__file__).resolve().parent
    for c in [here.parent.parent / "data" / "public",
              here.parent / "data" / "public",
              here / "data" / "public"]:
        if c.exists():
            return c
    raise FileNotFoundError("No encuentro data/public/ relativo al app.")


def _resolve_asset(name: str) -> Path:
    here = Path(__file__).resolve().parent
    for base in (here, here.parent):
        p = base / "assets" / name
        if p.exists():
            return p
    return here / "assets" / name


PUB = _resolve_pub()
AG6 = _resolve_asset("ag6.svg")

VERDE = "#1B4332"; DORADO = "#D8B25C"; TERRACOTA = "#BC6C25"; HUESO = "#FAFAF8"; AZUL = "#2C5F7C"
COLOR_CAT = {"Tolerante": VERDE, "Sensible": TERRACOTA, "Sin estimar": AZUL}
PRESUPUESTO_SEMANAL_KG = 2_000

# ═══════════════ DICCIONARIO i18n ═══════════════
STR = {
"ES": {
 "page": "Cosecha · Público",
 "h_title": "Cosecha · Productividad de cosecha de arándanos",
 "h_sub": "Versión pública anonimizada · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales",
 "ban_t": "🫐 VERSIÓN PÚBLICA · DATASET K-ANONIMIZADO",
 "ban_s": "k≥5 trabajadores y celdas≥10 registros por celda publicada · sin identificadores directos · sin bloques · kg/h con top-coding p99.5 · referencias de cliente omitidas por confidencialidad.",
 "tabs": ["🛡️ 00 · Metodología", "📦 01 · Capacidad", "👥 02 · Crowding", "📈 03 · Curva",
          "📅 04 · Estacionalidad", "🎯 05 · Planificador (demo)", "🧠 06 · Modelos y Backtest"],
 "t00_t": "🛡️ Metodología de anonimización y gobernanza",
 "t00_rules": "**Reglas de publicación (k-anonimato):** k ≥ 5 trabajadores únicos por celda · celdas ≥ 10 registros · sin identificadores directos · sin bloques (agregados a predio) · top-coding kg/h en p99.5 · sin fechas exactas.",
 "m_cells_w": "Celdas semanales", "m_cells_mv": "Celdas mes×variedad",
 "m_weeks": "Semanas estacionalidad", "m_vars": "Variedades con parámetros",
 "t00_info": "Este tablero muestra **solo agregados**: cada número publicado corresponde a un grupo de ≥5 personas y ≥10 horas.",
 "exp_not": "📜 Qué NO se publica",
 "exp_not_b": "- IDs y nombres de trabajadores.\n- Bloques individuales.\n- Fechas/horas exactas.\n- Logros individuales.\n- Estado real de plantilla (el Planificador opera en modo demo).\n- Identidad de clientes y referencias comerciales (confidencialidad).",
 "exp_bud": "💰 Metodología de presupuesto (sin datos reales)",
 "exp_bud_b": "Anual 100,000 kg · Mensual 8,333 kg · Semanal 2,000 kg.\nSemáforo: 🟢 ≥95% · 🟡 85–94% · 🔴 <85%. Costo/kg = costo de horas ÷ kg.",
 "t01_t": "📦 Capacidad por predio × sistema × variedad (mensual)",
 "t01_cap": "🟩 Tolerante · 🟥 Sensible · 🟦 Sin estimar.",
 "ren_cap": {"fundo_predio": "Predio", "sistema_cultivo": "Sistema", "tipo_variedad": "Variedad",
             "categoria": "Categoría", "kg": "kg", "horas": "Horas", "costo": "Costo",
             "kg_h": "kg/h", "costo_kg": "Costo/kg", "etiqueta": "Combinación"},
 "cat_map": {"Tolerante": "Tolerante", "Sensible": "Sensible", "Sin estimar": "Sin estimar"},
 "t02_t": "👥 Efecto de novatos sobre experimentados (agregado)",
 "ax_share": "Share de horas de nuevos", "ax_kgh_exp": "kg/h de experimentados", "trend": "Tendencia",
 "t02_beta": "**Sensibilidad al crowding (β) por variedad:**",
 "ren_beta": {"tipo_variedad": "Variedad", "beta": "β", "categoria": "Categoría"},
 "t03_t": "📈 Curva de aprendizaje (cohortes, sin individuos)",
 "ax_weeks": "Semanas activas", "ax_kgh_coh": "kg/h (mediana de cohorte)", "asint": "Asíntota típica",
 "t03_cap": "Cada punto es la mediana de una cohorte de ≥5 trabajadores. Esta curva es la que hace convivir múltiples ritmos de aprendizaje en el planificador.",
 "t04_t": "📅 Estacionalidad semanal",
 "m_peak": "Pico · Sem", "m_valley": "Valle · Sem", "m_amp": "Amplitud",
 "bud_line": " Presupuesto 2,000 kg/sem", "ax_week": "Semana ISO", "ax_kg": "kg promedio",
 "t05_t": "🎯 Planificador semanal prescriptivo",
 "demo": "MODO DEMO · estado físico sintético, no datos reales",
 "t05_cap0": "El **share de nuevos NO es un slider**: se deriva del estado físico (composición por antigüedad, que hace convivir muchas curvas de aprendizaje) y de la **decisión de contratar**, que añade estrés sobre las curvas ya convivientes.",
 "in_kg": "kg proyectados", "in_jorn": "Jornada (h/sem)", "in_tope": "Tope extra (h/sem/persona)",
 "cap_base": "Equipo base (demo): {tb} personas · share de nuevos inicial s₀ = {s0:.0%} · kg/h efectivo inicial = {kh:.2f} (promedio ponderado de las curvas convivientes).",
 "in_hire": "Nuevos a contratar (decisión)",
 "m_share": "Share nuevos s₀→s₁", "m_kgh": "kg/h efectivo", "m_extra": "Horas extra", "m_falt": "Faltante",
 "cap_stress": "**Estrés añadido por contratar {n}:** {lh:,.1f} h perdidas ≈ ${cop:,.0f} ≈ {kg:,.0f} kg.",
 "w_hire": "🟥 CONTRATAR: aún faltan {f} personas tras horas extra.",
 "w_extra": "🟧 HORAS EXTRA: {h:,.0f} h dentro del tope.",
 "s_ok": "✅ El equipo (base + nuevos) cubre la proyección.",
 "exp_form": "🧮 Fórmulas aplicadas",
 "form_b": "- kg/h base (curvas convivientes): promedio ponderado por antigüedad = {khs:.2f}\n- kg/h efectivo tras contratar = {khm:.2f}\n- horas = kg / kg_h_efectivo · gap = horas − equipo·jornada",
 "t06_t": "🧠 Zoológico de pronósticos y selección por backtest",
 "t06_cap": "Demostración con datos públicos: serie semanal por predio×sistema. Se comparan 4 métodos y se elige el de menor WMAPE (holdout 4 semanas).",
 "sel_pred": "Predio", "sel_sis": "Sistema",
 "tit_wmape": "Método ganador: {m}", "ax_wmape": "WMAPE holdout",
 "hist": "Histórico", "fcst": "Pronóstico ({m})", "band": "Intervalo 80%",
 "info_short": "Serie demasiado corta para backtest.", "info_insuf": "Serie insuficiente para esta combinación.",
 "footer": "Versión pública anonimizada · Cosecha operativo · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales · Referencias de cliente omitidas por confidencialidad.",
},
"EN": {
 "page": "Harvest · Public",
 "h_title": "Harvest · Blueberry harvesting productivity",
 "h_sub": "Public anonymized release · Prepared by Andrés Gómez · Agri-industrial Data Analyst",
 "ban_t": "🫐 PUBLIC RELEASE · K-ANONYMIZED DATASET",
 "ban_s": "k≥5 workers and ≥10 records per published cell · no direct identifiers · no block-level data · kg/h top-coded at p99.5 · client references omitted for confidentiality.",
 "tabs": ["🛡️ 00 · Methodology", "📦 01 · Capacity", "👥 02 · Crowding", "📈 03 · Learning curve",
          "📅 04 · Seasonality", "🎯 05 · Planner (demo)", "🧠 06 · Models & Backtest"],
 "t00_t": "🛡️ Anonymization methodology & governance",
 "t00_rules": "**Publication rules (k-anonymity):** k ≥ 5 unique workers per cell · cells ≥ 10 records · no direct identifiers · no blocks (aggregated to farm) · kg/h top-coded at p99.5 · no exact dates.",
 "m_cells_w": "Weekly cells", "m_cells_mv": "Month×variety cells",
 "m_weeks": "Seasonality weeks", "m_vars": "Varieties with parameters",
 "t00_info": "This dashboard shows **aggregates only**: every published number corresponds to a group of ≥5 people and ≥10 hours.",
 "exp_not": "📜 What is NOT published",
 "exp_not_b": "- Worker IDs and names.\n- Individual blocks.\n- Exact dates/times.\n- Individual achievements.\n- Real weekly headcount (the Planner runs in demo mode).\n- Client identity and commercial references (confidentiality).",
 "exp_bud": "💰 Budget methodology (no real data)",
 "exp_bud_b": "Annual 100,000 kg · Monthly 8,333 kg · Weekly 2,000 kg.\nTraffic light: 🟢 ≥95% · 🟡 85–94% · 🔴 <85%. Cost/kg = hour cost ÷ kg.",
 "t01_t": "📦 Capacity by farm × system × variety (monthly)",
 "t01_cap": "🟩 Tolerant · 🟥 Sensitive · 🟦 Not estimated.",
 "ren_cap": {"fundo_predio": "Farm", "sistema_cultivo": "System", "tipo_variedad": "Variety",
             "categoria": "Category", "kg": "kg", "horas": "Hours", "costo": "Cost",
             "kg_h": "kg/h", "costo_kg": "Cost/kg", "etiqueta": "Combination"},
 "cat_map": {"Tolerante": "Tolerant", "Sensible": "Sensitive", "Sin estimar": "Not estimated"},
 "t02_t": "👥 Effect of newcomers on experienced workers (aggregated)",
 "ax_share": "Share of newcomer hours", "ax_kgh_exp": "kg/h of experienced", "trend": "Trend",
 "t02_beta": "**Crowding sensitivity (β) by variety:**",
 "ren_beta": {"tipo_variedad": "Variety", "beta": "β", "categoria": "Category"},
 "t03_t": "📈 Learning curve (cohorts, no individuals)",
 "ax_weeks": "Active weeks", "ax_kgh_coh": "kg/h (cohort median)", "asint": "Typical asymptote",
 "t03_cap": "Each point is the median of a cohort of ≥5 workers. This curve is what makes multiple learning paces coexist in the planner.",
 "t04_t": "📅 Weekly seasonality",
 "m_peak": "Peak · Week", "m_valley": "Valley · Week", "m_amp": "Amplitude",
 "bud_line": " Budget 2,000 kg/week", "ax_week": "ISO week", "ax_kg": "avg kg",
 "t05_t": "🎯 Prescriptive weekly planner",
 "demo": "DEMO MODE · synthetic physical state, not real data",
 "t05_cap0": "The **newcomer share is NOT a slider**: it derives from the physical state (tenure composition, where many learning curves coexist) and from the **hiring decision**, which adds stress on top of the already-coexisting curves.",
 "in_kg": "Projected kg", "in_jorn": "Workweek (h/wk)", "in_tope": "Overtime cap (h/wk/person)",
 "cap_base": "Base team (demo): {tb} people · initial newcomer share s₀ = {s0:.0%} · initial effective kg/h = {kh:.2f} (tenure-weighted average of coexisting curves).",
 "in_hire": "Newcomers to hire (decision)",
 "m_share": "Newcomer share s₀→s₁", "m_kgh": "Effective kg/h", "m_extra": "Overtime hours", "m_falt": "Shortfall",
 "cap_stress": "**Added stress from hiring {n}:** {lh:,.1f} lost hours ≈ ${cop:,.0f} ≈ {kg:,.0f} kg.",
 "w_hire": "🟥 HIRE: still short {f} people after overtime.",
 "w_extra": "🟧 OVERTIME: {h:,.0f} h within the legal cap.",
 "s_ok": "✅ The team (base + newcomers) covers the projection.",
 "exp_form": "🧮 Applied formulas",
 "form_b": "- Base kg/h (coexisting curves): tenure-weighted average = {khs:.2f}\n- Effective kg/h after hiring = {khm:.2f}\n- hours = kg / effective kg/h · gap = hours − team·workweek",
 "t06_t": "🧠 Forecast zoo & backtest selection",
 "t06_cap": "Demo on public data: weekly series per farm×system. Four methods compared; the lowest-WMAPE one wins (4-week holdout).",
 "sel_pred": "Farm", "sel_sis": "System",
 "tit_wmape": "Winning method: {m}", "ax_wmape": "Holdout WMAPE",
 "hist": "History", "fcst": "Forecast ({m})", "band": "80% interval",
 "info_short": "Series too short for backtest.", "info_insuf": "Insufficient series for this combination.",
 "footer": "Public anonymized release · Harvest operations · Prepared by Andrés Gómez · Agri-industrial Data Analyst · Client references omitted for confidentiality.",
},
}

st.set_page_config(page_title="Cosecha · Público / Harvest · Public", page_icon="🫐", layout="wide")

# ── Toggle de idioma SIEMPRE visible (arriba a la derecha) ──
_spacer, _lang_col = st.columns([6, 1], vertical_alignment="center")
with _lang_col:
    LANG = st.radio(
        "Idioma / Language", ["ES", "EN"], index=0, horizontal=True,
        key="lang", label_visibility="collapsed",
    )
T = STR[LANG]

AG6_SVG = AG6.read_text(encoding="utf-8") if AG6.exists() else ""
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
    h1,h2,h3,h4 {{ font-family:'Sora',sans-serif !important; color:#1B4332; }}
    [data-testid="stMetric"] {{ background:#fff; border:1px solid rgba(27,67,50,.08);
        border-left:4px solid #D8B25C; border-radius:12px; padding:14px 18px; }}
    [data-testid="stMetricValue"] {{ color:#1B4332; font-weight:700; }}
    .stTabs [data-baseweb="tab-list"] {{ gap:8px; border-bottom:2px solid rgba(216,178,92,.30); }}
    .stTabs [data-baseweb="tab"] {{ font-family:'Sora',sans-serif; font-weight:600; padding:10px 22px; border-radius:10px 10px 0 0; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ background:#1B4332 !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] p {{ color:#FAFAF8 !important; }}
    .ag-header {{ display:flex; align-items:center; gap:18px; padding-bottom:16px; margin-bottom:12px;
        border-bottom:2px solid rgba(216,178,92,.45); }}
    .ag-logo {{ width:84px; flex-shrink:0; }} .ag-logo svg {{ width:100%; height:auto; display:block; }}
    .ag-title {{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.6rem; color:#1B4332; }}
    .ag-subtitle {{ font-size:.85rem; color:#2c5b48; margin-top:4px; }}
    .pub-banner {{ background:#1B4332; color:#FAFAF8; border-left:6px solid #D8B25C;
        border-radius:12px; padding:14px 22px; margin-bottom:18px; }}
    .pub-banner .t {{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.15rem; }}
    .pub-banner .s {{ font-size:.88rem; opacity:.92; margin-top:4px; }}
    .demo-badge {{ display:inline-block; background:#FEF3C7; color:#92400E; font-weight:700;
        padding:4px 12px; border-radius:12px; font-size:.85rem; }}
    </style>
    <div class="ag-header">
      <div class="ag-logo">{AG6_SVG}</div>
      <div>
        <div class="ag-title">{T['h_title']}</div>
        <div class="ag-subtitle">{T['h_sub']}</div>
      </div>
    </div>
    <div class="pub-banner">
      <div class="t">{T['ban_t']}</div>
      <div class="s">{T['ban_s']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

pio.templates["ag_cosecha"] = go.layout.Template(
    layout=dict(colorway=[VERDE, AZUL, DORADO, TERRACOTA, "#E9C46A"],
                font=dict(family="Inter, sans-serif", color=VERDE),
                paper_bgcolor=HUESO, plot_bgcolor=HUESO,
                margin=dict(l=48, r=20, t=48, b=40)))
pio.templates.default = "ag_cosecha"


@st.cache_data
def cargar_public() -> dict:
    return {
        "hechos_semana": pl.read_parquet(PUB / "hechos_semana.parquet"),
        "hechos_var": pl.read_parquet(PUB / "hechos_mes_variedad.parquet"),
        "curva": pl.read_parquet(PUB / "curva_public.parquet"),
        "crowding": pl.read_parquet(PUB / "crowding_public.parquet"),
        "params": pl.read_parquet(PUB / "params_public.parquet"),
        "est": pl.read_parquet(PUB / "estacionalidad_public.parquet"),
    }


P = cargar_public()

tab_met, tab_cap, tab_crowd, tab_curva, tab_est, tab_sim, tab_mod = st.tabs(T["tabs"])

# ═══════════ 00 · METODOLOGÍA ═══════════
with tab_met:
    st.subheader(T["t00_t"])
    st.markdown(T["t00_rules"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T["m_cells_w"], f"{P['hechos_semana'].height:,}")
    m2.metric(T["m_cells_mv"], f"{P['hechos_var'].height:,}")
    m3.metric(T["m_weeks"], P["est"].height)
    m4.metric(T["m_vars"], P["params"].height)
    st.info(T["t00_info"])
    with st.expander(T["exp_not"]):
        st.markdown(T["exp_not_b"])
    with st.expander(T["exp_bud"]):
        st.markdown(T["exp_bud_b"])

# ═══════════ 01 · CAPACIDAD ═══════════
with tab_cap:
    st.subheader(T["t01_t"])
    hv = P["hechos_var"].join(P["params"].select(["tipo_variedad", "categoria"]),
                              on="tipo_variedad", how="left"
                              ).with_columns(categoria=pl.col("categoria").fill_null("Sin estimar"))
    cap = (hv.group_by(["fundo_predio", "sistema_cultivo", "tipo_variedad", "categoria"])
           .agg([pl.col("kg").sum().alias("kg"), pl.col("n_regs").sum().alias("horas"),
                 pl.col("costo").sum().alias("costo")])
           .with_columns([(pl.col("kg") / pl.col("horas").clip(lower_bound=1)).alias("kg_h"),
                          (pl.col("costo") / pl.col("kg").clip(lower_bound=1)).alias("costo_kg")])
           .with_columns(etiqueta=pl.col("fundo_predio").str.replace("Predio_", "P")
                         + "·" + pl.col("sistema_cultivo").str.replace("Sistema_", "S")
                         + "·" + pl.col("tipo_variedad").str.replace("Variedad_", "V"))
           .sort("kg_h", descending=True))
    top = cap.head(12).to_pandas()
    fig = go.Figure(go.Bar(x=top["etiqueta"], y=top["kg_h"],
                           marker_color=[COLOR_CAT.get(c, AZUL) for c in top["categoria"]],
                           text=[f"{v:.2f}" for v in top["kg_h"]], textposition="outside"))
    fig.update_layout(yaxis_title="kg/h", height=400)
    st.plotly_chart(fig, width="stretch")
    st.caption(T["t01_cap"])
    disp = cap.to_pandas()
    disp["categoria"] = disp["categoria"].map(lambda c: T["cat_map"].get(c, c))
    disp.columns = [T["ren_cap"].get(c, c) for c in disp.columns]
    st.dataframe(disp, width="stretch", hide_index=True)

# ═══════════ 02 · CROWDING ═══════════
with tab_crowd:
    st.subheader(T["t02_t"])
    cw = P["crowding"].filter(pl.col("n_regs") >= 20).to_pandas()
    fig = go.Figure()
    for pred, grp in cw.groupby("fundo_predio"):
        fig.add_trace(go.Scatter(x=grp["share_horas_nuevos"], y=grp["kg_h_exp"], mode="markers",
                                 name=pred, marker=dict(size=7, opacity=0.6,
                                 color=VERDE if pred == "Predio_1" else AZUL)))
    if len(cw) > 2:
        b, a_ = np.polyfit(cw["share_horas_nuevos"], cw["kg_h_exp"], 1)
        xs = np.linspace(0, cw["share_horas_nuevos"].max(), 20)
        fig.add_trace(go.Scatter(x=xs, y=a_ + b * xs, mode="lines", name=T["trend"],
                                 line=dict(color=TERRACOTA, width=3, dash="dash")))
    fig.update_layout(xaxis_title=T["ax_share"], yaxis_title=T["ax_kgh_exp"], height=420)
    st.plotly_chart(fig, width="stretch")
    st.markdown(T["t02_beta"])
    bt = P["params"].select(["tipo_variedad", "beta", "categoria"]).sort("beta", descending=True).to_pandas()
    bt["categoria"] = bt["categoria"].map(lambda c: T["cat_map"].get(c, c))
    bt.columns = [T["ren_beta"].get(c, c) for c in bt.columns]
    st.dataframe(bt, width="stretch", hide_index=True)

# ═══════════ 03 · CURVA ═══════════
with tab_curva:
    st.subheader(T["t03_t"])
    cv = P["curva"].to_pandas()
    fig = go.Figure(go.Scatter(x=cv["semanas_activas"], y=cv["kg_h_mediana"],
                               mode="lines+markers", line=dict(color=VERDE, width=3)))
    asint = float(P["params"]["a"].median())
    fig.add_hline(y=asint, line_dash="dot", line_color=DORADO,
                  annotation_text=f"{T['asint']} {asint:.2f}")
    fig.update_layout(xaxis_title=T["ax_weeks"], yaxis_title=T["ax_kgh_coh"], height=420)
    st.plotly_chart(fig, width="stretch")
    st.caption(T["t03_cap"])

# ═══════════ 04 · ESTACIONALIDAD ═══════════
with tab_est:
    st.subheader(T["t04_t"])
    es = P["est"].to_pandas()
    pico = es.loc[es["kg_promedio"].idxmax()]; valle = es.loc[es["kg_promedio"].idxmin()]
    m1, m2, m3 = st.columns(3)
    m1.metric(f"{T['m_peak']} {int(pico['semana_numero'])}", f"{pico['kg_promedio']:,.0f} kg")
    m2.metric(f"{T['m_valley']} {int(valle['semana_numero'])}", f"{valle['kg_promedio']:,.0f} kg")
    m3.metric(T["m_amp"], f"{pico['kg_promedio']/valle['kg_promedio']:.1f}×")
    fig = go.Figure(go.Bar(x=es["semana_numero"], y=es["kg_promedio"],
                           marker_color=[VERDE if k >= PRESUPUESTO_SEMANAL_KG else AZUL for k in es["kg_promedio"]]))
    fig.add_hline(y=PRESUPUESTO_SEMANAL_KG, line_dash="dash", line_color=TERRACOTA,
                  annotation_text=T["bud_line"])
    fig.update_layout(xaxis_title=T["ax_week"], yaxis_title=T["ax_kg"], height=420)
    st.plotly_chart(fig, width="stretch")

# ═══════════ 05 · PLANIFICADOR (DEMO) ═══════════
with tab_sim:
    st.subheader(T["t05_t"])
    st.markdown(f'<span class="demo-badge">{T["demo"]}</span>', unsafe_allow_html=True)
    st.caption(T["t05_cap0"])
    COMP_DEMO = {1: 2, 2: 2, 3: 1, 4: 1, 6: 2, 8: 2, 12: 2, 16: 2, 24: 2, 32: 2, 40: 2}
    curva_map = {int(r["semanas_activas"]): float(r["kg_h_mediana"]) for r in P["curva"].iter_rows(named=True)}
    max_sem = max(curva_map)

    def kg_h_ten(t):
        t = min(int(t), max_sem)
        while t not in curva_map and t > 0:
            t -= 1
        return curva_map.get(t, 0.0)

    total_base = sum(COMP_DEMO.values())
    new_base = sum(c for t, c in COMP_DEMO.items() if t <= 4)
    s0 = new_base / total_base
    kg_h_base = sum(c * kg_h_ten(t) for t, c in COMP_DEMO.items()) / total_base

    c1, c2, c3 = st.columns(3)
    kg_proy = c1.number_input(T["in_kg"], 0, 20000, 2000, 100)
    jornada = c2.number_input(T["in_jorn"], 40, 48, 46, 1)
    tope_extra = c3.number_input(T["in_tope"], 0, 12, 10, 1)
    st.caption(T["cap_base"].format(tb=total_base, s0=s0, kh=kg_h_base))

    horas_base = kg_proy / kg_h_base if kg_h_base > 0 else 0
    gap = horas_base - total_base * jornada
    n_sugg = int(np.ceil(gap / jornada)) if gap > 0 else 0
    n_contr = st.number_input(T["in_hire"], 0, 20, n_sugg, 1)

    total_new = total_base + n_contr
    s1 = (new_base + n_contr) / total_new
    kg_h_new = (sum(c * kg_h_ten(t) for t, c in COMP_DEMO.items()) + n_contr * kg_h_ten(1)) / total_new
    horas_new = kg_proy / kg_h_new if kg_h_new > 0 else 0
    gap_new = horas_new - total_new * jornada
    h_extra = min(max(gap_new, 0), total_new * tope_extra)
    faltante = int(np.ceil(max(gap_new - h_extra, 0) / jornada))
    rate = float(P["hechos_semana"]["costo"].sum() / P["hechos_semana"]["n_regs"].sum())
    lost_h = max(0.0, kg_proy * (1 / kg_h_new - 1 / kg_h_base)) if kg_h_new > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T["m_share"], f"{s0:.0%} → {s1:.0%}")
    m2.metric(T["m_kgh"], f"{kg_h_new:.2f}", delta=f"{kg_h_new - kg_h_base:+.2f}")
    m3.metric(T["m_extra"], f"{h_extra:,.0f}")
    m4.metric(T["m_falt"], faltante)
    st.caption(T["cap_stress"].format(n=n_contr, lh=lost_h, cop=lost_h * rate, kg=lost_h * kg_h_new))
    if faltante > 0:
        st.warning(T["w_hire"].format(f=faltante))
    elif h_extra > 0:
        st.warning(T["w_extra"].format(h=h_extra))
    else:
        st.success(T["s_ok"])
    with st.expander(T["exp_form"]):
        st.markdown(T["form_b"].format(khs=kg_h_base, khm=kg_h_new))

# ═══════════ 06 · MODELOS Y BACKTEST ═══════════
with tab_mod:
    st.subheader(T["t06_t"])
    st.caption(T["t06_cap"])
    try:
        from berrix import forecaster as fc
    except ImportError:
        import forecaster as fc
    hs = P["hechos_semana"].with_columns((pl.col("ano") * 100 + pl.col("semana_numero")).alias("periodo"))
    cc1, cc2 = st.columns(2)
    p_sel = cc1.selectbox(T["sel_pred"], sorted(hs["fundo_predio"].unique().to_list()))
    s_sel = cc2.selectbox(T["sel_sis"], sorted(hs["sistema_cultivo"].unique().to_list()))
    ser = hs.filter((pl.col("fundo_predio") == p_sel) & (pl.col("sistema_cultivo") == s_sel)).sort("periodo")
    y = ser["kg"].to_list()
    if len(y) >= 14:
        res_bt = fc.backtest_combo(np.array(y, float), h_hold=4)
        if res_bt:
            errs, denom = res_bt
            wmape = {m: errs[m] / denom for m in fc.METODOS}
            ganador = min(wmape, key=wmape.get)
            figw = go.Figure(go.Bar(x=list(wmape.keys()), y=[wmape[m] for m in wmape],
                                    marker_color=[VERDE if m == ganador else AZUL for m in wmape],
                                    text=[f"{wmape[m]:.0%}" for m in wmape], textposition="outside"))
            figw.update_layout(yaxis_title=T["ax_wmape"], height=320, title=T["tit_wmape"].format(m=ganador))
            st.plotly_chart(figw, width="stretch")
            pts, bands = fc.forecast(np.array(y, float), 6, ganador)
            hx = list(range(1, len(y) + 1)); fx = list(range(len(y) + 1, len(y) + 7))
            figf = go.Figure()
            figf.add_trace(go.Scatter(x=hx, y=y, mode="lines", name=T["hist"], line=dict(color=AZUL, width=2)))
            figf.add_trace(go.Scatter(x=fx, y=pts, mode="lines+markers", name=T["fcst"].format(m=ganador),
                                      line=dict(color=VERDE, width=3)))
            lo = [b[0] for b in bands]; hi = [b[1] for b in bands]
            figf.add_trace(go.Scatter(x=fx + fx[::-1], y=hi + lo[::-1], fill="toself",
                                      fillcolor="rgba(27,67,50,0.15)", line=dict(width=0), name=T["band"]))
            figf.update_layout(yaxis_title="kg", height=420)
            st.plotly_chart(figf, width="stretch")
        else:
            st.info(T["info_short"])
    else:
        st.info(T["info_insuf"])

st.markdown(
    f"""
    <div style="margin-top:40px;padding-top:20px;border-top:2px solid rgba(216,178,92,.45);
                color:#777;font-size:.85rem;text-align:center;">{T['footer']}</div>
    """,
    unsafe_allow_html=True,
)
