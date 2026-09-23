# Proyecto de Riesgo de Crédito — Análisis del riesgo de incumplimiento

Análisis del **riesgo de incumplimiento de solicitudes de crédito** para el
sector financiero colombiano, construido sobre tres fuentes de datos reales:
la cartera del **ICETEX** (crédito educativo), la **Superintendencia
Financiera de Colombia (SFC)** (cartera por producto) y el codebook de la
**IEFIC** del Banco de la República (encuesta de inclusión/ingresos).

El proyecto cubre el ciclo completo: EDA → análisis de factores de riesgo →
modelo de scoring (Random Forest) → dashboards (Streamlit en Python y
frontend estático HTML/JS) con asesor opcional de IA (Google Gemini).

> **Grupo Estoicos** · Business Analytics & Big Data II.
> Contexto detallado del problema y fichas por etapa en [`docs/`](docs/).

---

## Estructura de carpetas

```
.
├── app.py                        # Dashboard Streamlit (v2, datos reales SFC/ICETEX)
├── api_datos.py                  # API JSON en vivo de los agregados (puerto 8189)
├── requirements.txt              # Dependencias Python
├── .env                          # Secretos locales (gitignored) — ver "Variables de entorno"
├── data/
│   ├── raw/                      # Datos crudos descargados (INMUTABLES)
│   │   ├── Comportamiento_de_Cartera_y_Crédito._20260914.csv     # ICETEX
│   │   ├── Distribución_de_cartera_por_producto_20260914.csv     # SFC
│   │   └── BANREP-IEFIC-2017-2018.xml                            # IEFIC codebook
│   └── processed/                # CSV limpios generados (gitignored)
│       ├── icetex_limpio.csv
│       └── sfc_limpio.csv
├── notebooks/                    # Flujo de análisis (ver notebooks/README.md)
│   ├── 01_eda_icetex.ipynb       # EDA ICETEX  → genera icetex_limpio.csv
│   ├── 02_eda_sfc.ipynb          # EDA SFC     → genera sfc_limpio.csv
│   ├── 03_iefic_codebook.ipynb   # Exploración del codebook IEFIC
│   ├── 04_analisis_riesgo.ipynb  # Factores de riesgo de incumplimiento
│   └── 05_modelo_scoring.ipynb   # Clasificador alto riesgo (Random Forest)
├── src/
│   └── utils/
│       ├── loaders.py                      # Carga y normalización de los 3 datasets
│       ├── exportar_agregados_dashboard.py # Agregados BI → datos_sistema.js
│       └── gemini_advisor.py               # Asesor IA (Gemini) del Streamlit
├── proyecto_riesgo_express/      # Frontend estático (ver su README.md)
│   ├── login.html                # Autenticación (SHA-256 client-side)
│   ├── index.html                # Dashboard v1 (datos simulados)
│   ├── index.mejorado.html       # RiskPulse — dashboard v2 (5 pestañas)
│   ├── ishikawa.html             # Diagrama de Ishikawa (SVG dinámico)
│   ├── auth.js / datos.js / datos_sistema.js / sha256.js / usuarios.js
│   ├── design/                   # Mockups OpenPencil (.fig)
│   └── vendor/                   # Tailwind, Chart.js, FontAwesome (NO editar)
└── docs/                         # Fichas de etapa, problema y documentación
```

## Stack tecnológico

- **Python 3.11+**: pandas, numpy, matplotlib, seaborn, scikit-learn, lxml,
  streamlit, google-genai (ver `requirements.txt`).
- **Frontend**: HTML + JavaScript vanilla, Tailwind CSS y Chart.js
  (servidos localmente desde `proyecto_riesgo_express/vendor/`).

## Instalación

```powershell
# 1) Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 2) Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

### 1. Generar los datos limpios (primera vez)

Ejecuta los notebooks `01_eda_icetex.ipynb` y `02_eda_sfc.ipynb` (escriben
`data/processed/`), o usa los loaders desde Python:

```powershell
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); from src.utils.loaders import load_sfc, load_icetex, save_processed; save_processed(load_sfc(),'sfc_limpio.csv'); save_processed(load_icetex(),'icetex_limpio.csv')"
```

### 2. Dashboard Python (Streamlit)

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Abre **http://localhost:8501** — filtros globales, KPIs, tabla SFC, gráficos
y pestaña de asesor IA (opcional, requiere `GEMINI_API_KEY`).

### 3. Frontend express (HTML/JS)

Ver [`proyecto_riesgo_express/README.md`](proyecto_riesgo_express/README.md).
Basta con abrir `login.html` en el navegador (o servir la carpeta con
`python -m http.server`). La pestaña "Sistema Real" requiere regenerar
`datos_sistema.js`:

```powershell
.venv\Scripts\python.exe src\utils\exportar_agregados_dashboard.py
```

### 4. (Opcional) API de datos en vivo

```powershell
.venv\Scripts\python.exe api_datos.py   # http://127.0.0.1:8189/api/sistema
```

## Variables de entorno

Solo hay una variable, definida en el archivo `.env` de la raíz (este archivo
está en `.gitignore` y **nunca debe commitearse**):

| Variable          | Dónde se usa                    | Para qué                                                        |
|-------------------|---------------------------------|-----------------------------------------------------------------|
| `GEMINI_API_KEY`  | `src/utils/gemini_advisor.py` (y `.env` del proyecto) | Habilita la pestaña "Asesor IA" del Streamlit. Key gratuita en [aistudio.google.com](https://aistudio.google.com). Sin ella, el resto del dashboard funciona igual. |

El frontend express guarda su propia key en `localStorage` del navegador
(nunca en el repositorio).

## Función de cada archivo principal

| Archivo | Función |
|---|---|
| `app.py` | Dashboard Streamlit con filtros, KPIs, gráficos y automatización de alertas sobre los datos reales. |
| `api_datos.py` | Micro API HTTP (stdlib) que sirve los agregados BI recalculados al vuelo. |
| `src/utils/loaders.py` | Parsers/normalizadores de los 3 datasets crudos (formatos colombianos de monto/fecha). |
| `src/utils/exportar_agregados_dashboard.py` | Genera `datos_sistema.js` (agregados que consume el frontend express). |
| `src/utils/gemini_advisor.py` | Cliente de Gemini para el asesor de riesgo del Streamlit. |
| `proyecto_riesgo_express/index.mejorado.html` | Dashboard v2 completo (donut interactivo, simulador VaR, CRUD cartera, sistema real, IA). |

## Reglas del proyecto

- `data/raw/` es **inmutable**: nunca se modifica; lo limpio va a
  `data/processed/`.
- Los formatos de monto difieren entre datasets (ICETEX usa comas de miles;
  SFC usa punto de miles y coma decimal) — `loaders.py` los normaliza.
- `vendor/` contiene librerías externas: no editar.
