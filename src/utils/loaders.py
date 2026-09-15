"""Carga y normalización de los datasets del proyecto de riesgo de crédito.

Reglas de oro:
- Nunca modificar data/raw/ (datos crudos inmutables).
- Formatos de monto colombianos (¡son DIFERENTES entre datasets!):
    * ICETEX:  '$ 14,629,091'  -> comas = separador de miles  -> 14629091.0
    * SFC:     '37.651.351.298' / '32.878.868.825,55' -> puntos = miles, coma = decimal
- Fechas ICETEX: '2022 Mar 31 12:00:00 AM' -> pd.to_datetime con format.
- CSV de SFC: separador coma, encoding UTF-8 (verificado por bytes; AGENTS.md
  indicaba ';' y latin-1 pero el archivo descargado no los usa).
- XML de BANREP: requiere lxml.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"

# ---------------------------------------------------------------------------
# Utilidades de parseo
# ---------------------------------------------------------------------------

def _to_float(s) -> float:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip()
    if not s or s in {"-", "NA", "N/A"}:
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def parse_monto_icetex(s) -> float:
    """'$ 14,629,091' -> 14629091.0  (comas = miles, sin decimales)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip()
    if s.startswith("$"):
        s = s[1:].strip()
    s = s.replace(",", "")
    return _to_float(s)


def parse_monto_sfc(s) -> float:
    """'37.651.351.298' -> 37651351298.0 ; '32.878.868.825,55' -> 32878868825.55
    (puntos = miles, coma = decimal)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".")
    return _to_float(s)


def parse_porcentaje(s) -> float:
    """'34.21%' o '100%' -> 34.21 / 100.0."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip().replace("%", "").replace(",", ".")
    return _to_float(s)


def parse_cantidad(s) -> float:
    """'3,355' -> 3355.0 (comas de miles)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip().replace(",", "")
    return _to_float(s)


# ---------------------------------------------------------------------------
# Cargadores
# ---------------------------------------------------------------------------

def load_icetex(path: Path | str | None = None) -> pd.DataFrame:
    """Carga y normaliza Comportamiento_de_Cartera_y_Crédito (ICETEX)."""
    path = Path(path) if path else RAW / "Comportamiento_de_Cartera_y_Crédito._20260914.csv"
    df = pd.read_csv(path)

    df["FECHA CORTE"] = pd.to_datetime(df["FECHA CORTE"], format="%Y %b %d %I:%M:%S %p")

    for c in ["SALDO CAPITAL", "SALDO TOTAL", "SALDO MORA"]:
        df[c] = df[c].map(parse_monto_icetex)

    for c in ["CANTIDAD CREDITOS AL DIA", "CANTIDAD CREDITOS CON MORA MENOR A 90 DIAS",
              "CANTIDAD CREDITOS MORA MAYOR A 90 DIAS", "TOTAL CREDITOS"]:
        df[c] = df[c].map(parse_cantidad)

    df["INDICADOR CARTERA VENCIDA"] = df["INDICADOR CARTERA VENCIDA"].map(parse_porcentaje)

    df = df.rename(columns={
        "FECHA CORTE": "fecha_corte",
        "DEPTORESIDENCIA": "departamento",
        "CANTIDAD CREDITOS AL DIA": "creditos_al_dia",
        "CANTIDAD CREDITOS CON MORA MENOR A 90 DIAS": "creditos_mora_menor_90",
        "CANTIDAD CREDITOS MORA MAYOR A 90 DIAS": "creditos_mora_mayor_90",
        "TOTAL CREDITOS": "total_creditos",
        "SALDO CAPITAL": "saldo_capital",
        "SALDO TOTAL": "saldo_total",
        "SALDO MORA": "saldo_mora",
        "INDICADOR CARTERA VENCIDA": "indicador_cartera_vencida",
        "EPOCA CARTERA": "epoca_cartera",
    })
    return df


# Nombres limpios para las 34 columnas del SFC (por posición, evita problemas de encoding)
SFC_COLUMNS = [
    "tipo_entidad", "codigo_entidad", "entidad", "fecha_corte", "unicap", "producto",
    "renglon", "desc_renglon",
    "saldo_total_cartera", "saldo_vigente",
    "vencida_1_2_meses", "vencida_2_3_meses", "vencida_1_3_meses",
    "vencida_3_4_meses", "vencida_mas_4_meses", "vencida_3_6_meses", "vencida_mas_6_meses",
    "vencida_1_4_meses", "vencida_4_6_meses", "vencida_6_12_meses",
    "vencida_12_18_meses", "vencida_mas_12_meses", "vencida_mas_18_meses",
    "clientes_mora_mas_30",
    "riesgo_A_clientes", "riesgo_A_saldo",
    "riesgo_B_clientes", "riesgo_B_saldo",
    "riesgo_C_clientes", "riesgo_C_saldo",
    "riesgo_D_clientes", "riesgo_D_saldo",
    "riesgo_E_clientes", "riesgo_E_saldo",
]

SFC_MONTO_COLS = {
    "saldo_total_cartera", "saldo_vigente",
    "vencida_1_2_meses", "vencida_2_3_meses", "vencida_1_3_meses",
    "vencida_3_4_meses", "vencida_mas_4_meses", "vencida_3_6_meses", "vencida_mas_6_meses",
    "vencida_1_4_meses", "vencida_4_6_meses", "vencida_6_12_meses",
    "vencida_12_18_meses", "vencida_mas_12_meses", "vencida_mas_18_meses",
    "riesgo_A_saldo", "riesgo_B_saldo", "riesgo_C_saldo", "riesgo_D_saldo", "riesgo_E_saldo",
}

SFC_CLIENTE_COLS = [
    "clientes_mora_mas_30",
    "riesgo_A_clientes", "riesgo_B_clientes", "riesgo_C_clientes",
    "riesgo_D_clientes", "riesgo_E_clientes",
]


def load_sfc(path: Path | str | None = None) -> pd.DataFrame:
    """Carga y normaliza Distribución_de_cartera_por_producto (Superfinanciera).

    Nota: el archivo real usa separador coma y encoding UTF-8 (AGENTS.md
    indicaba ';' y latin-1 pero el archivo descargado no los usa).
    """
    path = Path(path) if path else RAW / "Distribución_de_cartera_por_producto_20260914.csv"
    df = pd.read_csv(path, sep=",", encoding="utf-8", low_memory=False, header=None, skiprows=1)
    df.columns = SFC_COLUMNS

    df["fecha_corte"] = pd.to_datetime(df["fecha_corte"], format="%d/%m/%Y")

    for c in SFC_MONTO_COLS:
        df[c] = df[c].map(parse_monto_sfc)

    for c in SFC_CLIENTE_COLS:
        df[c] = df[c].map(parse_cantidad)

    return df


def load_iefic_codebook(path: Path | str | None = None) -> pd.DataFrame:
    """Extrae el diccionario de variables del codebook DDI de la IEFIC (XML).

    El XML define cada variable por archivo (F17=IEFIC_2017, F18=IEFIC_2018),
    por lo que se deduplica por nombre (331 variables únicas).
    """
    from lxml import etree

    path = Path(path) if path else RAW / "BANREP-IEFIC-2017-2018.xml"
    tree = etree.parse(str(path))
    ns = {"ddi": "http://www.icpsr.umich.edu/DDI"}

    rows = []
    for var in tree.xpath("//ddi:var", namespaces=ns):
        name = var.get("name")
        labl = var.findtext("ddi:labl", default="", namespaces=ns)
        qstn = var.findtext("ddi:qstn/ddi:qstnLit", default="", namespaces=ns)
        intrvl = var.get("intrvl")
        rows.append({
            "name": name,
            "label": (labl or "").strip(),
            "question": (qstn or "").strip(),
            "type": intrvl,
        })
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset="name", keep="first").reset_index(drop=True)
    return df


def save_processed(df: pd.DataFrame, name: str) -> Path:
    """Guarda un DataFrame limpio en data/processed/ (CSV UTF-8)."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / name
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out