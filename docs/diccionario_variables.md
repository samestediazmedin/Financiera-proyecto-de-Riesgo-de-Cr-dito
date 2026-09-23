# Diccionario de Variables

Descripción formal de las variables de las tres fuentes de datos del proyecto. Para cada dataset se documenta el nombre original (crudo), el nombre limpio (`data/processed/`), el tipo y la descripción.

| Fuente | Archivo crudo | Archivo limpio | Dimensiones |
|---|---|---|---|
| ICETEX | `data/raw/Comportamiento_de_Cartera_y_Crédito._20260914.csv` | `data/processed/icetex_limpio.csv` | 1.240 × 11 |
| Superfinanciera (SFC) | `data/raw/Distribución_de_cartera_por_producto_20260914.csv` | `data/processed/sfc_limpio.csv` | 110.969 × 34 |
| Banco de la República (IEFIC) | `data/raw/BANREP-IEFIC-2017-2018.xml` | `data/processed/iefic_diccionario.csv` (codebook) | 331 variables |

La carga y transformación de todas las fuentes vive en `src/utils/loaders.py`.

---

## 1. ICETEX — Comportamiento de Cartera y Crédito

Cartera de crédito educativo del ICETEX por departamento de residencia. Corte trimestral: 2022-03-31 a 2026-06-30. 46 departamentos/regiones (incluye agregados como "Exterior" y "Sin Información").

| Variable limpia | Variable original | Tipo | Descripción |
|---|---|---|---|
| `fecha_corte` | `FECHA CORTE` | datetime | Fecha de corte del reporte (trimestral). Formato original: `2022 Mar 31 12:00:00 AM` |
| `departamento` | `DEPTORESIDENCIA` | str | Departamento de residencia del deudor |
| `creditos_al_dia` | `CANTIDAD CREDITOS AL DIA` | float | N.º de créditos sin mora (al día) |
| `creditos_mora_menor_90` | `CANTIDAD CREDITOS CON MORA MENOR A 90 DIAS` | float | N.º de créditos en mora de menos de 90 días |
| `creditos_mora_mayor_90` | `CANTIDAD CREDITOS MORA MAYOR A 90 DIAS` | float | N.º de créditos en mora de más de 90 días |
| `total_creditos` | `TOTAL CREDITOS` | float | N.º total de créditos (al día + en mora) |
| `saldo_capital` | `SALDO CAPITAL` | float | Saldo de capital en COP. Formato original: `$ 14,629,091` |
| `saldo_total` | `SALDO TOTAL` | float | Saldo total (capital + intereses y otros) en COP |
| `saldo_mora` | `SALDO MORA` | float | Saldo en mora en COP |
| `indicador_cartera_vencida` | `INDICADOR CARTERA VENCIDA` | float | % de cartera vencida = `saldo_mora / saldo_total × 100`. Formato original: `34.21%` |
| `epoca_cartera` | `EPOCA CARTERA` | str | Etapa del crédito: `AMORTIZACION` (pago del préstamo) o `ESTUDIOS` (periodo de estudio, aún no paga) |

**Notas de transformación**
- Montos: coma como separador de miles, sin decimales (`parse_monto_icetex`).
- `epoca_cartera` llega con inconsistencias de mayúsculas (`Estudios`/`AMORTIZACION`); normalizar a mayúsculas/minúsculas antes de agrupar.

---

## 2. Superfinanciera (SFC) — Distribución de Cartera por Producto

Cartera del sistema financiero por entidad, producto y renglón. Corte mensual: 2015-01-31 a 2026-06-30. 32 productos (crédito rotativo, tarjetas, libre inversión, libranza, microcréditos, etc.).

### 2.1 Identificación (dimensiones)

| Variable limpia | Columna original | Tipo | Descripción |
|---|---|---|---|
| `tipo_entidad` | `TIPO_ENTIDAD` | int | Código del tipo de entidad. Valores presentes: `1` = banco, `2` = corporación financiera, `4` = compañía de financiamiento, `22` = otras entidades (FNA, FDN, Caja Militar…), `32` = cooperativa financiera |
| `codigo_entidad` | `CODIGO_ENTIDAD` | int | Código de la entidad vigilada |
| `entidad` | `NOMBREENTIDAD` | str | Razón social de la entidad |
| `fecha_corte` | `FECHA_CORTE` | datetime | Fecha de corte mensual. Formato original: `31/01/2015` |
| `unicap` | `UNICAP` | int | Código de la unidad de captura (agrupación de renglones dentro del reporte) |
| `producto` | `DESCRIP_UC` | str | Producto de crédito (32 categorías: `CRÉDITO ROTATIVO`, `TARJETAS DE CRÉDITO`, `LIBRE INVERSIÓN`, `LIBRANZA`, `VEHÍCULO`, `MICROCREDITOS…`, etc.) |
| `renglon` | `RENGLON` | int | Código del renglón dentro de la unidad de captura |
| `desc_renglon` | `DESC_RENGLON` | str | Descripción del renglón (p. ej. `CRÉDITO ROTATIVO TOTAL`) |

### 2.2 Saldos de cartera (COP)

Montos con formato original punto = miles, coma = decimal (`parse_monto_sfc`).

| Variable limpia | Columna original | Descripción |
|---|---|---|
| `saldo_total_cartera` | `(1) Saldo de la cartera…` | Saldo total de la cartera a la fecha de corte |
| `saldo_vigente` | `(2) Vigente` | Saldo al día (sin mora) |
| `vencida_1_2_meses` | `(3) Vencida 1-2 Meses` | Saldo vencido entre 1 y 2 meses |
| `vencida_2_3_meses` | `(4) Vencida 2-3 Meses` | Saldo vencido entre 2 y 3 meses |
| `vencida_1_3_meses` | `(5) Vencida 1-3 Meses` | Saldo vencido entre 1 y 3 meses (agregado) |
| `vencida_3_4_meses` | `(6) Vencida 3-4 Meses` | Saldo vencido entre 3 y 4 meses |
| `vencida_mas_4_meses` | `(7) Vencida > de 4 Meses` | Saldo vencido de más de 4 meses |
| `vencida_3_6_meses` | `(8) Vencida 3-6 Meses` | Saldo vencido entre 3 y 6 meses |
| `vencida_mas_6_meses` | `(9) Vencida +6 meses` | Saldo vencido de más de 6 meses |
| `vencida_1_4_meses` | `(10) Vencida 1-4 meses` | Saldo vencido entre 1 y 4 meses |
| `vencida_4_6_meses` | `(11) Vencida 4-6 meses` | Saldo vencido entre 4 y 6 meses |
| `vencida_6_12_meses` | `(12) Vencida 6-12 meses` | Saldo vencido entre 6 y 12 meses |
| `vencida_12_18_meses` | `(13) Vencida 12-18 meses` | Saldo vencido entre 12 y 18 meses |
| `vencida_mas_12_meses` | `(14) Vencida > 12 meses` | Saldo vencido de más de 12 meses |
| `vencida_mas_18_meses` | `(15) Vencida > 18 meses` | Saldo vencido de más de 18 meses |

> **Ojo con los agregados:** las columnas 5, 7, 8, 9, 10, 11 y 14–15 se solapan entre sí (p. ej. `vencida_3_6_meses` ⊇ `vencida_3_4_meses`). No sumarlas verticalmente; para "% de cartera vencida" usar `saldo_total_cartera − saldo_vigente` sobre `saldo_total_cartera`.

### 2.3 Clientes en mora y calificación de riesgo

| Variable limpia | Columna original | Tipo | Descripción |
|---|---|---|---|
| `clientes_mora_mas_30` | `(16) Número de clientes Mora > 30 días` | float | N.º de clientes con mora superior a 30 días |
| `riesgo_A_clientes` | `(17) Calif. Riesgo A / N.º Clientes` | float | Clientes calificados en riesgo **A** (mejor calidad, menor probabilidad de incumplimiento) |
| `riesgo_A_saldo` | `(18) Calif. Riesgo A / Saldo` | float | Saldo (COP) de los clientes calificados A |
| `riesgo_B_clientes` | `(19) Calif. Riesgo B / N.º Clientes` | float | Clientes calificados en riesgo B |
| `riesgo_B_saldo` | `(20) Calif. Riesgo B / Saldo` | float | Saldo (COP) de los clientes calificados B |
| `riesgo_C_clientes` | `(21) Calif. Riesgo C / N.º Clientes` | float | Clientes calificados en riesgo C |
| `riesgo_C_saldo` | `(22) Calif. Riesgo C / Saldo` | float | Saldo (COP) de los clientes calificados C |
| `riesgo_D_clientes` | `(23) Calif. Riesgo D / N.º Clientes` | float | Clientes calificados en riesgo D |
| `riesgo_D_saldo` | `(24) Calif. Riesgo D / Saldo` | float | Saldo (COP) de los clientes calificados D |
| `riesgo_E_clientes` | `(25) Calif. Riesgo E / N.º Clientes` | float | Clientes calificados en riesgo **E** (peor calidad, mayor probabilidad de pérdida) |
| `riesgo_E_saldo` | `(26) Calif. Riesgo E / Saldo` | float | Saldo (COP) de los clientes calificados E |

**Notas de transformación**
- El CSV se lee `header=None` y se asignan nombres por posición (`SFC_COLUMNS`) para esquivar el encoding de los encabezados.
- Conteos de clientes: coma como separador de miles (`parse_cantidad`).
- En registros "totales" de entidad, las columnas de calificación A llegan con formato distinto (`6.176` con punto decimal); el parser de montos SFC lo maneja.

---

## 3. BANREP — IEFIC 2017-2018 (codebook XML)

`BANREP-IEFIC-2017-2018.xml` es un **codebook DDI** (estándar ICPSR): no contiene microdatos, sino la documentación de las **331 variables** de la Encuesta de Ingresos y Gastos (IEFIC). El XML define cada variable dos veces (F17 = IEFIC_2017, F18 = IEFIC_2018); se deduplica por nombre.

El diccionario completo y consultable está exportado en **`data/processed/iefic_diccionario.csv`** con esta estructura:

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | str | Nombre corto de la variable (p. ej. `P6050`, `INGTOTOB`) |
| `label` | str | Etiqueta descriptiva de la variable |
| `question` | str | Literal de la pregunta del cuestionario |
| `type` | str | Tipo de intervalo (`contin` = continua, `discrete` = discreta) |

Para regenerarlo:

```python
from utils.loaders import load_iefic_codebook
codebook = load_iefic_codebook()   # 331 × 4
```

**Variables IEFIC más relevantes para el proyecto**

| Variable | Descripción |
|---|---|
| `INGTOTOB` | Ingreso total por persona |
| `INGRESO_COMPLETO` | Estado del ingreso total (1 = completo, 0 = falta algún componente) |
| `P6050` | Parentesco con el jefe del hogar |
| `P10` | Nivel educativo |
| `DEPARTAMENTO` / `MUNICIPIO` / `CLASE` | Ubicación geográfica del hogar |
| `P2439`–`P2464` | Tenencia de vivienda, año de compra, valor de venta estimado, subsidios |

---

*Generado el 2026-09-22 a partir de `src/utils/loaders.py` y los archivos crudos. Actualizar si cambian las fuentes.*
