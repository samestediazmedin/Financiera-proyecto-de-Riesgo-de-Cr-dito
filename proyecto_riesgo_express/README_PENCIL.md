# Dashboard + OpenPencil — guía real (verificada)

## Estado: FUNCIONA ✅ (openpencil 0.14.0 + bun 1.4.2, Windows)

## Setup necesario (una sola vez)

1. `npm install -g @open-pencil/cli @open-pencil/mcp bun`
2. **Parche imprescindible en Windows**: los paquetes `@open-pencil/*` publican
   condiciones `"bun": "./src/*.ts"` en `exports`, pero solo incluyen `dist/` →
   bajo runtime bun fallan con `Cannot find module`. Fix: eliminar las claves
   `"bun"` de `exports`/`imports` en TODOS los `package.json` de:
   - `%AppData%\npm\node_modules\@open-pencil\mcp\`
   - `%AppData%\npm\node_modules\@open-pencil\cli\node_modules\@open-pencil\` (core, dom-css, fig, kiwi, pen, scene-graph)
3. Ejecutar SIEMPRE con runtime bun forzado: `bunx --bun openpencil <cmd>`
   (el shim `.cmd` usa node → `Bun is not defined`).

## Comandos verificados

```powershell
# importar HTML → documento de diseño editable (.fig)
bunx --bun openpencil import index.html -o design/dashboard_v1.fig
bunx --bun openpencil import index.mejorado.html -o design/dashboard_v2.fig

# lint de diseño (hallazgos v1: 0 errores, 40 warnings, 47 info)
bunx --bun openpencil lint design/dashboard_v1.fig

# análisis de tokens
bunx --bun openpencil analyze colors design/dashboard_v1.fig
bunx --bun openpencil analyze typography design/dashboard_v1.fig
bunx --bun openpencil analyze spacing design/dashboard_v1.fig

# estructura y variables
bunx --bun openpencil tree design/dashboard_v1.fig
bunx --bun openpencil variables design/dashboard_v1.fig

# export (PNG falla en Windows por bug upstream de canvaskit locateFile —
# los .fig se abren directamente en la app OpenPencil o en https://app.openpencil.dev)
```

## Hallazgos del lint sobre la v1 (motivaron index.mejorado.html)
- `no-hardcoded-colors` (warn): fills sin variable de diseño → v2 usa `:root` tokens
- `text-style-required` (info): tipografía sin tokens → v2 normaliza tamaños/pesos
- `prefer-auto-layout` (info): frames sin auto-layout → v2 usa flex/grid consistente

## Archivos
- `design/dashboard_v1.fig` — documento de diseño del dashboard original
- `design/dashboard_v2.fig` — documento de diseño del dashboard mejorado
- `index.mejorado.html` — v2 con tokens, filtros, búsqueda, orden, CSV, accesibilidad
- `index.html` — v1 original (sin tocar)

## MCP en opencode
`~/.config/opencode/opencode.json` y `.jsonc` → `"pencil": openpencil-mcp.cmd, enabled: true`.
El bridge stdiO necesita la app desktop; headless puro = usar el CLI (arriba) o
`openpencil-mcp-http` (HTTP en http://127.0.0.1:7600/mcp, requiere token Bearer
vía OPENPENCIL_MCP_AUTH_TOKEN).

## Login (demo académica)

`login.html` controla el acceso a ambos dashboards (`index.html` y `index.mejorado.html`).

- **Mecanismo**: usuarios en `usuarios.js` con passwords hasheadas SHA-256 (Web Crypto);
  sesión en `sessionStorage` (expira al cerrar la pestaña); guard en `auth.js`.
- **Roles**: Administrador, Cobranzas, Analista — visibles en el chip del header (v2).
- **Logout**: botón "⏻ Salir" en el header de la v2.

| Usuario | Password | Rol |
|---|---|---|
| `admin` | `riesgo2026` | Administrador |
| `cobranzas` | `cobranzas2026` | Cobranzas |
| `analista` | `analista2026` | Analista |

⚠️ Es una demo académica: la validación es client-side (no es seguridad real de servidor).
