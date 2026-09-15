# Proyecto de Riesgo de Crédito

Análisis del riesgo de incumplimiento de solicitudes de crédito para el sector financiero colombiano.

## Problema

> El problema identificado es la dificultad para identificar oportunamente las características asociadas al riesgo de incumplimiento de las solicitudes de crédito, que afecta a los analistas y responsables de la gestión del riesgo, provocando una mayor incertidumbre en la evaluación de las solicitudes y posibles pérdidas por créditos incumplidos.

Ver [`PROBLEMA.md`](PROBLEMA.md) para el enunciado completo.

## Datos

| Archivo | Fuente | Descripción |
|---|---|---|
| `data/raw/Comportamiento_de_Cartera_y_Crédito._20260914.csv` | Superfinanciera | Comportamiento de cartera por departamento de residencia del deudor: créditos al día, mora <90 días, mora >90 días, saldos e indicador de cartera vencida |
| `data/raw/Distribución_de_cartera_por_producto_20260914.csv` | Superfinanciera | Distribución de cartera por entidad y producto: saldos vigentes, vencidos por rango de meses, número de créditos |
| `data/raw/BANREP-IEFIC-2017-2018.xml` | Banco de la República | Encuesta IEFIC 2017-2018 (indicadores de financiación e inclusión financiera) |

## Estructura

```
├── data/raw/          # Datos crudos (no modificar)
├── notebooks/         # Análisis exploratorio y modelado (Jupyter)
├── src/
│   ├── eda/           # Scripts de análisis exploratorio
│   ├── models/        # Modelos de scoring / riesgo
│   └── utils/         # Utilidades compartidas (carga, limpieza)
├── docs/              # Documentación del proyecto
├── PROBLEMA.md        # Enunciado del problema
└── AGENTS.md          # Contexto para agentes de opencode
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Flujo de trabajo sugerido

1. **EDA** — explorar los datos en `notebooks/01_eda_cartera.ipynb`
2. **Limpieza** — normalizar formatos (fechas, montos con `$`, separadores)
3. **Modelado** — construir indicador de riesgo / scoring de incumplimiento
4. **Validación** — métricas de desempeño y análisis de sensibilidad
