[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

<div align="center">

<img src="src/berrix/assets/ag6.svg" alt="AG · Andrés Gómez/Agrodata" width="180"/>

# 🫐 Productividad de Cosecha de Arándanos · Berrix
### Versión Pública

**Planificador semanal prescriptivo para cosecha de arándanos en invernadero.**<br/>
Python · Polars · Streamlit · Plotly · dataset público k-anonimizado.

[![Python](https://img.shields.io/badge/Python-3.13-1B4332?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.61-1B4332?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Polars](https://img.shields.io/badge/Polars-1.43-2C5F7C?style=flat-square)](https://pola.rs/) [![DuckDB](https://img.shields.io/badge/DuckDB-SQL-2C5F7C?style=flat-square&logo=duckdb&logoColor=white)](https://duckdb.org/) [![Plotly](https://img.shields.io/badge/Plotly-6.9-BC6C25?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)

*Elaborado por **Andrés Gómez** · Analista de Datos Agroindustriales*

[🚀 Demo en vivo](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/) · [📖 Documentación](docs/public/) · [📊 Cerebro analítico](docs/public/cerebro-cosecha-public.md)

</div>

---

## Resumen en 2 minutos

Un planificador semanal prescriptivo que traduce la proyección de cosecha de arándanos en horas de trabajo, brechas de personal y costos operativos. Convierte datos históricos de productividad en pronósticos accionables y mide la exactitud semana tras semana. Construido sobre datos reales anonimizados (k ≥ 5 trabajadores, ≥ 10 registros por celda), con demo pública y metodología estadística documentada.

> **Aviso legal:** Los agregados publicados cumplen estándares estrictos de k-anonimato. No permiten identificar trabajadores individuales, bloques específicos ni revelar la identidad del cliente. Consulta las [Decisiones Estadísticas](docs/public/decisiones-estadisticas-cosecha-public.md) para la especificación completa.

## El problema

Los equipos de producción y RRHH en agroindustria suelen planificar la cosecha con promedios estáticos, subestimando el efecto de la curva de aprendizaje, la fatiga acumulada y la estacionalidad. Cuando la planificación es reactiva, se generan costos por horas extra no planificadas, estrés operativo y mermas en la productividad. 

La pregunta que este proyecto responde: ¿cómo transformar datos operativos históricos en un plan de cosecha prescriptivo, justo y eficiente?

## Qué demuestra este proyecto

- **Modelar la realidad operativa:** Traducir conceptos agronómicos (curva de aprendizaje, efecto crowding) en fórmulas matemáticas ejecutables en Python y Polars.
- **Pronósticos explicables sobre "cajas negras":** Implementar un "zoológico de pronósticos" (media móvil, estacional, Holt, Theta) que compiten por WMAPE, priorizando la interpretabilidad sobre la complejidad del machine learning.
- **Toma de decisiones con incertidumbre:** Calcular intervalos de confianza al 80% y escenarios de break-even (horas extra vs. contratación) para respaldar decisiones de RRHH con datos, no con intuición.
- **Gobernanza y anonimización rigurosa:** Aplicar k-anonimato, supresión y top-coding para publicar datos operativos sensibles sin comprometer la privacidad de los trabajadores.
- **Ciclo de vida completo del dato:** Desde la extracción de registros ERP hasta un tablero interactivo en Streamlit con toggle bilingüe (ES/EN) y documentación de linaje.

## Recomendaciones e impacto

> **Nota de transparencia:** Las cifras de impacto (costos, kg, horas) se presentan como rangos estimados bajo NDA. Las cifras exactas están bajo confidencialidad y deben validarse internamente antes de su uso en presentaciones.

### 1 · Optimizar la mezcla de personal (Mixto vs. Horas Extra)
El comparador de RRHH identifica el punto de break-even donde contratar personal nuevo acumula menos costo que pagar horas extra con fatiga. La recomendación es usar este umbral para aprobar solicitudes de contratación temporal antes de que la brecha de horas se vuelva insostenible.

### 2 · Intervención temprana en cohortes de novatos
La vista de "Curva de aprendizaje" permite identificar cuándo una cohorte se estanca. La recomendación operativa es asignar mentores o ajustar la carga de trabajo en las primeras 4 semanas, antes de que la productividad caiga por debajo del 70% del objetivo senior.

### 3 · Ajuste dinámico de metas por estacionalidad
La vista de estacionalidad revela picos de estrés operativo. La recomendación es ajustar las metas de kg/hora esperadas durante ventanas florales o climáticas críticas, evitando penalizar al equipo por factores externos no modelados.

## Demo en vivo

**🔗 [Abrir el tablero público →](https://cosecha-public-bvexudmlprqdcpwzjzmpxb.streamlit.app/)**

Siete pestañas, toggle ES/EN, todos los datos k-anonimizados:

| Pestaña | Audiencia | Qué muestra |
|---------|-----------|-------------|
| 00 · Metodología | Analista | Gobernanza, reglas de anonimización, linaje |
| 01 · Capacidad | Producción | kg/h por predio × sistema × variedad (mensual) |
| 02 · Crowding | RRHH / Analista | Efecto de novatos sobre experimentados (β) |
| 03 · Curva | RRHH | Progresión por cohortes hacia la senioría |
| 04 · Estacionalidad | Producción | Ritmo semanal, frecuencia, riesgo de estrés |
| 05 · Planificador *(demo)* | Producción / RRHH | Planificador prescriptivo con equipo sintético |
| 06 · Modelos y Backtest | Analista | Zoológico de pronósticos + selección + intervalos |

## Metodología destacada

### Modelo de productividad
- **Crowding por variedad (β):** `kg_h_senior(s) = max(a·(1−β·s), 0.70·a)`
- **Productividad mixta:** `kg_h_mixto = (1−s)·kg_h_senior + s·kg_h_nuevo`
- El share de nuevos `s` es un **output** del estado actual, nunca un input.

### Zoológico de pronósticos (Paso 3a)
Cuatro métodos explicables compiten por WMAPE holdout sobre las últimas 4 semanas:

| Método | Qué captura | Requiere |
|--------|-------------|----------|
| `mov_avg` | Baseline | 6 observaciones |
| `seasonal` | Forma anual | 52 + 4 observaciones |
| `holt` | Tendencia | ≥ 2 |
| `theta` | Tendencia + nivel suavizado | ≥ 3 |

Intervalos de predicción al 80%: `ŷ ± 1.28·σ·√h`.

### Comparador RRHH (Paso 3b)
Para cada predio con gap de horas, tres opciones comparadas lado a lado:

- **A · Horas extra** (fatiga = 95%)
- **B · Contratar N personas** (estrés tasado en horas perdidas → COP y kg)
- **C · Mixto** (horas extra al tope + contratar el residuo)

Break-even: semana a partir de la cual contratar acumula menos costo que horas extra para el mismo kg.

## Estructura del repositorio

```
cosecha-public/
├── src/
│       └── berrix/
│           ├── app_cosecha_public.py     # Dashboard Streamlit (ES/EN)
│           ├── forecaster.py             # Zoológico de pronósticos + backtest holdout
│           └── assets/
│               └── ag6.svg               # Logo de marca
├── data/
│       └── public/                       # Dataset k-anonymized (6 parquet tables)
│           ├── hechos_semana.parquet
│           ├── hechos_mes_variedad.parquet
│           ├── curva_public.parquet
│           ├── crowding_public.parquet
│           ├── params_public.parquet
│           ├── estacionalidad_public.parquet
│           ├── README.md
│           └── validacion.txt
├── docs/
│       └── public/                       # Documentos de metodología Español
│           ├── cerebro-cosecha-public.md
│           ├── decisiones-estadisticas-cosecha-public.md
│           ├── guia-comite-cosecha-public.html
│           └── en/                       # Traducciones Inglés
├── .streamlit/config.toml
├── requirements.txt
└── uv.lock
```
> 👨🏻‍💻 **Nota técnica:** `berrix es el nombre del paquete interno (contracción de berries + analytics) que alberga el motor analítico y los módulos de pronóstico de esta suite de proyectos. Se mantiene como namespace para preservar la coherencia arquitectónica con el repositorio acompañante (berries-dashboard).

## Ejecución local

### Opción A · uv (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/ag-agrodata/cosecha-public.git
cd cosecha-public

# Sincronizar e instalar dependencias
uv sync

# Corre el simulador
uv run streamlit run src/berrix/app_cosecha_public.py
```

### Opción B · pip

```bash
# Clonar el repositorio
git clone https://github.com/ag-agrodata/cosecha-public.git
cd cosecha-public

# Crear el entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Corre el simulador
streamlit run src/berrix/app_cosecha_public.py
```

Abre `http://localhost:8501`. El toggle **ES | EN** está arriba a la derecha del tablero.

## Reglas de anonimización

Toda celda publicada cumple:

1. **k ≥ 5** trabajadores únicos por celda
2. **≥ 10** registros (horas) por celda
3. **Sin identificadores directos** (IDs y nombres eliminados)
4. **Sin identificadores indirectos** (bloques agregados a nivel predio)
5. **Jittering temporal** (fechas redondeadas a semana ISO)
6. **Top-coding** en p99.5 para kg/h
7. **Sin correlación con NDA** (dominios comercial y financiero excluidos)

Reporte de validación: [`data/public/validacion.txt`](data/public/validacion.txt).

## Linaje del dato

- **Fuente:** registros operativos del ERP, anonimizados en origen por el cliente.
- **Cobertura:** 2022-12 → 2025-05, 118,329 registros horarios.
- **Procesamiento:** pipelines Polars → tablas parquet k-anonimizadas.

Los pipelines internos (`build_public.py`, `validar_public.py`) **no** forman parte de esta versión pública, ya que requieren acceso al dataset granular (no público).

## Proyecto Acompañante: Analítica Agroindustrial Integral

Este repositorio es parte de un ecosistema mayor. Se complementa con [berries-dashboard](https://github.com/ag-agrodata/berries-dashboard) para cubrir el ciclo completo del negocio: mientras esta herramienta resuelve cuellos de botella operativos (rendimiento, personal y costos), `berries-dashboard` traduce los datos de ventas B2B en acciones estratégicas para el comité comercial.

## Stack tecnológico

- **Lenguaje:** Python 3.12 / 3.13
- **Datos:** [Polars](https://pola.rs/) (DataFrames ultrarrápidos)
- **UI:** [Streamlit](https://streamlit.io/) (tablero + widgets interactivos)
- **Gráficos:** [Plotly](https://plotly.com/python/) (Plotly Express + Graph Objects)
- **Pronósticos:** implementaciones NumPy propias (sin dependencias de ML)
- **Hosting:** Streamlit Community Cloud

## Licencia

Este proyecto usa una **licencia dual**:

- **Código** (`src/`, `.streamlit/`, `requirements.txt`): [Licencia MIT](LICENSE).
- **Datos** (`data/public/`): [Acuerdo de Uso de Datos](LICENSE) — no comercial,
  sin re-identificación, requiere atribución.
- **Documentación** (`docs/`, READMEs): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

> ⚠️ Los datasets k-anonimizados se publican con fines demostrativos.
> Cualquier intento de re-identificar individuos o vincular los datos con
> una organización específica está expresamente prohibido. Consulta el
> archivo [LICENSE](LICENSE) para los términos completos.

---

<div align="center">

**Andrés Gómez**<br/>
Analista de Datos Agroindustriales<br/>
"Transformo la complejidad del campo en decisiones basadas en datos."

[🌐 Portafolio](https://github.com/ag-agrodata) · [📧 Contacto](mailto:afgomez.agroindustrial@gmail.com)

</div>
