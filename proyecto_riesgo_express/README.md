# proyecto_riesgo_express — Frontend del Dashboard de Riesgo de Crédito

Frontend **estático** (HTML + JavaScript vanilla + Tailwind + Chart.js) del
proyecto. No requiere build ni servidor: todo corre en el navegador.

## Cómo abrir / servir

**Opción directa:** abre `login.html` con doble clic (protocolo `file://`).
El login funciona en este modo gracias al respaldo puro de `sha256.js`
(cuando `crypto.subtle` no está disponible).

**Opción con servidor local** (recomendada, evita restricciones del
navegador):

```powershell
# Desde la raíz del proyecto
.venv\Scripts\python.exe -m http.server 8080 --directory proyecto_riesgo_express
# Luego abre http://localhost:8080/login.html
```

> **Datos del "Sistema Real":** la pestaña correspondiente de
> `index.mejorado.html` lee `datos_sistema.js`. Si no existe o está
> desactualizado, regenerarlo desde la raíz con:
> `.venv\Scripts\python.exe src\utils\exportar_agregados_dashboard.py`

## Páginas

| Página | Qué es | Requiere sesión |
|---|---|---|
| `login.html` | Pantalla de acceso (SHA-256 client-side, sesión en pestaña o enlace firmado). | No |
| `index.html` | **Dashboard v1**: KPIs, 3 charts (doughnut/barras/burbujas), tabla y automatización con los 6 clientes simulados de `datos.js`. | Sí (`auth.js`) |
| `index.mejorado.html` | **RiskPulse (dashboard v2)**: 5 pestañas — donut SVG interactivo por nivel de riesgo, simulador de estrés con VaR Monte Carlo, gestor de cartera (CRUD en localStorage), sistema real SFC/ICETEX/IEFIC y asesor IA (Gemini con key local). | Sí (`auth.js`) |
| `ishikawa.html` | Diagrama de Ishikawa del problema (SVG dibujado por JS, imprimible a PDF). | No |

**Usuarios demo** (mostrados también en el propio login):
`admin` / `cobranzas` / `analista` — las contraseñas están como hint en el
pie de `login.html` (demo académica; los hashes viven en `usuarios.js`).

## Rol de cada archivo JS

| Archivo | Rol |
|---|---|
| `auth.js` | Guardián de sesión: lee `sessionStorage` (con fallback a token `#s=base64` en la URL), redirige a `login.html` si no hay sesión, pinta el chip de usuario/rol y expone `logout()`. Se incluye **primero** en toda página protegida. |
| `datos.js` | Datos de demo: `baseDatosConsolidada`, 6 clientes simulados que representan la unión de las 3 bases (clientes × créditos × mora). Alimenta la v1 y el estado inicial de la v2. |
| `datos_sistema.js` | **AUTOGENERADO** por `src/utils/exportar_agregados_dashboard.py` — no editar a mano. Contiene `DATOS_SISTEMA` con los agregados reales del sistema financiero (serie mensual de % vencida, top productos, calificación A–E, top ICETEX y codebook IEFIC). |
| `usuarios.js` | Directorio de usuarios demo con contraseñas hasheadas (SHA-256 hex). |
| `sha256.js` | Implementación de SHA-256 en JS puro; respaldo de `login.html` cuando Web Crypto no está disponible (contextos `file://`). Solo entrada ASCII. |
| `tailwind.config.cjs` | Configuración de Tailwind usada al compilar `vendor/tailwind.css`. |

## Esquema de `DATOS_SISTEMA` (datos_sistema.js)

- `serieVencida`: `{mes, total, bancos, noBancarias}` × 24 cortes — % de
  cartera vencida mensual del sistema.
- `topProductos`: `{producto, saldoMilesM, pctVencida}` — top 8 por saldo
  en el último corte.
- `calificacion`: `{letra, saldoMilesM, pct}` — saldos A–E y participación.
- `icetexTop`: `{departamento, pctVencida}` — top 10 departamentos por
  indicador de vencida (valores escalados ×100; 2719.5 ≡ 27.2%).
- `iefic`: `{total, vars: [{n, l}]}` — 331 variables del codebook BANREP.
- `meta`: `{desde, hasta, filasSfc, generado}` — rango y trazabilidad.

## Vendor (NO editar)

`vendor/` contiene dependencias locales: `tailwind.css`, `chart.umd.js`
(Chart.js), fuentes y FontAwesome. Son librerías externas empaquetadas para
que el dashboard funcione sin CDN.
