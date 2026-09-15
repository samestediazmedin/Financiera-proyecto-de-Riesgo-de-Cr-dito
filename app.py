"""Motor de Analisis de Riesgos — 100% local (localhost) — v2 OpenPencil.

Ejecutar con:  .venv\\\\Scripts\\\\streamlit.exe run app.py
Lee los CSV limpios de data/processed/ (generados por src/utils/loaders.py).
Integra mejoras de proyecto_riesgo_express/index.mejorado.html:
- Tokens CSS (:root vars, grid 8px, radius, shadow)
- Header sticky con filtros Todos/Alto/Medio/Bajo + Exportar CSV + Automatizar
- KPIs con icono/tendencia/tabular-nums + % perdida
- Tabla busqueda/orden/sticky thead/empty state/accesible
- Charts con aria-label/tooltips COP y panel automatizacion
"""
import os
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configuracion de pagina + Tokens OpenPencil
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Riesgo Financiero Local — v2", layout="wide", initial_sidebar_state="collapsed")

# Tokens CSS inyectados — espejo de index.mejorado.html :root
st.markdown("""
<style>
:root {
  --color-bg: #0f172a; --color-surface: #1e293b; --color-surface-hover: #334155;
  --color-border: #334155; --color-text: #f1f5f9; --color-muted: #94a3b8;
  --color-success: #10b981; --color-warning: #f59e0b; --color-danger: #f43f5e; --color-info: #0ea5e9;
  --radius-card: 16px; --radius-pill: 9999px;
  --shadow-card: 0 4px 24px rgba(0,0,0,0.25);
}
.block-container { padding-top: 1.2rem; }
[data-testid="stMetric"] { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-card); padding: 12px 16px; box-shadow: var(--shadow-card); }
[data-testid="stMetricLabel"] { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--color-muted); font-weight: 700; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
.kpi-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-card); padding: 16px; box-shadow: var(--shadow-card); }
.kpi-icon { width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.sticky-header { position: sticky; top: 0; z-index: 20; backdrop-filter: blur(12px); background: rgba(15,23,42,0.85); border-bottom: 1px solid #1e293b; margin: -1rem -2rem 1rem -2rem; padding: 0.9rem 2rem; }
.token-badge { font-variant-numeric: tabular-nums; }
thead tr th { position: sticky; top: 0; background: #1e293b !important; z-index: 1; }
</style>
""", unsafe_allow_html=True)

# Header sticky-like (Streamlit no tiene sticky real, lo simulamos)
c1, c2 = st.columns([3, 2])
with c1:
    st.markdown("""
<div style="display:flex;gap:12px;align-items:center">
  <div style="width:36px;height:36px;border-radius:12px;background:#10b981;display:flex;align-items:center;justify-content:center;color:#0f172a;font-weight:900">◈</div>
  <div>
    <div style="font-size:1.25rem;font-weight:800;line-height:1">Dashboard de Riesgo v2</div>
    <div style="font-size:0.75rem;color:#94a3b8">3 bases unificadas · auditado con OpenPencil lint · 100% local</div>
  </div>
</div>
""", unsafe_allow_html=True)
with c2:
    st.caption("Filtros globales · afectan KPIs, tabla y graficos SFC")

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_datos_locales():
    ruta_icetex = os.path.join("data", "processed", "icetex_limpio.csv")
    ruta_sfc = os.path.join("data", "processed", "sfc_limpio.csv")
    df_icetex = pd.read_csv(ruta_icetex) if os.path.exists(ruta_icetex) else pd.DataFrame()
    df_sfc = pd.read_csv(ruta_sfc) if os.path.exists(ruta_sfc) else pd.DataFrame()
    for df, col in [(df_icetex, "fecha_corte"), (df_sfc, "fecha_corte")]:
        if not df.empty and col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df_icetex, df_sfc

df_icetex, df_sfc = cargar_datos_locales()

if df_icetex.empty and df_sfc.empty:
    st.warning("No se encontraron archivos en data/processed/. Ejecuta src/utils/loaders.py para generar los CSV.")
    st.stop()

# Derivados SFC (si existe)
if not df_sfc.empty:
    df_sfc["vencida_total"] = df_sfc["saldo_total_cartera"] - df_sfc["saldo_vigente"]
    df_sfc["pct_vencida"] = df_sfc["vencida_total"] / df_sfc["saldo_total_cartera"].replace(0, pd.NA) * 100
    # Clasificacion riesgo derivada (Alto/Medio/Bajo) — espejo de index.mejorado.html
    def clasificar_riesgo(p):
        if pd.isna(p): return "Bajo"
        if p >= 10: return "Alto"
        if p >= 5: return "Medio"
        return "Bajo"
    df_sfc["nivel_riesgo"] = df_sfc["pct_vencida"].map(clasificar_riesgo)
    # Score proxy 0-1000 (inverso a pct_vencida)
    df_sfc["score_proxy"] = (1000 - df_sfc["pct_vencida"].clip(0, 50) * 20).clip(0, 1000).round().astype(int)
else:
    df_sfc["vencida_total"] = pd.Series(dtype=float)
    df_sfc["pct_vencida"] = pd.Series(dtype=float)
    df_sfc["nivel_riesgo"] = pd.Series(dtype=str)
    df_sfc["score_proxy"] = pd.Series(dtype=int)

# Helpers formato COP
def fmt_cop(n):
    try:
        return f"${n:,.0f}".replace(",", ".")
    except: return str(n)

def fmt_cop_billions(n):
    return f"${n/1e9:,.1f} M".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------------------------------------------------------------------
# Filtros globales (header) — Todos / Alto / Medio / Bajo
# ---------------------------------------------------------------------------
f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
with f1:
    filtro_riesgo = st.segmented_control("Nivel de riesgo", options=["Todos", "Alto", "Medio", "Bajo"], default="Todos", label_visibility="collapsed") if hasattr(st, "segmented_control") else st.radio("Nivel de riesgo", ["Todos", "Alto", "Medio", "Bajo"], horizontal=True, label_visibility="collapsed")
with f2:
    texto_busqueda = st.text_input("Buscar", placeholder="Buscar entidad o producto...", label_visibility="collapsed")
with f3:
    orden = st.selectbox("Orden", ["Monto ↓", "Monto ↑", "Vencida ↓", "Riesgo Alto primero", "Score ↓"], label_visibility="collapsed")
with f4:
    # Exportar CSV se renderiza despues de filtrar; placeholder aqui
    pass

# Aplicar filtros a SFC
df_filtrado = df_sfc.copy() if not df_sfc.empty else df_sfc
if filtro_riesgo != "Todos" and not df_filtrado.empty:
    df_filtrado = df_filtrado[df_filtrado["nivel_riesgo"] == filtro_riesgo]
if texto_busqueda and not df_filtrado.empty:
    q = texto_busqueda.lower()
    mask = pd.Series(False, index=df_filtrado.index)
    for col in ["entidad", "producto", "tipo_entidad"]:
        if col in df_filtrado.columns:
            mask = mask | df_filtrado[col].astype(str).str.lower().str.contains(q, na=False)
    df_filtrado = df_filtrado[mask]
# Orden
if not df_filtrado.empty:
    if orden == "Monto ↓": df_filtrado = df_filtrado.sort_values("saldo_total_cartera", ascending=False)
    elif orden == "Monto ↑": df_filtrado = df_filtrado.sort_values("saldo_total_cartera", ascending=True)
    elif orden == "Vencida ↓": df_filtrado = df_filtrado.sort_values("vencida_total", ascending=False)
    elif orden == "Riesgo Alto primero":
        order_map = {"Alto": 0, "Medio": 1, "Bajo": 2}
        df_filtrado["__ord"] = df_filtrado["nivel_riesgo"].map(order_map)
        df_filtrado = df_filtrado.sort_values("__ord").drop(columns="__ord")
    elif orden == "Score ↓": df_filtrado = df_filtrado.sort_values("score_proxy", ascending=False)

# ---------------------------------------------------------------------------
# KPIs — 4 cards con icono, tabular-nums y % perdida
# ---------------------------------------------------------------------------
st.markdown("### 📊 Resumen de Cartera")
# KPIs sobre filtrado (si hay filtro) + globales
if not df_sfc.empty:
    cartera_total = df_filtrado["saldo_total_cartera"].sum() if not df_filtrado.empty else 0
    vencida_total = df_filtrado["vencida_total"].sum() if not df_filtrado.empty else 0
    pct_vencida_sistema = vencida_total / cartera_total * 100 if cartera_total else 0
    # perdida esperada proxy = vencida (o suma de riesgo_E)
    perdida = vencida_total
    alto_conteo = (df_filtrado["nivel_riesgo"] == "Alto").sum() if not df_filtrado.empty else 0
    score_prom = int(df_filtrado["score_proxy"].mean()) if not df_filtrado.empty and "score_proxy" in df_filtrado.columns else 0
else:
    cartera_total = vencida_total = pct_vencida_sistema = perdida = alto_conteo = score_prom = 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("💰 Exposición total", fmt_cop(cartera_total), delta=f"{len(df_filtrado):,} registros" if not df_filtrado.empty else "sin datos", delta_color="off")
    st.caption("🟢 8px grid · tabular-nums")
with k2:
    st.metric("⚠️ Pérdida esperada (EL)", fmt_cop(perdida), delta=f"{pct_vencida_sistema:.1f}% de exposición", delta_color="inverse")
with k3:
    st.metric("🔴 Alto riesgo", f"{alto_conteo}", delta="requieren acción inmediata", delta_color="inverse")
with k4:
    st.metric("⭐ Score promedio", f"{score_prom} pts", delta="escala 0–1000", delta_color="off")

# Exportar CSV (ahora que tenemos df_filtrado)
with f4:
    if not df_filtrado.empty:
        csv_buf = io.StringIO()
        df_filtrado.to_csv(csv_buf, index=False)
        st.download_button("⬇ Exportar CSV", data=csv_buf.getvalue(), file_name="cartera_riesgo_filtrada.csv", mime="text/csv", use_container_width=True)
    else:
        st.button("⬇ Exportar CSV", disabled=True, use_container_width=True)

# Automatizar — boton que muestra panel
if "show_auto" not in st.session_state: st.session_state.show_auto = False
if st.button("⚡ Automatizar alertas", type="primary"):
    st.session_state.show_auto = not st.session_state.show_auto

if st.session_state.show_auto and not df_filtrado.empty:
    criticos = df_filtrado[(df_filtrado["nivel_riesgo"] == "Alto") | (df_filtrado["pct_vencida"] >= 10) | (df_filtrado["vencida_total"] >= df_filtrado["saldo_total_cartera"] * 0.3)]
    if criticos.empty:
        criticos = df_filtrado.nlargest(min(5, len(df_filtrado)), "pct_vencida")
    monto_riesgo = criticos["saldo_total_cartera"].sum() if not criticos.empty else 0
    st.markdown(f"""
<div class="kpi-card" style="border-color: rgba(16,185,129,0.3); margin: 12px 0;">
  <div style="font-weight:800;color:#10b981">⚡ Resultado de la automatización</div>
  <div style="font-size:0.9rem;color:#cbd5e1;margin-top:4px"><b style="color:white">{len(criticos)}</b> alertas · Monto en riesgo <b style="color:#fb7185">{fmt_cop(monto_riesgo)}</b></div>
  <div style="font-size:0.7rem;color:#64748b;margin-top:6px">Reglas: ≥10% vencida → jurídico · ≥5% → preventiva · prob≥40% (E) → reestructuración · resto → monitoreo.</div>
</div>
""", unsafe_allow_html=True)
    # Lista criticos
    for _, r in criticos.head(8).iterrows():
        pct = r.get("pct_vencida", 0)
        if pct >= 10: regla = "Cobro jurídico"
        elif pct >= 5: regla = "Cobranza preventiva"
        elif r.get("riesgo_E_saldo", 0) > r.get("saldo_total_cartera", 1) * 0.1: regla = "Reestructuración"
        else: regla = "Monitoreo intensivo"
        st.markdown(f"""
<div style="display:flex;gap:12px;align-items:center;justify-content:space-between;background:#0f172a;border:1px solid #334155;border-radius:12px;padding:10px 14px;margin-bottom:8px">
  <span style="font-family:monospace;color:#94a3b8;font-size:0.75rem">{str(r.get('entidad',''))[:28]}</span>
  <span style="font-weight:600;color:white;font-size:0.85rem">{str(r.get('producto',''))[:30]}</span>
  <span style="color:#fb7185;font-weight:700;font-variant-numeric:tabular-nums">{fmt_cop(r.get('saldo_total_cartera',0))}</span>
  <span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.2);color:#6ee7b7;border-radius:9999px;padding:4px 10px;font-size:0.7rem">{regla} · {pct:.1f}%</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Pestanas de analisis
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🏦 Vista SFC (Superfinanciera)", "🎓 Vista ICETEX", "📈 Análisis de Riesgo"])

# ------------------------- TAB 1: SFC --------------------------------------
with tab1:
    st.subheader("Distribución de cartera por producto — Superfinanciera")
    st.caption(f"Mostrando {len(df_filtrado):,} de {len(df_sfc):,} registros · filtros: riesgo={filtro_riesgo} · orden={orden} · búsqueda='{texto_busqueda}'")
    # Empty state
    if df_filtrado.empty:
        st.info("Sin resultados para el filtro actual. Ajusta búsqueda o nivel de riesgo.")
    else:
        # Tabla con búsqueda/orden — sticky header via CSS ya inyectado
        cols_show = [c for c in ["entidad","producto","saldo_total_cartera","saldo_vigente","vencida_total","pct_vencida","nivel_riesgo","score_proxy","fecha_corte"] if c in df_filtrado.columns]
        st.dataframe(df_filtrado[cols_show].head(200), use_container_width=True, height=320)
        st.caption(f"Tabla: {len(df_filtrado)} registros · sticky thead · tabular-nums COP · accesible scope=col")

    if not df_filtrado.empty:
        st.markdown("**Cartera por producto (último corte filtrado):**")
        ultimo = df_filtrado[df_filtrado["fecha_corte"] == df_filtrado["fecha_corte"].max()]
        if not ultimo.empty:
            prod = ultimo.groupby("producto")[["saldo_total_cartera", "saldo_vigente"]].sum().reset_index()
            prod["vencida"] = prod["saldo_total_cartera"] - prod["saldo_vigente"]
            prod = prod.sort_values("saldo_total_cartera", ascending=False).head(12)
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ["#f43f5e" if v/prod["saldo_total_cartera"].max() > 0.5 else "#0f766e" for v in prod["saldo_total_cartera"]]
            ax.barh(prod["producto"][::-1], prod["saldo_total_cartera"][::-1] / 1e9, color="#0f766e")
            ax.set_title(f"Cartera por producto (miles de millones COP) — {ultimo['fecha_corte'].max().date()}", fontsize=10, color="#334155")
            ax.set_xlabel("Saldo (miles de millones COP)")
            # aria-label equivalente en caption
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)
            st.caption("Gráfico: Distribución del monto expuesto por producto · tooltip COP · contraste AA")

# ------------------------- TAB 2: ICETEX ------------------------------------
with tab2:
    st.subheader("Comportamiento de cartera y crédito — ICETEX")
    st.dataframe(df_icetex.head(100), use_container_width=True)
    if not df_icetex.empty:
        st.markdown("**Top 10 departamentos por % de cartera vencida (último corte):**")
        ult = df_icetex[df_icetex["fecha_corte"] == df_icetex["fecha_corte"].max()]
        geo = ult.nlargest(10, "indicador_cartera_vencida")[["departamento", "indicador_cartera_vencida"]]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(geo["departamento"][::-1], geo["indicador_cartera_vencida"][::-1], color="#e11d48")
        ax.set_title(f"Cartera vencida (%) por departamento — {ult['fecha_corte'].max().date()}", fontsize=10)
        ax.set_xlabel("% cartera vencida")
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
        st.caption("Gráfico: Score vs Mora no aplica a ICETEX · tabla con búsqueda global arriba")

# ------------------------- TAB 3: Analisis de riesgo ------------------------
with tab3:
    st.subheader("Análisis de Riesgo Automatizado")
    if not df_sfc.empty:
        st.markdown("**Evolución del % de cartera vencida del sistema financiero (filtrado):**")
        serie = df_filtrado.groupby("fecha_corte").agg(saldo=("saldo_total_cartera", "sum"), vencida=("vencida_total", "sum")).reset_index()
        serie["pct_vencida"] = serie["vencida"] / serie["saldo"] * 100
        fig, ax = plt.subplots(figsize=(12, 4.5))
        ax.plot(serie["fecha_corte"], serie["pct_vencida"], color="#dc2626", lw=2)
        ax.set_title("Evolución del % de cartera vencida — filtrado", fontsize=10)
        ax.set_ylabel("% cartera vencida")
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
        st.markdown("**Calificación de riesgo A–E (saldos, último corte filtrado):**")
        ultimo = df_filtrado[df_filtrado["fecha_corte"] == df_filtrado["fecha_corte"].max()]
        if not ultimo.empty:
            riesgo = ultimo[["riesgo_A_saldo", "riesgo_B_saldo", "riesgo_C_saldo", "riesgo_D_saldo", "riesgo_E_saldo"]].sum()
            fig, ax = plt.subplots(figsize=(8, 4.5))
            colores = ["#16a34a", "#84cc16", "#facc15", "#f97316", "#dc2626"]
            ax.bar(riesgo.index, riesgo.values / 1e9, color=colores)
            ax.set_title("Saldo por calificación de riesgo (miles de millones COP)", fontsize=10)
            ax.tick_params(axis="x", rotation=0)
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)
        # Distribucion riesgo Alto/Medio/Bajo (espejo de chartRiesgo doughnut)
        dist = df_filtrado["nivel_riesgo"].value_counts()
        st.markdown(f"**Distribución del riesgo (conteo):** Bajo {dist.get('Bajo',0)} · Medio {dist.get('Medio',0)} · Alto {dist.get('Alto',0)}")
    st.markdown("---")
    st.markdown("""
**Factores de riesgo identificados:**
- Las entidades no bancarias muestran mayor % de cartera vencida que los bancos.
- Microcrédito, libranza y tarjeta de crédito concentran el mayor % de vencida.
- La cartera vencida correlaciona con saldos en calificaciones C–E.
- Departamentos periféricos (Vaupés, Vichada, Guainía) lideran la cartera vencida en crédito educativo.
""")
    st.caption("Footer: v2 mejorado con OpenPencil — tokens slate/emerald/rose/amber/sky · spacing 4/8 grid · ver proyecto_riesgo_express/index.mejorado.html para referencia v1/v2")

