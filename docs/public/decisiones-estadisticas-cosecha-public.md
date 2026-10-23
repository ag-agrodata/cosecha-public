> **Versión pública anonimizada** · sin identificadores de cliente · Elaborado por Andrés Gómez · Analista de Datos Agroindustriales.

# Decisiones estadísticas y componente matemático · Cosecha Operativo

> Documento de transparencia matemática del proyecto Cosecha (operativo).
> Base para la futura versión pública anonimizada.
> Separado estrictamente de cualquier proyecto comercial bajo NDA.

---

## 1 · Modelo de productividad

### 1.1 Curva de aprendizaje
El kg/h de un cosechador nuevo aumenta con las semanas activas hasta alcanzar una asíntota.
La asíntota se define como la mediana del kg/h de los top performers (regla de empresa).

**Umbral operativo de "nuevo" (S08):** ≤ 4 semanas activas.

### 1.2 Crowding (efecto β) — Decisión D01
El efecto de los novatos sobre los senior **depende de la variedad**, no del predio.

**Fórmula del kg/h del senior con share s de horas de nuevos:**

$$
kg\_h_{senior}(s) = \max\bigl(a \cdot (1 - \beta \cdot s),\; 0.70 \cdot a\bigr)
$$

Donde:
- `a` = kg/h senior sin novatos (parámetro por variedad).
- `β` = sensibilidad al crowding (0 para tolerantes, hasta 0.38 para sensibles).
- `s` = share de horas trabajadas por nuevos (output del estado actual).
- Piso 0.70·a = protección contra caídas extremas.

**Clasificación empírica (D01):**
- Tolerantes (β = 0): variedades 16, 19, 1, 20, 10, 24.
- Sensibles: Variedad_9 (0.38), Variedad_4 (0.26), Variedad_15 (0.13).

### 1.3 Fórmula mixta (modelo completo)
Combina curva de aprendizaje y crowding:

$$
kg\_h_{mixto}(s) = (1 - s) \cdot kg\_h_{senior}(s) \;+\; s \cdot kg\_h_{nuevo}
$$

Donde `kg_h_nuevo` es el kg/h del novato en su primera semana (parámetro por variedad).

**Interpretación:** un share s=1.0 (solo novatos) devuelve `kg_h_nuevo` (ritmo de novato).
Un share s=0.0 (solo senior) devuelve `kg_h_senior(0) = a`.

### 1.4 Métricas derivadas
- **kg/h efectivo:** `kg_h_mixto(s)`, con piso configurable (default 3.5 para combinaciones sin modelo).
- **% dificultad:** caída del kg/h efectivo respecto al ideal senior.

$$
\%\;dificultad = 1 - \frac{kg\_h_{mixto}}{a}
$$

0% = rinde como senior. 30% = rinde 30% menos por novatos + β.

---

## 2 · Pronóstico de kilogramos (Paso 3a)

### 2.1 Serie semanal densa
Por cada combinación, se construye una serie semanal continua (ordinal desde `week_start`) con `0` en semanas sin cosecha. Esto respeta patrones quincenales y evita el sesgo de la media móvil en puntos de giro.

### 2.2 Zoológico de métodos
| Método | Descripción | Requiere |
|---|---|---|
| `mov_avg` | Media móvil de últimas 6 cosechas (baseline) | 6 observaciones |
| `seasonal` | Naive estacional: misma semana año anterior × razón de nivel reciente | 52 + 4 observaciones |
| `holt` | Suavizado exponencial doble (nivel + tendencia, α=0.3, β=0.1) | ≥ 2 |
| `theta` | Promedio de tendencia lineal y SES con pendiente | ≥ 3 |

### 2.3 Selección por backtest holdout
Para cada grupo (variedad/bloque/predio), se entrena con datos hasta el corte y se evalúa WMAPE sobre las últimas 4 semanas (holdout). El método con menor WMAPE agrupado gana.

$$
WMAPE = \frac{\sum |forecast_t - real_t|}{\sum |real_t|}
$$

### 2.4 Intervalos de predicción (80%)

$$
[ \hat{y}_{t+h} \pm z \cdot \sigma \cdot \sqrt{h} ]
$$

- `z = 1.28` (percentil 90 para banda de 80%).
- `σ` = desviación estándar de residuos in-sample.
- Límite inferior truncado a 0 (kg no negativos).

### 2.5 Factores de recalibración
Por grupo, tras comparar pronósticos con reales:

$$
factor = \frac{\sum real}{\sum forecast}
$$

Factor < 1 → método sobreestima; > 1 → subestima. Útil para ajustar el siguiente pronóstico.

### 2.6 Regla ISO del jueves (Pestaña 06)
Cada semana ISO se asigna al mes/año del **jueves** correspondiente. Evita problemas de semanas transanuales y asegura consistencia al navegar históricamente.

---

## 3 · Motor del planificador (Pestaña 05)

### 3.1 Por combinación programada
$$
horas\_necesarias = \frac{kg\_proyectado}{kg\_h_{mixto}(s)}
$$

### 3.2 Por predio
$$
horas\_disponibles = equipo\_activo \times jornada\_ordinaria
$$
$$
gap = horas\_necesarias - horas\_disponibles
$$

### 3.3 Horas extra (D04, output)
$$
horas\_extra = \min(gap,\; equipo\_activo \times tope\_horas\_extra)
$$

Tope legal: Art. 167 CST = 12 h/semana/persona. Tope operativo configurable (default 10 h).

### 3.4 Faltante de personal
$$
gap\_restante = gap - horas\_extra
$$
$$
faltante\_personas = \lceil gap\_restante / jornada\_ordinaria \rceil
$$

---

## 4 · Comparador RRHH (Paso 3b, D09)

### 4.1 Opción A — Horas extra
$$
kg_A = horas\_extra \times kg\_h_{predio} \times fatiga
$$
$$
costo_A = horas\_extra \times rate \times 1.25
$$

- `fatiga` = 0.95 (S04, configurable).
- `rate` = costo hora ordinaria promedio del predio.

### 4.2 Opción B — Contratar N personas
$$
N = \lceil gap / jornada\_ordinaria \rceil
$$
$$
kg_{B,w1} = N \times jornada \times kg\_h_{nuevo}
$$
$$
costo_B = N \times jornada \times rate \times (1 + sobrecosto)
$$

- `sobrecosto` = 0.15 (S05, configurable, administración/dotación de terceriza).

**Estrés tasado en horas perdidas:**

$$
s_{new} = \frac{s_{actual} \cdot horas\_base + horas\_new}{horas\_tot}
$$

$$
lost\_h = \max\bigl(0,\; kg_{predio} \cdot (\frac{1}{kg\_h_{mixto}(s_{new})} - \frac{1}{kg\_h_{mixto}(s_{actual})})\bigr)
$$

$$
estres\_COP = lost\_h \times rate \quad\quad estres\_kg = lost\_h \times kg\_h_{mixto}(s_{new})
$$

Descomposición del estrés:
- **Aprendizaje:** pérdida por kg_h_nuevo < kg_h_senior (siempre).
- **Crowding:** pérdida adicional por β>0 cuando sube el share de nuevos (solo en variedades sensibles).

### 4.3 Opción C — Mixto
Horas extra al tope + contratar el residuo. Costo y estrés proporcionales a la fracción contratada.

### 4.4 Punto de equilibrio (S07)
Proyección a `horizonte` semanas (default 8). Para cada semana w se acumula costo y kg de A y B. `break_even` = primera semana donde B acumula menos costo que A para el mismo kg.

Si `gap` es transitorio (≤ 2 sem), gana A. Si es estructural (≥ horizonte), gana B.

---

## 5 · Backtest (exactitud)

### 5.1 Métricas
- **WMAPE por método:** robusto a semanas pequeñas.
- **Sesgo:** `mean(forecast − real)`. Positivo = sobre-proyección.
- **Clasificación operativa:**
  - Acierto: programado y cosechado.
  - Sobre-proyección: programado y no cosechado.
  - No programado pero cosechado: látigo.
  - Correctamente no programado.

### 5.2 Rejilla con cero explícito
Para clasificar bien "sobre-proyección" y "correctamente no programado", la rejilla de reales incluye **todas** las combinaciones × semanas objetivo, con `kg_real = 0` donde no hubo cosecha. Evita el sesgo de solo considerar semanas con kg > 0.

---

## 6 · Estacionalidad y frecuencia

### 6.1 Estacionalidad semanal
Amplitud pico/valle = **7.3×**. Pico real: semana 18 (abril). Valle: semana 1 (enero).

**Nota:** ene–abr basado solo en 2025 por huecos de captura en 2023-2024.

### 6.2 Frecuencia de cosecha
- **Semanal (≥90%):** Sistema_3.
- **Quincenal (45-89%):** Sistema_10.
- Un bloque puede contener combinaciones semanales y quincenales; por eso la unidad operativa es la combinación, no el bloque (D10).

### 6.3 Cobertura real por evento de cosecha
- Sistemas: 44% promedio por evento.
- Variedades: 66% promedio por evento.
- Solo 3% de los eventos cosechan el bloque completo.

**Conclusión:** "Todo el bloque se cosecha siempre" se cumple **acumulado en la semana** (múltiples visitas), no por evento.

---

## 7 · Reglas de anonimización (versión pública)

Para el deploy público, todo agregado debe cumplir:

1. **k ≥ 5:** cualquier agregado por grupo debe contener ≥ 5 trabajadores únicos. Grupos menores se suprimen o se fusionan con grupos hermanos.
2. **Celdas ≥ 10:** celdas de tablas cruzadas con conteo < 10 se suprimen.
3. **Sin identificadores directos:** `cosechador_id` y `nombre_cosechador` eliminados; solo agregados por cohorte/categoría.
4. **Sin identificadores indirectos:** bloques pequeños (< 5 trabajadores) se agregan a nivel predio.
5. **Jittering temporal:** fechas exactas de logros se redondean a semana.
6. **Top-coding:** valores extremos (p99.5+) se truncan.
7. **Sin correlación con NDA:** todo el análisis se restringe al ámbito operativo (productividad de cosecha); los dominios comerciales y financieros quedan fuera.

---

## 8 · Limitaciones y supuestos no modelados

- **Sin datos de madurez:** la fruta rezagada por inmadurez se detecta por ausencia de cosecha + criterio agronómico, no por sensor.
- **Sin impacto climático:** invernadero, impacto despreciable.
- **Sin rotación futura predecible:** 57% de abandonos en ventanas florales (competencia florícola) es estacional pero no predecible a nivel individual.
- **Huecos de captura:** ene-abr 2023-2024 corregidos con datos 2025; cualquier análisis de tendencia en ese rango debe tomarse con cautela.

---

## 9 · Referencias

- **Dataset:** histórico anonimizado 2022-12 → 2025-05, 118,329 registros.
- **Marco laboral:** Ley 2101 de 2021 (reducción progresiva de jornada).
- **Art. 167 CST:** tope de horas extra.
- **Malla laboral validada:** 48h (dic-22→jun-23) → 47h (jul-23→jun-24) → 46h (jul-24→may-25).
