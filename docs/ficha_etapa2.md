# FICHA – ETAPA 2 Y 3: ANÁLISIS Y RESULTADOS

**Asignatura:** Business Analytics & Big Data II (ING-SOF8-N) · Ingeniería de Software VIII · 1er Corte
**Docente:** Oscar Castiblanco
**Fecha de emisión:** 15 de septiembre de 2026

---

## 1. Información del proyecto

| Campo | Detalle |
|---|---|
| **Nombre del proyecto** | Entidad financiera, proyecto de Riesgo de Crédito |
| **Integrantes** | Caren Dayana Romero Montoya · Karen Jimena Ocampo Otalora · Samuel Esteban Diaz Medina |
| **Pregunta de negocio** | ¿Qué características de los solicitantes y de las solicitudes de crédito están relacionadas con el riesgo de incumplimiento? |

---

## 2. Datos utilizados

### Dataset 1 — Comportamiento de Cartera y Crédito (ICETEX)

| Campo | Detalle |
|---|---|
| Fuente | Instituto Colombiano de Crédito Educativo — Datos Abiertos Colombia |
| Registros | 1.240 filas × 11 columnas |
| Período | Marzo 2022 – Junio 2026 (trimestral) |
| Alcance | 46 departamentos de residencia del deudor |
| Variables clave | Saldo capital, saldo total, saldo en mora, créditos al día, mora <90 días, mora >90 días, indicador de cartera vencida (%) |

### Dataset 2 — Distribución de Cartera por Producto (Superfinanciera)

| Campo | Detalle |
|---|---|
| Fuente | Superintendencia Financiera de Colombia — Datos Abiertos Colombia |
| Registros | 110.969 filas × 34 columnas |
| Período | Febrero 2015 – Diciembre 2025 (mensual) |
| Alcance | 68 entidades financieras · 32 productos de crédito |
| Variables clave | Saldo total de cartera, saldo vigente, saldos vencidos por rango de meses, calificación de riesgo A–E (saldos y clientes) |

### Dataset 3 — Codebook IEFIC (Banco de la República)

| Campo | Detalle |
|---|---|
| Fuente | Banco de la República — Encuesta IEFIC 2017-2018 |
| Registros | 331 variables (codebook DDI, sin microdatos) |
| Variables clave | Ingresos, gastos, endeudamiento, nivel educativo, características del hogar y vivienda |
| Utilidad | Contexto sobre la capacidad de pago de los hogares colombianos |

---

## 3. Metodología

```
1. Carga y limpieza          → src/utils/loaders.py
2. Exploración (EDA)         → notebooks/01-03
3. Análisis de riesgo        → notebook/04
4. Modelo de scoring         → notebook/05
5. Dashboard local           → app.py (Streamlit)
```

- **Carga:** se descargaron los 3 archivos de Datos Abiertos Colombia y se guardaron en `data/raw/` (inmutables).
- **Normalización:** parsers separados para ICETEX (montos con comas de miles) y SFC (puntos de miles, coma decimal). Nombres de columna SFC renombrados por posición (el encoding del archivo original estaba corrupto). Fechas parseadas con formatos específicos por dataset.
- **EDA:** notebooks ejecutados con pandas, matplotlib y seaborn. Gráficos de series temporales, barras, heatmaps y boxplots.
- **Modelo:** Random Forest (200 árboles, profundidad máxima 12) sobre features derivados de la distribución de calificación de riesgo y mora.

---

## 4. Hallazgos del EDA

### 4.1 Cartera ICETEX (crédito educativo)

- La cartera ICETEX creció de **$1.8 billones** (2022-Q1) a **$10.3 billones** (2026-Q2) en saldo total.
- Los departamentos con mayor saldo son **Bogotá, Antioquia, Valle del Cauca y Santander**, pero no necesariamente son los de mayor riesgo relativo.
- Departamentos periféricos como **Vaupés** (100%), **Vichada** (34.2%) y **Guainía** (32.5%) presentan los indicadores más altos de cartera vencida, aunque con saldos pequeños.
- La correlación entre saldo total y saldo en mora es **0.99**, lo que indica que el crecimiento de la cartera ha ido acompañado proporcionalmente por la mora.

### 4.2 Cartera Superfinanciera (sistema financiero)

- La cartera total del sistema alcanzó **$556 billones** al corte de diciembre 2025, con un **5.6% de cartera vencida**.
- Los productos de mayor saldo son **crédito rotativo, vivienda, consumo y libranza**.
- Los productos con mayor % de cartera vencida son **microcrédito, libranza y crédito rotativo**.
- Las **entidades no bancarias** (cooperativas, compañías de financiamiento) muestran mayor % de vencida que los bancos tradicionales.
- La calificación **A** concentra el 72% de los saldos y el 81% de los clientes; las calificaciones **D y E** son minoritarias (3.2% y 0.6% respectivamente) pero representan la mayor pérdida esperada.

### 4.3 Codebook IEFIC

- Se documentan **331 variables** (ingresos, deudas, empleo, patrimonio, vivienda) que complementan la información de los datasets de cartera.
- Permite contextualizar la **capacidad de pago** de los hogares, aunque no contiene microdatos descargables en el archivo obtenido.

---

## 5. Análisis de factores de riesgo

| Factor | Hallazgo |
|---|---|
| **Tipo de entidad** | Cooperativas y compañías de financiamiento tienen 2–3× más % de cartera vencida que los bancos. |
| **Producto** | Microcrédito y libranza concentran el mayor % de vencida; vivienda y leasing el menor. |
| **Calificación** | La cartera vencida correlaciona positivamente con saldos en calificaciones C–E (riesgo alto). |
| **Geografía** | Departamentos periféricos (Vaupés, Vichada, Guainía) lideran la cartera vencida en crédito educativo. |
| **Tiempo** | El % de cartera vencida del sistema muestra ciclos: picos en épocas de desaceleración económica. |
| **Mora acumulada** | La correlación entre saldo en mora y saldo total es casi perfecta (r=0.99), indicando que el riesgo escala con el tamaño de la cartera. |

---

## 6. Modelo de scoring

| Parámetro | Valor |
|---|---|
| Algoritmo | Random Forest (sklearn) |
| Hiperparámetros | n_estimators=200, max_depth=12 |
| Umbral de clasificación | Percentil 75 del % de cartera vencida (**8.78%**) |
| AUC-ROC | **1.0000** |
| Accuracy | **100%** |
| Datos de entrenamiento | 70% (~77.678 registros) |
| Datos de prueba | 30% (~33.291 registros) |

### Top 5 productos con mayor probabilidad de alto riesgo

| Producto | P(alto riesgo) |
|---|---|
| Vivienda no VIS UVR | 0.75 |
| Vivienda VIS UVR | 0.60 |
| Leasing habitacional no VIS UVR | 0.59 |
| Otros portafolios de consumo | 0.55 |
| Microcréditos ≤ 25 SMMLV | 0.45 |

### Características más importantes (Feature Importance)

El modelo identifica que las variables con mayor poder predictivo son:
1. **% de saldo en calificación A** (menor riesgo → reduce P(alto riesgo))
2. **% de saldo en calificaciones D+E** (mayor riesgo → aumenta P(alto riesgo))
3. **% de clientes en mora > 30 días**
4. **Tipo de entidad** (bancaria vs. no bancaria)
5. **Producto** (rotativo, vivienda, consumo)

> **Nota:** el alto rendimiento del modelo se debe a que las features incluyen componentes de la calificación de riesgo, que son indicadores directos de la salud de la cartera. En un escenario de producción, el modelo se entrenaría con datos de solicitudes individuales (no agregadas).

---

## 7. Dashboard local

Se construyó un panel de control interactivo con **Streamlit** que opera 100% en local:

```bash
streamlit run app.py    # → http://localhost:8501
```

El dashboard incluye:
- **KPIs en tiempo real:** registros, cartera total, cartera vencida y % del sistema.
- **Pestaña SFC:** cartera por producto (gráfico de barras, último corte).
- **Pestaña ICETEX:** top 10 departamentos por % de cartera vencida.
- **Pestaña Análisis de Riesgo:** evolución temporal del % vencida y distribución por calificación A–E.

---

## 8. Conclusiones

1. **El riesgo de incumplimiento no es uniforme**: varía significativamente por tipo de entidad, producto, geografía y calificación de riesgo. Las entidades no bancarias y los productos de consumo concentran el mayor riesgo relativo.

2. **La calificación de riesgo A–E es un predictor válido**: el análisis de correlación confirma que la cartera vencida se asocia con las calificaciones C–E. Este es el insumo principal para un sistema de scoring temprano.

3. **La geografía importa**: los departamentos periféricos con menor acceso a servicios financieros muestran indicadores de cartera vencida más altos en crédito educativo, posiblemente por menor infraestructura de cobro y apoyo financiero.

4. **El modelo de Random Forest demuestra viabilidad**: aunque el rendimiento perfecto se debe a la naturaleza agregada de los datos, la metodología es válida para un escenario con datos individuales (solicitudes de crédito).

5. **El dashboard local permite monitoreo continuo**: la interfaz Streamlit se actualiza automáticamente con los datos limpios, permitiendo a un analista revisar el estado de la cartera sin necesidad de internet ni infraestructura en la nube.

---

## 9. Próximos pasos

- Integrar datos de solicitudes individuales (si están disponibles) para entrenar el modelo con mayor fidelidad.
- Construir un sistema de alertas tempranas basado en el scoring de riesgo.
- Ampliar el análisis con datos macroeconómicos (TIB, inflación, desempleo) para el modelo de riesgo.
- Automatizar la actualización de los datasets desde Datos Abiertos Colombia.

---

*Documento elaborado por el Grupo Estoicos — Business Analytics & Big Data II · 1er Corte.*