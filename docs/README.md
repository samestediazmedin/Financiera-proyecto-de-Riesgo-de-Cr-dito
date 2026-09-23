# Proyecto de Riesgo de Crédito

Análisis del riesgo de incumplimiento de solicitudes de crédito para el sector financiero colombiano.

> **Grupo Estoicos** · Caren Dayana Romero Montoya · Karen Jimena Ocampo Otalora · Samuel Esteban Diaz Medina
> Business Analytics & Big Data II · Docente: Oscar Castiblanco

## Problema

> El problema identificado es la dificultad para identificar oportunamente las características asociadas al riesgo de incumplimiento de las solicitudes de crédito, que afecta a los analistas y responsables de la gestión del riesgo, provocando una mayor incertidumbre en la evaluación de las solicitudes y posibles pérdidas por créditos incumplidos.

Ver [`PROBLEMA.md`](PROBLEMA.md) y [`docs/ficha_etapa2.md`](docs/ficha_etapa2.md) para los resultados completos.

## Datos

| Archivo | Fuente | Registros | Descripción |
|---|---|---|---|
| `Comportamiento_de_Cartera_y_Crédito._20260914.csv` | ICETEX | 1.240 × 11 | Cartera por departamento: créditos al día, mora, saldos, indicador de cartera vencida |
| `Distribución_de_cartera_por_producto_20260914.csv` | Superfinanciera | 110.969 × 34 | Cartera por producto/entidad: saldos, mora por rango, calificación A–E |
| `BANREP-IEFIC-2017-2018.xml` | Banco de la República | 331 variables | Codebook IEFIC: diccionario de variables de la encuesta de ingresos y gastos |

Ver [`diccionario_variables.md`](diccionario_variables.md) para el diccionario completo de las tres fuentes (variables, tipos, formatos y transformaciones).

## Estructura del proyecto

```
├── data/
│   ├── raw/                    # Datos crudos (inmutables)
│   └── processed/              # Datos limpios (generados)
├── notebooks/
│   ├── 01_eda_icetex.ipynb     # EDA — ICETEX
│   ├── 02_eda_sfc.ipynb        # EDA — Superfinanciera
│   ├── 03_iefic_codebook.ipynb # Codebook IEFIC
│   ├── 04_analisis_riesgo.ipynb# Análisis de factores de riesgo
│   └── 05_modelo_scoring.ipynb # Modelo de scoring (Random Forest)
├── src/utils/loaders.py        # Carga y normalización de datasets
├── app.py                      # Dashboard local con Streamlit
├── docs/ficha_etapa2.md        # Ficha etapa 2 y 3: análisis y resultados
├── entregable_etapa1/          # Ficha etapa 1 e Ishikawa
└── requirements.txt
```

## Setup

```powershell
# Crear e instalar entorno virtual
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar el dashboard (100% local)

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

El dashboard se abre en **http://localhost:8501**. Muestra:
- KPIs: registros, cartera total y vencida del sistema
- Cartera por producto (Superfinanciera)
- Top departamentos por % de cartera vencida (ICETEX)
- Evolución temporal del riesgo + calificación A–E

## Ejecutar los notebooks

```powershell
.\.venv\Scripts\python.exe -m jupyter notebook notebooks/
```

## Flujo de trabajo

1. **Carga y limpieza** → `src/utils/loaders.py` (parsers separados para cada dataset)
2. **EDA** → `notebooks/01-03` (exploración visual de cada fuente)
3. **Análisis de riesgo** → `notebooks/04` (correlaciones, ranking de factores)
4. **Modelado** → `notebooks/05` (Random Forest para clasificación alto/normal)
5. **Dashboard** → `app.py` (panel interactivo local con Streamlit)

## Hallazgos clave

- Las **entidades no bancarias** tienen 2–3× más % de cartera vencida que los bancos.
- **Microcrédito y libranza** concentran el mayor riesgo de incumplimiento.
- La cartera del sistema financiero alcanzó **$556 billones** con un **5.6% de cartera vencida** (dic 2025).
- Departamentos periféricos (Vaupés, Vichada) lideran la cartera vencida en crédito educativo.
- El modelo de scoring identifica los **productos y entidades de mayor riesgo** con alta precisión.