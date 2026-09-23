# Auditoría de Calidad de Datos — Tres Bases

Evaluación de las tres bases de datos del proyecto sobre los siete puntos solicitados: **valores nulos, duplicados, tipos de datos incorrectos, valores inconsistentes, valores atípicos, columnas innecesarias y problemas de formato**.

| # | Base | Archivo crudo (`data/raw/`) | Fuente | Registros | Variables | Periodo |
|---|---|---|---|---|---|---|
| 1 | ICETEX | `Comportamiento_de_Cartera_y_Crédito._20260914.csv` | ICETEX | 1.240 | 11 | 2022-Q1 → 2026-Q2 (trimestral) |
| 2 | Superfinanciera (SFC) | `Distribución_de_cartera_por_producto_20260914.csv` | Superintendencia Financiera | 110.969 | 34 | 2015-01 → 2026-06 (mensual, 138 meses sin huecos) |
| 3 | BANREP — IEFIC 2017-2018 | `BANREP-IEFIC-2017-2018.xml` | Banco de la República | 331 variables documentadas | 4 campos | Metadatos de encuesta |

La auditoría de las bases 1 y 2 se ejecutó sobre los datos limpios de `data/processed/` (generados por `src/utils/loaders.py`); la base 3 se audita sobre el codebook XML crudo, ya que es un documento de metadatos (no contiene microdatos). Cuando el hallazgo proviene del archivo crudo se indica.

---

# Base 1 — ICETEX (`Comportamiento_de_Cartera_y_Crédito._20260914.csv`)

## 1.1 Valores nulos

**0 nulos** (verificado en las 11 columnas × 1.240 filas). Base completa; no requiere imputación.

## 1.2 Duplicados

- **Filas exactas duplicadas: 0.**
- **Duplicados por clave natural** `(fecha_corte, departamento, epoca_cartera)`: **0**. Cada combinación aparece una única vez.

## 1.3 Tipos de datos incorrectos

En el archivo crudo **todo llega como texto**; la corrección se aplica en `load_icetex()`:

| Problema en crudo | Columnas | Corrección |
|---|---|---|
| Fecha como texto (`2022 Mar 31 12:00:00 AM`) | `FECHA CORTE` | `pd.to_datetime` con `format='%Y %b %d %I:%M:%S %p'` |
| Montos con `$` y comas (`$ 14,629,091`) | saldos | `parse_monto_icetex` → `float` |
| Conteos con comas (`3,355`) | créditos | `parse_cantidad` → `float` |
| Porcentaje como texto (`34.21%`) | indicador | `parse_porcentaje` → `float` |

Tras la carga no queda ninguna columna numérica como texto.

## 1.4 Valores inconsistentes

| Hallazgo | Evidencia | Tratamiento |
|---|---|---|
| `epoca_cartera` con 4 variantes de mayúsculas | `AMORTIZACION` (482), `ESTUDIOS` (482), `Estudios` (140), `Amortizacion` (136) | normalizar antes de agrupar |
| `departamento` con **46 valores** (Colombia tiene 32 + Bogotá) | ver detalle abajo | mapear a catálogo DANE |
| Conteos que no suman | en **68 filas** `al_dia + mora<90 + mora>90 ≠ total_creditos` | usar `total_creditos` como valor oficial |
| Indicador no replicable | en **1.189 filas (96%)** el indicador difiere >0.5 pp de `saldo_mora/saldo_total`; tampoco replica con `saldo_mora/saldo_capital` ni con los conteos | usar el valor publicado, no recalcular |

Detalle de `departamento`: variantes sin espacio (`DISTRITOCAPITAL`, `LAGUAJIRA`, `NORTEDESANTANDER`, `SANANDRES`, `VALLEDELCAUCA`) junto a las versiones con espacio; **ciudades como departamento** (`CARTAGENA` 1 fila, `YOPAL` 1 fila); **sin información** en 14 filas (`SIN INFO`, `SIN INFORMACION`, `Sin Informacion`, `SinInformacion`, `NO REGISTRA`) y `EXTRANJERO` (36 filas).

## 1.5 Valores atípicos

Detectados con regla IQR (1.5 × rango intercuartílico):

| Columna | Atípicos | % | Máximo |
|---|---|---|---|
| `saldo_total` | 101 | 8.1% | $1.66 billones |
| `saldo_mora` | 157 | 12.7% | $33.7 mil millones |
| `indicador_cartera_vencida` | 30 | 2.4% | 100% |
| `total_creditos` | 85 | 6.9% | 49.291 |

- **Diagnóstico:** atípicos **estructurales, no errores** — el crédito educativo se concentra en departamentos grandes (Antioquia, Valle, Cundinamarca) frente a Vaupés o Guainía, con 3 órdenes de magnitud de diferencia en saldos.
- **Tratamiento:** no se eliminan ni recortan; en visualizaciones se usan escalas logarítmicas o percentiles.
- Coherencia verificada: ninguna fila con `saldo_mora > saldo_total` ni indicador > 100%.

## 1.6 Columnas innecesarias

**Ninguna crítica.** `total_creditos` es derivable de la suma de los tres conteos, pero se conserva como columna de control (permite detectar las 68 filas inconsistentes del punto 1.4).

## 1.7 Problemas de formato

| Problema | Solución aplicada |
|---|---|
| Montos con formato `$ 14,629,091` (coma = miles) | `parse_monto_icetex` |
| Fecha no estándar `2022 Mar 31 12:00:00 AM` | parseo con formato explícito |
| Porcentaje con `%` pegado | `parse_porcentaje` |
| Export a Excel/CSV | `utf-8-sig` (BOM) para compatibilidad |

---

# Base 2 — Superfinanciera (`Distribución_de_cartera_por_producto_20260914.csv`)

## 2.1 Valores nulos

**461 nulos (0.01% de 3.77 millones de celdas)**, concentrados en:

| Columna | Nulos | % |
|---|---|---|
| `riesgo_A_clientes` | 460 | 0.41% |
| `riesgo_D_clientes` | 1 | 0.001% |

- **Causa:** la Superfinanciera no publica la calificación A en algunos cortes de ciertas entidades pequeñas.
- **Impacto:** mínimo; no afecta KPIs agregados.
- **Tratamiento:** se dejan como `NaN` (imputar a 0 cambiaría el significado: "cero clientes-A" ≠ "no reportado"). Al agregar se usa `sum()`, que los ignora.

## 2.2 Duplicados

**Filas exactas duplicadas: 0.** Pero hay dos hallazgos sobre claves:

1. **Falsa colisión por clave incompleta:** 6.689 filas comparten `(codigo_entidad, fecha, producto, renglon)`. La causa es que el código de entidad **no es único entre tipos de entidad**: el código `1` es a la vez Banco de Bogotá (tipo 1, banco) y Cooperativa Financiera de Antioquia (tipo 32, cooperativa). La clave correcta debe incluir `tipo_entidad`.
2. **986 claves repetidas aun con la clave completa** `(tipo_entidad, codigo_entidad, fecha, producto, renglon)` — 1.972 filas. Se verificó que **ninguna** tiene saldos idénticos: el reporte publica filas desglosadas que comparten renglón (p. ej. Giros & Finanzas C.F. reporta el renglón 10 de tarjetas en dos filas: $0 y $5.555 millones).

- **Impacto:** asumir unicidad de clave contaría dos veces los mismos renglones.
- **Tratamiento:** no se eliminan (no son copias); todo análisis agrega con `groupby().sum()`.

## 2.3 Tipos de datos incorrectos

En crudo todo es texto; correcciones aplicadas en `load_sfc()`:

| Problema en crudo | Corrección |
|---|---|
| Montos `37.651.351.298` / `32.878.868.825,55` | `parse_monto_sfc` → `float` |
| Fecha `31/01/2015` | `to_datetime` con `format='%d/%m/%Y'` |
| Encabezados ilegibles → lectura sin cabecera | nombres por posición (`SFC_COLUMNS`) |

**Hallazgo residual:** las columnas de conteo (`riesgo_*_clientes`) se esperarían enteras, pero **45.538 filas (41%) tienen decimales** (p. ej. `6.176` clientes): la fuente publica conteos promedio/ponderados. Se mantienen como `float`. Verificado: ninguna columna numérica quedó como `object` tras la limpieza.

## 2.4 Valores inconsistentes

| Hallazgo | Evidencia |
|---|---|
| Saldo vigente mayor que el total | 30 filas |
| Vigente = 0 con saldo total > 0 | 998 filas (entidades que no desglosan lo vigente) |
| Agregados de mora incoherentes entre sí | en 37.134 filas (33%) `vencida_1_3_meses < vencida_1_2_meses`, siendo el primero un agregado que debería contener al segundo |
| Nombres de entidad | sin variantes conflictivas: cada `(tipo_entidad, codigo_entidad)` tiene un único nombre |

## 2.5 Valores atípicos

| Columna | Atípicos | % | Máximo |
|---|---|---|---|
| `saldo_total_cartera` | 16.387 | 14.8% | $49.6 billones |
| `saldo_vigente` | 16.354 | 14.7% | $48.8 billones |
| `riesgo_E_saldo` | 19.021 | 17.1% | $2.09 billones |
| `clientes_mora_mas_30` | 18.287 | 16.5% | **999** |

- **Diagnóstico:** atípicos **estructurales** — la cartera colombiana está extremadamente concentrada (bancos grandes vs. compañías de financiamiento pequeñas), por lo que 15–17% de atípicos es esperado.
- **Tratamiento:** no se eliminan ni winsorizan (se distorsionaría la concentración real); se usan escalas logarítmicas o percentiles en visualizaciones.
- **Sospecha de censura en la fuente:** `clientes_mora_mas_30` tiene máximo **999**, con 5 filas exactamente en 999 y 51 filas ≥ 990 — patrón típico de cifra censurada "999+". Interpretar esos valores como "al menos 999".

## 2.6 Columnas innecesarias

| Columna(s) | Motivo | Decisión |
|---|---|---|
| `desc_renglon` | redundante: describe lo mismo que `producto` + `renglon` | se conserva por legibilidad, no se usa en modelos |
| `unicap` | código técnico del formato de reporte, sin valor analítico | idem |
| 7 columnas de mora solapadas (`vencida_1_3`, `1_4`, `3_6`, `mas_4`, `mas_6`, `mas_12`, `mas_18`) | agregados derivables de los tramos base; sumarlas produce doble conteo | para análisis se usa un solo conjunto no solapado (`1_2`, `2_3`, `3_4`, `4_6`, `6_12`, `12_18`) y/o `(saldo_total − vigente)/saldo_total` |

## 2.7 Problemas de formato

| Problema | Solución aplicada |
|---|---|
| **Montos con convención colombiana inversa a ICETEX** (punto = miles, coma = decimal) | parsers separados `parse_monto_icetex` / `parse_monto_sfc` — usarlos indistintamente corrompería valores ×1000 |
| Convención decimal mixta dentro del archivo: conteos de clientes con punto decimal (`6.176`) junto a enteros planos | parseo tolerante a `float` |
| Encabezados con mojibake (`CRÉDITO` → `CR�DITO`) y numerados `(1)…(26)` | lectura `header=None` + nombres por posición |
| Fecha `31/01/2015` (día primero) | `format='%d/%m/%Y'` |
| Export a Excel/CSV | `utf-8-sig` |

---

# Base 3 — BANREP IEFIC 2017-2018 (`BANREP-IEFIC-2017-2018.xml`)

*Naturaleza distinta: es un codebook DDI (estándar ICPSR) — documenta las 331 variables de la Encuesta de Ingresos y Gastos; no contiene microdatos. La auditoría aplica sobre los metadatos.*

## 3.1 Valores nulos

Sobre el diccionario extraído (331 variables × 4 campos: `name`, `label`, `question`, `type`):

| Campo | Vacíos | Detalle |
|---|---|---|
| `name` | 0 | — |
| `label` | 0 | — |
| `question` | **3** | `DIRECTORIO`, `DEPARTAMENTO`, `MUNICIPIO` — variables de identificación/geográficas que no son preguntas de encuesta |
| `type` | 0 | — |

**Tratamiento:** los 3 vacíos son esperables por diseño; se dejan sin pregunta.

## 3.2 Duplicados

- El XML define cada variable **dos veces**: una por archivo (`F17` = IEFIC_2017, `F18` = IEFIC_2018) → **662 elementos `<var>` para 331 nombres**; los 331 nombres aparecen duplicados entre años.
- Verificado: **0 variables con etiqueta distinta entre 2017 y 2018** (las definiciones son idénticas).
- Tras deduplicar por nombre: **331 variables únicas, 0 duplicados exactos**.

**Tratamiento:** `load_iefic_codebook()` deduplica por nombre (`drop_duplicates`).

## 3.3 Tipos de datos incorrectos

- El atributo `intrvl` tipifica cada variable: **206 discretas (62%) y 125 continuas (38%)**. Sin errores de tipificación.
- El codebook **no documenta las categorías de las variables discretas** (0 elementos `<catgry>` en las 662 definiciones): las discretas solo traen etiqueta y pregunta, sin el catálogo de valores. Es una limitación del documento, no un error reparable.
- El XML es la única de las tres bases que **ya viene estructurada** (no hay que convertir tipos).

## 3.4 Valores inconsistentes

| Hallazgo | Evidencia | Impacto |
|---|---|---|
| Nomenclatura mixta de variables | 319 con prefijo `P` (preguntas: `P6050`, `P10`), 12 con nombre de palabra (`DIRECTORIO`, `CLASE`, `LLAVE`, `FEX`, `INGTOTOB`…) | cosmético; dificulta búsqueda por patrón |
| 3 variables con `label` igual al `name` (`DIRECTORIO`, `DEPARTAMENTO`, `MUNICIPIO`) | la etiqueta no aporta descripción | documentación débil en variables clave de cruce geográfico |
| Etiquetas idénticas entre los dos años | 0 discrepancias | ✔ consistente |

## 3.5 Valores atípicos

**No aplica:** el codebook contiene metadatos (nombres, etiquetas, preguntas), no observaciones numéricas. Como referencia descriptiva, el largo de las preguntas es máximo 216 caracteres (p95 = 140), sin valores extremos anómalos.

## 3.6 Columnas innecesarias

- La duplicación por año (F17/F18) es estructuralmente redundante → se colapsa al deduplicar.
- Del estándar DDI, el proyecto solo usa 4 campos (`name`, `labl`, `qstnLit`, `intrvl`); el XML trae además ubicación en archivo, pesos y metadatos de productores que no se extraen.
- De las 331 variables documentadas, el análisis usa ~10 (`INGTOTOB`, `INGRESO_COMPLETO`, `P6050`, `P10`, `DEPARTAMENTO`, `MUNICIPIO`, `CLASE`, bloque `P2439`–`P2464`).

## 3.7 Problemas de formato

| Problema | Solución aplicada |
|---|---|
| XML DDI 1.2.2 con namespace ICPSR (no parseable con parser simple) | `lxml` + XPath con namespace |
| Encoding UTF-8 declarado y verificado (0 caracteres corruptos al parsear) | — |
| Bloques `CDATA` y metadatos multi-línea en productores | `findtext`/`xpath` tolerantes |
| El codebook no trae el catálogo de valores de las discretas | limitación de la fuente; se documenta |
| Export del diccionario | `data/processed/iefic_diccionario.csv` en `utf-8-sig` |

---

# Síntesis comparativa

| Punto | ICETEX | SFC | BANREP → `BANREP-IEFIC-2017-2018.xml` |
|---|---|---|---|
| Nulos | ✅ 0 | ⚠️ 461 (0.01%, calif. A) | ⚠️ 3 sin pregunta (esperable) |
| Duplicados | ✅ 0 | ⚠️ 0 exactos; 986 claves repetidas → agregar, no deduplicar | ⚠️ duplicada por año → dedup (331 únicas) |
| Tipos incorrectos | ✅ corregidos en carga | ✅ corregidos; conteos con decimales por diseño | ✅ ya tipificadas (206 discretas / 125 continuas) |
| Inconsistentes | ⚠️ `epoca` (4 variantes), 46 "departamentos", 68 conteos, indicador no replicable | ⚠️ 30 vigente>total, agregados de mora incoherentes (33%) | ⚠️ nomenclatura mixta; sin catálogo de valores |
| Atípicos | ⚠️ estructurales (8–13%) | ⚠️ estructurales (15–17%) + posible censura en 999 | ➖ no aplica (metadatos) |
| Columnas innecesarias | ✅ ninguna crítica | ⚠️ 7 agregados solapados, `unicap`, `desc_renglon` | ⚠️ duplicación por año; 4 campos de ~10 del DDI |
| Formato | ✅ resuelto en `loaders.py` | ✅ resuelto (ojo: convención de montos inversa a ICETEX) | ✅ resuelto con `lxml` |

**Conclusión general:** las tres bases quedan aptas para el análisis tras la capa de carga de `src/utils/loaders.py`. Puntos vigilados: normalizar `epoca_cartera` y `departamento` (ICETEX); incluir `tipo_entidad` en cualquier clave de entidad y agregar en vez de deduplicar (SFC); usar el codebook IEFIC como catálogo documental, no como fuente de datos observados.

---

*Auditoría ejecutada el 2026-09-22 con pandas y lxml sobre `data/raw/` y `data/processed/`; verificaciones reproducibles con `load_icetex()` / `load_sfc()` / `load_iefic_codebook()` de `src/utils/loaders.py`.*
