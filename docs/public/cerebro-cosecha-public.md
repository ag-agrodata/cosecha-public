> **Versión pública anonimizada** · sin identificadores de cliente · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales.

# Cerebro Cosecha · Operativo
> Fuente única de verdad del proyecto operativo de productividad de cosecha.
> Separado estrictamente de cualquier proyecto comercial bajo NDA.
> Última actualización: sesión de cierre del Paso 3 + Pestaña 06.

## 0 · Identidad del proyecto
- **Nombre:** Cosecha (Operativo).
- **Tipo:** Dashboard operativo + planificador prescriptivo de cosecha de arándanos.
- **Cliente:** Productor colombiano (datos anonimizados de origen).
- **Stack:** Python 3.13 · uv · Polars · Streamlit 1.65 · Plotly · NumPy.
- **Confidencialidad:** dataset anonimizado; el tablero no individualiza ni perfila trabajadores (agregados por cohorte/categoría).

## 1 · Contexto de negocio
- Cultivo de arándanos en invernadero; el clima tiene impacto despreciable (controlado).
- Dos predios (Predio_1, Predio_2); 28 bloques/invernaderos; múltiples sistemas de siembra y variedades por bloque.
- La cosecha es la operación crítica: la fruta madura no espera; el rezago (látigo) degrada calidad y vida poscosecha.
- Política operativa: "todo el bloque se cosecha siempre", cumplida de forma acumulada en la semana (múltiples visitas), no por evento.

## 2 · Flujo operativo semanal
1. **Miércoles:** cierre de seguimiento de cosecha.
2. **Jueves 9 am:** reunión de planificación (Producción + Cosecha). Inputs: fruta pendiente, fecha de última cosecha, frecuencia por variedad, látigo, mano de obra disponible, kg proyectados vs cosechados.
3. **Día a día:** revisión de ruta; aplazamientos por madurez (informa Agronomía) o por falta de mano de obra (PEPS).
4. **Sábado:** estimación de fruta pendiente; si aplica, horas extra sábado/dominical y prioridad en packing/despachos.

## 3 · Roles y audiencias
| Rol | Usa | Para qué |
|---|---|---|
| Producción / Cosecha | Pestañas 04, 05 | Ruta, proyección de kg, cumplimiento |
| RRHH | Pestaña 05 (Secciones 4, 7) | Faltantes, contratar vs extras, estrés |
| Gerencia / Dirección | Pestaña 06 | Presupuesto, costo, alertas |
| Analista | Pestañas 00–03, backtest | Calidad, capacidad, crowding, curva |

## 4 · Fuentes de datos y linaje
- **Entrada primaria:** CSV del ERP (20 columnas base). Sin APIs ni conectores: descarga manual → carga en Streamlit.
- **Histórico:** `data/processed/cosecha_model.parquet` (38 columnas, 2022-12 → 2025-05).
- **Agregados:** agg_capacidad, agg_crowding(+binned), corr_crowding, curva_aprendizaje, hist_logros, betas_por_variedad, param_simulador_variedad, umbral_nuevo_senior, estacionalidad_real, estacionalidad_semanal, frecuencia_cosecha, frecuencia_vs_estres.
- **Libro de planes:** `data/plans/*.parquet` (planes guardados con metadata; no toca la base operativa).
- **Diagnósticos:** diagnostico_bloques.txt; demo_erp_semanas_recientes.csv (pruebas).

## 5 · Glosario operativo
- **Combinación:** bloque × sistema × variedad. Unidad mínima de planificación.
- **Equipo base:** personal fijo por predio, móvil entre bloques (D02: 43 con ≥25% presencia).
- **Nuevo / Senior:** nuevo = ≤4 semanas activas (S08); senior = alcanza asíntota de la curva.
- **Share de nuevos (s):** fracción de HORAS trabajadas por nuevos en una combinación. Es un OUTPUT del estado actual, no un input.
- **Crowding (β):** freno que los nuevos imponen a los senior en variedades sensibles (D01).
- **Látigo:** fruta rezagada no cosechada a tiempo; se prioriza por PEPS.
- **FTE:** equivalente a tiempo completo = horas / jornada ordinaria.
- **Horas ORDINARIA / EXTRA / DOMINICAL:** tipos de hora con recargos legales (extra diurna 125%, dominical 200%).

## 6 · Decisiones consolidadas
| ID | Decisión | Justificación |
|---|---|---|
| D01 | Crowding depende de la VARIEDAD, no del predio. Tolerantes β=0 (16,19,1,20,10,24); sensibles 9(0.38), 4(0.26), 15(0.13). Fórmula kg_h_senior(s)=a·(1−β·s), piso 0.70·a | Evidencia estadística F4c |
| D02 | Grupo base = 43 trabajadores móviles entre predios | F5b |
| D03 | Presupuesto = 2,000 kg/semana (redondeo de 100 t/año) | Criterio de negocio |
| D04 | Horas extra = OUTPUT del simulador, no input | Evita sesgo de planificación |
| D07 | Variedad_4 es delicada (plagas/sobre-ablandamiento); su kg/h bajo es agronómico | Contexto agronómico |
| D09 | Comparador RRHH (contratar vs extras vs mixto) con estrés tasado en horas perdidas → COP y kg | Cierre del Paso 3 |
| D10 | Unidad operativa = combinación (bloque×sistema×variedad), no bloque completo | Diagnóstico F6a: cobertura real 44–66% por evento |
| D11 | Equipo fijo por predio, móvil entre bloques; redistribución entre predios solo excepcional | Entrevista operativa |
| D12 | Share de nuevos = OUTPUT del estado actual | Evita suponer composición de plantilla |
| D13 | Deshabilitar elementos rige desde la semana elegida; el histórico se conserva | Trazabilidad |
| D14 | Pronóstico elegido por backtest (zoológico mov_avg/seasonal/holt/theta) | Paso 3a |
> Nota: los IDs D05, D06 y D08 quedaron reservados/retirados en iteraciones previas; no se reutilizan.

## 7 · Supuestos y limitaciones
| ID | Supuesto | Valor |
|---|---|---|
| S04 | Rendimiento de la hora extra (fatiga) | 95% configurable |
| S05 | Sobrecosto de terceriza | +15% configurable |
| S06 | Split de extras | Solo diurna (125%) por defecto |
| S07 | Horizonte del punto de equilibrio | 8 semanas configurable |
| S08 | Umbral de "nuevo" | ≤4 semanas activas |
| S09 | kg/h por defecto para combinaciones sin histórico | 3.5 configurable |
- **Limitaciones conocidas:** sin datos de madurez ni clima (invernadero); huecos de captura ene-abr 2023-2024 (corregidos con 2025); sin rotación futura predecible (57% de abandonos en ventanas florales, F5d).

## 8 · Calidad del dato (gobernanza)
| Inconsistencia | Estado |
|---|---|
| Registros 2027–2033 (carga manual) | ✅ Corregido (año=2025) |
| Madrugadas Android (12 h) | ✅ Corregido (+12 h) |
| costo_hora_registro=0 en ordinarias | ✅ Imputado por tipo de hora |
| Recargo dominical 2023=2.0426 | 📋 Reportado a RRHH |
| Huecos ene-abr 2023-2024 | ⚠️ Corregido con 2025 (F5f) |

## 9 · Mapa del tablero
| Pestaña | Propósito | Audiencia |
|---|---|---|
| 00 Gobernanza | Calidad del dato, malla laboral, plantilla | Analista |
| 01 Capacidad | kg/h por predio×sistema×variedad | Analista/Producción |
| 02 Crowding | Efecto de novatos sobre senior | Analista/RRHH |
| 03 Curva | Aprendizaje nuevo→senior, logros | RRHH |
| 04 Estacionalidad | Ritmo semanal, frecuencia, riesgo de estrés | Producción |
| 05 Planificador | Proyección, motor de faltantes, comparador RRHH, backtest | Producción/RRHH |
| 06 Presupuesto | Cumplimiento anual/mensual/semanal, costo, alertas | Gerencia |

## 10 · Módulos de código
- `app_cosecha_v2.py` (tablero), `plan_ledger.py` (libro de planes), `backtest.py` (exactitud), `forecaster.py` (zoológico de pronósticos), `comparador_rrhh.py` (contratar vs extras), `exportar_csv_demo.py` (pruebas).

## 11 · Roadmap
1. **Git:** inicializar repo + commit inicial (pendiente).
2. **Documentación:** este Cerebro + Guía de Comité + Decisiones estadísticas (en curso).
3. **Versión pública:** anonimización k≥5 / celdas≥10, i18n ES/EN, deploy Streamlit Cloud.
4. **No planeado:** APIs/conectores (se mantiene CSV manual), módulo de madurez.