# Dataset público · Cosecha operativo (anonimizado)

Reglas aplicadas (Doc 3, sección 7):
- k ≥ 5 trabajadores únicos por celda publicada.
- Celdas ≥ 10 registros (horas).
- Sin identificadores directos (cosechador_id, nombre_cosechador eliminados).
- Sin bloques (identificador indirecto; agregados a nivel predio).
- Top-coding: kg/h truncado en p99.5 = 10.23.
- Sin fechas exactas (solo año / semana ISO / mes).

Tablas:
- hechos_semana.parquet        : semana × predio × sistema (668 celdas, 99.5% del kg).
- hechos_mes_variedad.parquet  : mes × predio × sistema × variedad (665 celdas, 99.4% del kg).
- curva_public.parquet         : curva de aprendizaje por semanas activas (40 bins).
- crowding_public.parquet      : semana × predio × modalidad (140 celdas).
- params_public.parquet        : parámetros de modelo por variedad (a, beta, categoria, kg_h_nuevo).
- estacionalidad_public.parquet: estacionalidad semanal derivada de Tabla 1.

Generado por build_public.py · Proyecto Cosecha operativo · referencias de cliente omitidas por confidencialidad.
