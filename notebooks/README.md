# Notebooks — Flujo de análisis del proyecto de Riesgo de Crédito

Cinco notebooks numerados que siguen el flujo del proyecto: exploración (EDA)
de cada fuente de datos → análisis de factores de riesgo → modelo de scoring.
Los notebooks **no se modifican** en esta fase de documentación; este README
describe su propósito, entradas, salidas y orden de ejecución.

> **Nota:** los notebooks hacen `sys.path.insert(0, "..")` para importar
> `src/utils/loaders.py`, por lo que deben ejecutarse **desde esta carpeta**
> (`notebooks/`) o con la raíz del proyecto en el PYTHONPATH.

## Orden de ejecución

```
01_eda_icetex ──┐
                ├──> 04_analisis_riesgo ──> 05_modelo_scoring
02_eda_sfc ─────┘
03_iefic_codebook  (independiente)
```

Los notebooks 01 y 02 **deben ejecutarse primero** (al menos una vez) porque
generan los CSV limpios de `data/processed/` que consumen `app.py` y
`src/utils/exportar_agregados_dashboard.py`. El 03 es independiente y el
04/05 leen los datos crudos a través de los loaders (no dependen de los CSV
procesados).

---

## 01_eda_icetex.ipynb — EDA cartera ICETEX

- **Propósito:** exploración del *Comportamiento de Cartera y Crédito* del
  ICETEX (crédito educativo por departamento de residencia del deudor).
- **Input:** `data/raw/Comportamiento_de_Cartera_y_Crédito._20260914.csv`
  (vía `load_icetex`).
- **Output:** `data/processed/icetex_limpio.csv` (vía `save_processed`).
- **Qué hace:**
  - Rango temporal, épocas de cartera y estadísticas de saldos/mora.
  - Serie temporal de la cartera total y la mora.
  - Top departamentos por % de cartera vencida y por saldo expuesto.
  - Boxplots de la distribución de mora (al día / <90 días / ≥90 días).
  - Matriz de correlaciones entre variables de riesgo.
- **Hallazgos:** cortes trimestrales; el indicador de cartera vencida varía
  fuertemente por departamento (hay casos extremos con la cartera casi toda
  vencida).

## 02_eda_sfc.ipynb — EDA cartera Superfinanciera

- **Propósito:** exploración de la *Distribución de cartera por producto* de
  la Superintendencia Financiera (SFC).
- **Input:** `data/raw/Distribución_de_cartera_por_producto_20260914.csv`
  (vía `load_sfc`; ~110.969 registros × 34 columnas).
- **Output:** `data/processed/sfc_limpio.csv` (vía `save_processed`).
- **Qué hace:**
  - Evolución de la cartera total/vigente/vencida del sistema financiero.
  - Cartera por producto en el último corte (saldo y % vencida).
  - Ranking de productos con mayor % de cartera vencida.
  - Saldos y clientes por calificación de riesgo A–E.
  - Entidades con mayor cartera vencida.
- **Hallazgos:** los productos de mayor saldo concentran la exposición, pero
  el % de vencida lo lideran microcrédito y productos de consumo.

## 03_iefic_codebook.ipynb — Codebook IEFIC (BANREP)

- **Propósito:** explorar el **codebook** (diccionario de variables, estándar
  DDI) de la Encuesta de Ingresos y Gastos / Inclusión Financiera de los
  Hogares 2017–2018 del Banco de la República. No contiene microdatos.
- **Input:** `data/raw/BANREP-IEFIC-2017-2018.xml` (vía
  `load_iefic_codebook`; requiere `lxml`).
- **Output:** ninguno (solo exploración en memoria).
- **Qué hace:**
  - Conteo de variables únicas (331 tras deduplicar F17/F18).
  - Búsqueda por palabras clave de variables de ingresos, deuda, empleo y
    patrimonio (factores clásicos de capacidad de pago).
  - Listados de variables de ingreso total/componentes y de deuda/crédito.
- **Hallazgos:** existen variables de ingreso total (`INGRESO_COMPLETO`,
  `INGTOTOB`) y componentes útiles para futuros modelos.

## 04_analisis_riesgo.ipynb — Factores de riesgo de incumplimiento

- **Propósito:** identificar qué factores (tipo de entidad, producto,
  calificación, geografía y tiempo) se asocian con el riesgo de
  incumplimiento, cruzando SFC e ICETEX.
- **Inputs:** `load_sfc` + `load_icetex` (en memoria, desde `data/raw/`).
- **Output:** ninguno persistente (visualizaciones + tabla resumen).
- **Qué hace:**
  - Evolución del % de cartera vencida del sistema.
  - Riesgo por tipo de entidad (bancos vs. no bancarias).
  - % vencida vs. % clientes en mora por producto.
  - Correlación entre calificación A–E y mora.
  - Riesgo geográfico ICETEX por departamento.
- **Hallazgos (tabla de factores):** las entidades no bancarias y los
  productos microcrédito/libranza/tarjeta concentran el mayor riesgo; la
  cartera vencida correlaciona con saldos en calificaciones C–E.

## 05_modelo_scoring.ipynb — Modelo de scoring

- **Propósito:** entrenar un clasificador que prediga si una combinación
  **entidad × producto × mes** es de **alto riesgo**.
- **Input:** `load_sfc` (en memoria).
- **Output:** ninguno persistente (modelo y métricas en memoria).
- **Qué hace:**
  - Variable objetivo: `alto_riesgo = 1` si `% vencida > P75` del sistema.
  - Ingeniería de características (composición de calificación A–E, % clientes
    en mora, etc.).
  - `RandomForestClassifier` (200 árboles, profundidad 12) con split
    estratificado 70/30.
  - Evaluación: reporte de clasificación, matriz de confusión, AUC-ROC.
  - Importancia de características y perfil medio de riesgo por producto.
- **Hallazgos:** AUC-ROC > 0.9; las características más informativas son la
  composición por calificación (D+E) y el % de clientes en mora.

---

## Requisitos

Los notebooks usan las mismas dependencias del proyecto
(`pip install -r requirements.txt`): pandas, numpy, matplotlib, seaborn,
scikit-learn y lxml. Lánzalos con:

```powershell
.venv\Scripts\python.exe -m jupyter notebook notebooks/
```
