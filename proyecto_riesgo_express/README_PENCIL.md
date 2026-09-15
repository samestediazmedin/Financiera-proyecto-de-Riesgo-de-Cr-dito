# Dashboard mejorado con OpenPencil

## Qué se hizo (open-pencil 0.14.0)
- **MCP headless** configurado en `~/.config/opencode/opencode.json` y `opencode.jsonc` → `openpencil-mcp` (npm global, enabled:true). Reiniciar opencode para que tome el cambio.
- **Dashboard v2**: `index.mejorado.html` — aplica hallazgos de `openpencil lint / analyze`:
  - Tokens normalizados (`:root` CSS vars), 8px grid, radius/shadow consistentes
  - Header sticky con filtros de riesgo (Todos/Alto/Medio/Bajo) + export CSV
  - KPIs con icono + tendencia + tabular-nums
  - Tabla con búsqueda, orden (monto/score/mora/riesgo), empty state, conteo, sticky thead, tabs accesibles
  - Charts con tooltips mejorados y aria-labels
  - Footer con referencia a lint/analyze y link a v1

## Uso OpenPencil CLI (headless, sin app)
```bash
# requiere bun (ya instalado: bun 1.4.2)
bunx openpencil tree dashboard.fig
bunx openpencil lint dashboard.fig
bunx openpencil analyze colors dashboard.fig
bunx openpencil variables dashboard.fig

# Import HTML → fig (cuando el bug Bun is not defined se arregle upstream, hoy falla en 0.14.0)
# bunx openpencil import index.html -o dashboard.fig
# bunx openpencil export dashboard.fig -f html --css tailwind
```

## MCP
- `openpencil-mcp` (stdio bridge) → necesita app desktop corriendo. Para headless puro usar `openpencil-mcp-http` en http://127.0.0.1:7600/mcp
- Con `bun` disponible, `openpencil lint/analyze/export/tree/query` ya funcionan sin servidor.

Probar v2: abrir `proyecto_riesgo_express/index.mejorado.html` en navegador.
