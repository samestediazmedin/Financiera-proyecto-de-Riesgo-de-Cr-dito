"""Exporta agregados BI del sistema financiero para el dashboard HTML.

Propósito
---------
Lee los CSV limpios de ``data/processed/`` (regla de oro: ``data/raw`` es
inmutable) y genera ``proyecto_riesgo_express/datos_sistema.js`` — un JSON
liviano (< 30 KB) consumible por el navegador con los agregados que dibuja
la pestaña "Sistema Real" del dashboard express:

  * ``serieVencida``  — evolución mensual del % de cartera vencida
                        (últimos 24 cortes): total sistema, bancos
                        (``tipo_entidad=1``) y no bancarias.
  * ``topProductos``  — top 8 productos por saldo en el último corte
                        (saldo + % vencida).
  * ``calificacion``  — saldos por calificación de riesgo A–E (últ. corte).
  * ``icetexTop``     — top 10 departamentos por % de cartera vencida
                        ICETEX (último corte).
  * ``iefic``         — diccionario de variables IEFIC (nombre + etiqueta).
  * ``meta``          — rango de fechas y nº de registros procesados.

También es consumido en vivo por ``api_datos.py`` (endpoint ``/api/sistema``).

Uso:
    python src/utils/exportar_agregados_dashboard.py

Documentado: 2026-09-18.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
SFC = BASE / "data" / "processed" / "sfc_limpio.csv"          # entrada: cartera SFC limpia
ICETEX = BASE / "data" / "processed" / "icetex_limpio.csv"    # entrada: cartera ICETEX limpia
IEFIC = BASE / "data" / "raw" / "BANREP-IEFIC-2017-2018.xml"  # entrada: codebook DDI (XML)
OUT = BASE / "proyecto_riesgo_express" / "datos_sistema.js"   # salida: JS consumido por el navegador

# Parámetros de agregación: nº de cortes mensuales y tamaños de los "top".
N_CORTES = 24
TOP_PRODUCTOS = 8
TOP_DEPTOS = 10


def _pct(vencida: float, total: float) -> float:
    """Calcula el porcentaje de cartera vencida de forma segura.

    Args:
        vencida: Saldo vencido (misma unidad que ``total``).
        total: Saldo total de la cartera.

    Returns:
        ``(vencida / total * 100)`` redondeado a 2 decimales, o ``0.0``
        cuando ``total`` es 0 (evita división por cero).
    """
    return round(vencida / total * 100, 2) if total else 0.0


def generar_datos() -> dict:
    """Genera el dict de agregados BI (usado por el CLI y por la API en vivo).

    Proceso:
        1. Carga ``sfc_limpio.csv`` y deriva ``vencida = total - vigente``
           y ``es_banco`` (``tipo_entidad == 1``).
        2. Construye la serie mensual (últimos ``N_CORTES``) del % vencida
           para total/bancos/noBancarias.
        3. Agrega top de productos, calificación A–E e ICETEX del último corte.
        4. Añade el diccionario IEFIC vía
           :func:`src.utils.loaders.load_iefic_codebook` (si falla, se omite
           sin romper la exportación).

    Returns:
        dict: Claves ``serieVencida``, ``topProductos``, ``calificacion``,
        ``icetexTop``, ``iefic`` y ``meta`` (rango de fechas, filas SFC y
        fecha de generación).
    """
    df = pd.read_csv(SFC, parse_dates=["fecha_corte"])
    df["vencida"] = df["saldo_total_cartera"] - df["saldo_vigente"]
    df["es_banco"] = df["tipo_entidad"] == 1

    # --- 1) Serie mensual: % vencida por corte (total / bancos / noBancarias) ---
    cortes = sorted(df["fecha_corte"].unique())[-N_CORTES:]
    serie = []
    for corte in cortes:
        d = df[df["fecha_corte"] == corte]
        fila = {"mes": pd.Timestamp(corte).strftime("%Y-%m")}
        for clave, sub in (("total", d), ("bancos", d[d["es_banco"]]), ("noBancarias", d[~d["es_banco"]])):
            t_ = sub["saldo_total_cartera"].sum(); v = sub["vencida"].sum()
            fila[clave] = _pct(v, t_)
        serie.append(fila)

    # --- 2) Top productos por saldo en el último corte ---
    ultimo = df[df["fecha_corte"] == cortes[-1]]
    prod = (ultimo.groupby("producto", as_index=False)
            .agg(saldo=("saldo_total_cartera", "sum"), vencida=("vencida", "sum"))
            .sort_values("saldo", ascending=False).head(TOP_PRODUCTOS))
    top_productos = [{"producto": str(r.producto).strip().title(),
                      "saldoMilesM": round(r.saldo / 1e9, 2),
                      "pctVencida": _pct(r.vencida, r.saldo)} for r in prod.itertuples()]

    # --- 3) Saldos por calificación de riesgo A–E (último corte) ---
    calif_cols = [f"riesgo_{letra}_saldo" for letra in "ABCDE"]
    calif_sums = ultimo[calif_cols].sum()
    calif_total = calif_sums.sum() or 1
    calificacion = [{"letra": letra, "saldoMilesM": round(calif_sums[f"riesgo_{letra}_saldo"] / 1e9, 2),
                     "pct": round(calif_sums[f"riesgo_{letra}_saldo"] / calif_total * 100, 1)} for letra in "ABCDE"]

    # --- 4) ICETEX: top departamentos por % de cartera vencida (últ. corte) ---
    icetex_top = []
    if ICETEX.exists():
        di = pd.read_csv(ICETEX, parse_dates=["fecha_corte"])
        if not di.empty and "indicador_cartera_vencida" in di.columns:
            ult = di[di["fecha_corte"] == di["fecha_corte"].max()]
            geo = (ult.groupby("departamento", as_index=False)["indicador_cartera_vencida"]
                   .mean().sort_values("indicador_cartera_vencida", ascending=False).head(TOP_DEPTOS))
            icetex_top = [{"departamento": str(r.departamento).strip().title(),
                           "pctVencida": round(r.indicador_cartera_vencida * 100, 2)} for r in geo.itertuples()]

    # --- 5) IEFIC: diccionario de variables (opcional, no rompe si falla) ---
    iefic = {"total": 0, "vars": []}
    try:
        import sys as _sys
        if str(BASE) not in _sys.path:
            _sys.path.insert(0, str(BASE))
        from src.utils.loaders import load_iefic_codebook
        cb = load_iefic_codebook()
        iefic["total"] = int(len(cb))
        iefic["vars"] = [{"n": str(r.name), "l": (str(r.label) or str(r.question) or "")[:90]}
                         for r in cb.itertuples()]
    except Exception as e:
        print("IEFIC omitida:", e)

    return {"serieVencida": serie, "topProductos": top_productos, "calificacion": calificacion,
            "icetexTop": icetex_top, "iefic": iefic,
            "meta": {"desde": pd.Timestamp(cortes[0]).strftime("%Y-%m"), "hasta": pd.Timestamp(cortes[-1]).strftime("%Y-%m"),
                     "filasSfc": int(len(df)), "generado": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}}


def main() -> None:
    """Punto de entrada CLI: genera ``datos_sistema.js`` en disco.

    Escribe el archivo ``proyecto_riesgo_express/datos_sistema.js`` con la
    constante global ``DATOS_SISTEMA`` (JSON indentado, UTF-8) e imprime un
    resumen con el tamaño y el rango de cortes exportados.
    """
    datos = generar_datos()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "// Generado por src/utils/exportar_agregados_dashboard.py — NO editar a mano\n"
    js += "const DATOS_SISTEMA = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"OK -> {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
    print(f"   serie: {len(datos['serieVencida'])} cortes ({datos['meta']['desde']} a {datos['meta']['hasta']})")


if __name__ == "__main__":
    main()
