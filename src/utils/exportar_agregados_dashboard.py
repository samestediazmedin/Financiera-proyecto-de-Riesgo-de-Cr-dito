"""Exporta agregados BI del sistema financiero para el dashboard HTML.

Lee los CSV limpios de data/processed/ (reglas de oro: data/raw es inmutable)
y genera proyecto_riesgo_express/datos_sistema.js — un JSON liviano (< 30 KB)
consumible por el navegador con:

  * serieVencida   — evolución mensual del % de cartera vencida (últ. 24 cortes):
                     total sistema, bancos (tipo_entidad=1) y no bancarias.
  * topProductos   — top 8 productos por saldo en el último corte (saldo + % vencida).
  * calificacion   — saldos por calificación de riesgo A–E (último corte).
  * icetexTop      — top 10 departamentos por % de cartera vencida ICETEX (últ. corte).
  * meta           — rango de fechas y nº de registros procesados.

Uso:
    python src/utils/exportar_agregados_dashboard.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
SFC = BASE / "data" / "processed" / "sfc_limpio.csv"
ICETEX = BASE / "data" / "processed" / "icetex_limpio.csv"
OUT = BASE / "proyecto_riesgo_express" / "datos_sistema.js"

N_CORTES = 24
TOP_PRODUCTOS = 8
TOP_DEPTOS = 10


def _pct(vencida: float, total: float) -> float:
    return round(vencida / total * 100, 2) if total else 0.0


def main() -> None:
    # ---------------- SFC ----------------
    df = pd.read_csv(SFC, parse_dates=["fecha_corte"])
    df["vencida"] = df["saldo_total_cartera"] - df["saldo_vigente"]
    df["es_banco"] = df["tipo_entidad"] == 1

    # Serie mensual (últimos N cortes) — total / bancos / no bancarias
    cortes = sorted(df["fecha_corte"].unique())[-N_CORTES:]
    serie = []
    for corte in cortes:
        d = df[df["fecha_corte"] == corte]
        fila = {"mes": pd.Timestamp(corte).strftime("%Y-%m")}
        for clave, sub in (
            ("total", d),
            ("bancos", d[d["es_banco"]]),
            ("noBancarias", d[~d["es_banco"]]),
        ):
            t = sub["saldo_total_cartera"].sum()
            v = sub["vencida"].sum()
            fila[clave] = _pct(v, t)
        serie.append(fila)

    # Último corte
    ultimo = df[df["fecha_corte"] == cortes[-1]]

    # Top productos por saldo
    prod = (
        ultimo.groupby("producto", as_index=False)
        .agg(saldo=("saldo_total_cartera", "sum"), vencida=("vencida", "sum"))
        .sort_values("saldo", ascending=False)
        .head(TOP_PRODUCTOS)
    )
    top_productos = [
        {
            "producto": str(r.producto).strip().title(),
            "saldoMilesM": round(r.saldo / 1e9, 2),          # miles de millones COP
            "pctVencida": _pct(r.vencida, r.saldo),
        }
        for r in prod.itertuples()
    ]

    # Calificación A–E
    calif_cols = [f"riesgo_{letra}_saldo" for letra in "ABCDE"]
    calif_sums = ultimo[calif_cols].sum()
    calif_total = calif_sums.sum() or 1
    calificacion = [
        {"letra": letra, "saldoMilesM": round(calif_sums[f"riesgo_{letra}_saldo"] / 1e9, 2),
         "pct": round(calif_sums[f"riesgo_{letra}_saldo"] / calif_total * 100, 1)}
        for letra in "ABCDE"
    ]

    # ---------------- ICETEX ----------------
    icetex_top: list[dict] = []
    if ICETEX.exists():
        di = pd.read_csv(ICETEX, parse_dates=["fecha_corte"])
        if not di.empty and "indicador_cartera_vencida" in di.columns:
            ult = di[di["fecha_corte"] == di["fecha_corte"].max()]
            geo = (
                ult.groupby("departamento", as_index=False)["indicador_cartera_vencida"]
                .mean()
                .sort_values("indicador_cartera_vencida", ascending=False)
                .head(TOP_DEPTOS)
            )
            icetex_top = [
                {"departamento": str(r.departamento).strip().title(),
                 "pctVencida": round(r.indicador_cartera_vencida * 100, 2)}
                for r in geo.itertuples()
            ]

    datos = {
        "serieVencida": serie,
        "topProductos": top_productos,
        "calificacion": calificacion,
        "icetexTop": icetex_top,
        "meta": {
            "desde": pd.Timestamp(cortes[0]).strftime("%Y-%m"),
            "hasta": pd.Timestamp(cortes[-1]).strftime("%Y-%m"),
            "filasSfc": int(len(df)),
            "generado": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "// Generado por src/utils/exportar_agregados_dashboard.py — NO editar a mano\n"
    js += "const DATOS_SISTEMA = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"OK -> {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
    print(f"   serie: {len(serie)} cortes ({datos['meta']['desde']} a {datos['meta']['hasta']})")
    print(f"   productos: {len(top_productos)} · calificación A-E · icetex: {len(icetex_top)} deptos")


if __name__ == "__main__":
    main()
