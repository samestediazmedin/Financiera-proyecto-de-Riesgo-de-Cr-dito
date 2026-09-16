
## v3 BI — integración RiskPulse + datos reales (2026-09-15)

Dashboard `index.mejorado.html` reorganizado en 3 pestañas:

1. **📊 Cartera** — dona SVG interactiva con drill-down (clic en Bajo/Medio/Alto → drawer
   con clientes de la banda y barras de composición), KPIs, gráficos, tabla con
   búsqueda/orden/filtros, automatización de alertas y export CSV.
2. **🧪 Simulador de estrés** — presets (Base, Estrés PD×1.5, Crisis PD×2, Recuperación
   PD×0.7) + sliders (multiplicador de PD, tasa de recuperación). Calcula EL, **VaR 95%
   y Expected Shortfall por Monte Carlo** (2.000 iteraciones, semilla fija) y gráfico
   EL por cliente base vs escenario. Metodología documentada en la propia pestaña.
3. **🏦 Sistema Real** — agregados desde `data/processed/` (SFC 111k filas + ICETEX):
   serie 24 cortes % cartera vencida (bancos vs no bancarias), top 8 productos,
   calificación A–E y top 10 departamentos ICETEX.

Generación de datos: `python src/utils/exportar_agregados_dashboard.py` (usa el .venv)
→ produce `datos_sistema.js` (~4.4 KB). Re-ejecutar tras actualizar data/processed/.

Componentes adaptados de RiskPulse (interactive_portfolio_risk_management_platform.html):
dona SVG con getArcPath, presets de escenario, toasts y navegación por pestañas.
No integrado: asesor IA Gemini (requiere API key propia) y tema claro/oscuro.
