# AGENTS.md — Contexto para agentes de opencode

## Proyecto
Análisis de **riesgo de crédito** (incumplimiento de solicitudes de crédito) en el sector financiero colombiano. Proyecto universitario.

## Reglas de oro
- **Nunca modificar `data/raw/`** — los datos crudos son inmutables. Cualquier transformación va en `src/` o `notebooks/` y se guarda en `data/processed/` (crear si hace falta).
- Los montos en los CSV vienen con formato colombiano: `$ 14,629,091` (miles separados por coma, decimales con punto). Normalizar antes de operar.
- Fechas en `Comportamiento_de_Cartera_y_Crédito` vienen como `"2022 Mar 31 12:00:00 AM"` — parsear con `pd.to_datetime(..., format=...)`.
- El CSV de distribución usa separador `;` y montos con punto como separador de miles (`37.651.351.298`).
- El XML de BANREP requiere `lxml` para parsear.

## Stack
Python 3 + pandas, numpy, matplotlib/seaborn, scikit-learn, Jupyter.

## Convenciones
- Commits pequeños y atómicos por cada cambio (el usuario quiere commits constantes para seguir el aprendizaje).
- Mensajes de commit en español, estilo conventional commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Notebooks numerados: `01_eda_*.ipynb`, `02_limpieza_*.ipynb`, etc.
- Documentar decisiones de análisis en `docs/`.

## Cómo trabajar
- Antes de tocar código, leer `README.md` y `PROBLEMA.md`.
- Para análisis exploratorio, crear notebooks en `notebooks/`.
- Para lógica reutilizable, crear módulos en `src/`.
