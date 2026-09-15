"""Motor de Análisis de Riesgos — 100% local (localhost).

Ejecutar con:  streamlit run app.py
Lee los CSV limpios de data/processed/ (generados por src/utils/loaders.py).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configuración de la página local
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Riesgo Financiero Local", layout="wide")
st.title("🛡️ Motor de Análisis de Riesgos (Localhost)")
st.caption("Proyecto de Riesgo de Crédito · Grupo Estoicos · 100% local, sin internet")

# ---------------------------------------------------------------------------
# Carga de datos desde la carpeta local procesada
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_datos_locales():
    ruta_icetex = os.path.join("data", "processed", "icetex_limpio.csv")
    ruta_sfc = os.path.join("data", "processed", "sfc_limpio.csv")

    df_icetex = pd.read_csv(ruta_icetex) if os.path.exists(ruta_icetex) else pd.DataFrame()
    df_sfc = pd.read_csv(ruta_sfc) if os.path.exists(ruta_sfc) else pd.DataFrame()

    # Normalizar fechas (vienen como texto desde el CSV)
    for df, col in [(df_icetex, "fecha_corte"), (df_sfc, "fecha_corte")]:
        if not df.empty and col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df_icetex, df_sfc


df_icetex, df_sfc = cargar_datos_locales()

if df_icetex.empty and df_sfc.empty:
    st.warning("⚠️ No se encontraron los archivos en data/processed/. Verifica que src/utils/loaders.py haya guardado los CSV.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs rápidos
# ---------------------------------------------------------------------------
st.markdown("### 📊 Resumen de Cartera")

if not df_sfc.empty:
    df_sfc["vencida_total"] = df_sfc["saldo_total_cartera"] - df_sfc["saldo_vigente"]
    df_sfc["pct_vencida"] = df_sfc["vencida_total"] / df_sfc["saldo_total_cartera"].replace(0, pd.NA) * 100
    cartera_total = df_sfc["saldo_total_cartera"].sum()
    vencida_total = df_sfc["vencida_total"].sum()
    pct_vencida_sistema = vencida_total / cartera_total * 100 if cartera_total else 0
else:
    cartera_total = vencida_total = pct_vencida_sistema = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros Superfinanciera (SFC)", f"{len(df_sfc):,}")
col2.metric("Registros ICETEX", f"{len(df_icetex):,}")
col3.metric("Cartera total del sistema", f"${cartera_total / 1e12:,.2f} B")
col4.metric("Cartera vencida del sistema", f"${vencida_total / 1e12:,.2f} B ({pct_vencida_sistema:.2f}%)")

st.markdown("---")

# ---------------------------------------------------------------------------
# Pestañas de análisis
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🏦 Vista SFC (Superfinanciera)", "🎓 Vista ICETEX", "📈 Análisis de Riesgo"])

# ------------------------- TAB 1: SFC --------------------------------------
with tab1:
    st.subheader("Distribución de cartera por producto — Superfinanciera")
    st.write("Muestra de datos estructurados (primeras 100 filas):")
    st.dataframe(df_sfc.head(100), use_container_width=True)

    if not df_sfc.empty:
        st.markdown("**Cartera por producto (último corte):**")
        ultimo = df_sfc[df_sfc["fecha_corte"] == df_sfc["fecha_corte"].max()]
        prod = ultimo.groupby("producto")[["saldo_total_cartera", "saldo_vigente"]].sum().reset_index()
        prod["vencida"] = prod["saldo_total_cartera"] - prod["saldo_vigente"]
        prod = prod.sort_values("saldo_total_cartera", ascending=False).head(12)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(prod["producto"][::-1], prod["saldo_total_cartera"][::-1] / 1e9, color="#0f766e")
        ax.set_title(f"Cartera por producto (miles de millones COP) — {ultimo['fecha_corte'].max().date()}")
        ax.set_xlabel("Saldo (miles de millones COP)")
        st.pyplot(fig)
        plt.close(fig)

# ------------------------- TAB 2: ICETEX ------------------------------------
with tab2:
    st.subheader("Comportamiento de cartera y crédito — ICETEX")
    st.write("Muestra de datos estructurados (primeras 100 filas):")
    st.dataframe(df_icetex.head(100), use_container_width=True)

    if not df_icetex.empty:
        st.markdown("**Top 10 departamentos por % de cartera vencida (último corte):**")
        ult = df_icetex[df_icetex["fecha_corte"] == df_icetex["fecha_corte"].max()]
        geo = ult.nlargest(10, "indicador_cartera_vencida")[["departamento", "indicador_cartera_vencida"]]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(geo["departamento"][::-1], geo["indicador_cartera_vencida"][::-1], color="#e11d48")
        ax.set_title(f"Cartera vencida (%) por departamento — {ult['fecha_corte'].max().date()}")
        ax.set_xlabel("% cartera vencida")
        st.pyplot(fig)
        plt.close(fig)

# ------------------------- TAB 3: Análisis de riesgo ------------------------
with tab3:
    st.subheader("Análisis de Riesgo Automatizado")

    if not df_sfc.empty:
        st.markdown("**Evolución del % de cartera vencida del sistema financiero:**")
        serie = df_sfc.groupby("fecha_corte").agg(
            saldo=("saldo_total_cartera", "sum"), vencida=("vencida_total", "sum")).reset_index()
        serie["pct_vencida"] = serie["vencida"] / serie["saldo"] * 100

        fig, ax = plt.subplots(figsize=(12, 4.5))
        ax.plot(serie["fecha_corte"], serie["pct_vencida"], color="#dc2626", lw=2)
        ax.set_title("Evolución del % de cartera vencida del sistema financiero colombiano")
        ax.set_ylabel("% cartera vencida")
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("**Calificación de riesgo A–E (saldos, último corte):**")
        ultimo = df_sfc[df_sfc["fecha_corte"] == df_sfc["fecha_corte"].max()]
        riesgo = ultimo[["riesgo_A_saldo", "riesgo_B_saldo", "riesgo_C_saldo", "riesgo_D_saldo", "riesgo_E_saldo"]].sum()

        fig, ax = plt.subplots(figsize=(8, 4.5))
        colores = ["#16a34a", "#84cc16", "#facc15", "#f97316", "#dc2626"]
        ax.bar(riesgo.index, riesgo.values / 1e9, color=colores)
        ax.set_title("Saldo por calificación de riesgo (miles de millones COP)")
        ax.tick_params(axis="x", rotation=0)
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")
    st.markdown("""
    **Factores de riesgo identificados:**
    - Las entidades no bancarias muestran mayor % de cartera vencida que los bancos.
    - Microcrédito, libranza y tarjeta de crédito concentran el mayor % de vencida.
    - La cartera vencida correlaciona con saldos en calificaciones C–E.
    - Departamentos periféricos (Vaupés, Vichada, Guainía) lideran la cartera vencida en crédito educativo.
    """)