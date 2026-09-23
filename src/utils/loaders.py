"""Carga y normalización de los datasets del proyecto de riesgo de crédito.

Propósito
---------
Única fuente de verdad para leer los datos crudos de ``data/raw/`` y entregar
DataFrames limpios y tipados. La usan los notebooks (01–05), el dashboard
``app.py`` y el exportador de agregados BI.

Reglas de oro
-------------
- Nunca modificar ``data/raw/`` (datos crudos inmutables); lo limpio se
  guarda en ``data/processed/`` vía :func:`save_processed`.
- Formatos de monto colombianos (¡son DIFERENTES entre datasets!):
    * ICETEX:  '$ 14,629,091'  -> comas = separador de miles  -> 14629091.0
    * SFC:     '37.651.351.298' / '32.878.868.825,55' -> puntos = miles, coma = decimal
- Fechas ICETEX: '2022 Mar 31 12:00:00 AM' -> pd.to_datetime con format.
- CSV de SFC: separador coma, encoding UTF-8 (verificado por bytes; AGENTS.md
  indicaba ';' y latin-1 pero el archivo descargado no los usa).
- XML de BANREP: requiere lxml.

Documentado: 2026-09-18.
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
    """Convierte un valor a ``float`` de forma tolerante.

    Helper privado compartido por todos los parsers de este módulo.

    Args:
        s: Valor de entrada (str, float, None...).

    Returns:
        float: El número parseado, o ``np.nan`` si es nulo, vacío,
        pertenece a ``{"-", "NA", "N/A"}`` o no es numérico.
    """
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
    """Parsea un monto con formato ICETEX: comas = miles, sin decimales.

    Args:
        s: Cadena tipo ``'$ 14,629,091'`` (el ``$`` es opcional).

    Returns:
        float: ``14629091.0``, o ``np.nan`` si el valor es nulo/vacío.
    """
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip()
    if s.startswith("$"):
        s = s[1:].strip()
    s = s.replace(",", "")
    return _to_float(s)


def parse_monto_sfc(s) -> float:
    """Parsea un monto con formato SFC: puntos = miles, coma = decimal.

    Args:
        s: Cadena tipo ``'37.651.351.298'`` o ``'32.878.868.825,55'``.

    Returns:
        float: ``37651351298.0`` / ``32878868825.55``, o ``np.nan`` si el
        valor es nulo/vacío.
    """
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".")
    return _to_float(s)


def parse_porcentaje(s) -> float:
    """Parsea un porcentaje textual a número (sin el factor 1/100).

    Args:
        s: Cadena tipo ``'34.21%'`` o ``'100%'`` (coma o punto decimal).

    Returns:
        float: ``34.21`` / ``100.0``, o ``np.nan`` si el valor es nulo/vacío.
    """
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip().replace("%", "").replace(",", ".")
    return _to_float(s)


def parse_cantidad(s) -> float:
    """Parsea una cantidad entera con comas de miles.

    Args:
        s: Cadena tipo ``'3,355'`` (conteos de créditos/clientes).

    Returns:
        float: ``3355.0``, o ``np.nan`` si el valor es nulo/vacío.
    """
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return np.nan
    s = str(s).strip().replace(",", "")
    return _to_float(s)


# ---------------------------------------------------------------------------
# Cargadores
# ---------------------------------------------------------------------------

def load_icetex(path: Path | str | None = None) -> pd.DataFrame:
    """Carga y normaliza Comportamiento_de_Cartera_y_Crédito (ICETEX).

    Transformaciones aplicadas:
        - ``FECHA CORTE`` → ``datetime`` (formato ``'%Y %b %d %I:%M:%S %p'``).
        - Saldos y cantidades parseados con :func:`parse_monto_icetex` /
          :func:`parse_cantidad`; indicador con :func:`parse_porcentaje`.
        - Columnas renombradas de MAYÚSCULAS con espacios a snake_case
          (``saldo_total``, ``indicador_cartera_vencida``, ...).

    Args:
        path: Ruta al CSV crudo; por defecto el de ``data/raw/``.

    Returns:
        pandas.DataFrame: DataFrame limpio con columnas normalizadas.
    """
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
# Estructura: entidad/producto/renglón + saldos (total, vigente, vencida por rangos
# de meses) + clientes en mora + calificación de riesgo A–E (clientes y saldo).
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
    # Columnas monetarias del SFC: se parsean con parse_monto_sfc (punto=miles).
    "saldo_total_cartera", "saldo_vigente",
    "vencida_1_2_meses", "vencida_2_3_meses", "vencida_1_3_meses",
    "vencida_3_4_meses", "vencida_mas_4_meses", "vencida_3_6_meses", "vencida_mas_6_meses",
    "vencida_1_4_meses", "vencida_4_6_meses", "vencida_6_12_meses",
    "vencida_12_18_meses", "vencida_mas_12_meses", "vencida_mas_18_meses",
    "riesgo_A_saldo", "riesgo_B_saldo", "riesgo_C_saldo", "riesgo_D_saldo", "riesgo_E_saldo",
}

SFC_CLIENTE_COLS = [
    # Columnas de conteo de clientes: se parsean con parse_cantidad (coma=miles).
    "clientes_mora_mas_30",
    "riesgo_A_clientes", "riesgo_B_clientes", "riesgo_C_clientes",
    "riesgo_D_clientes", "riesgo_E_clientes",
]


def load_sfc(path: Path | str | None = None) -> pd.DataFrame:
    """Carga y normaliza Distribución_de_cartera_por_producto (Superfinanciera).

    Transformaciones aplicadas:
        - Lectura sin cabecera (``header=None``) y asignación de nombres
          limpios por posición desde :data:`SFC_COLUMNS`.
        - ``fecha_corte`` → ``datetime`` (formato ``'%d/%m/%Y'``).
        - Montos con :func:`parse_monto_sfc` y conteos de clientes con
          :func:`parse_cantidad`.

    Nota: el archivo real usa separador coma y encoding UTF-8 (AGENTS.md
    indicaba ';' y latin-1 pero el archivo descargado no los usa).

    Args:
        path: Ruta al CSV crudo; por defecto el de ``data/raw/``.

    Returns:
        pandas.DataFrame: DataFrame limpio (~110k filas × 34 columnas).
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

    Recorre los nodos ``<var>`` del estándar DDI y extrae nombre (``name``),
    etiqueta (``labl``), literal de pregunta (``qstnLit``) y tipo de
    intervalo (``intrvl``).

    El XML define cada variable por archivo (F17=IEFIC_2017, F18=IEFIC_2018),
    por lo que se deduplica por nombre (331 variables únicas).

    Args:
        path: Ruta al XML crudo de BANREP; por defecto el de ``data/raw/``.

    Returns:
        pandas.DataFrame: Columnas ``name``, ``label``, ``question``, ``type``.
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
    """Guarda un DataFrame limpio en ``data/processed/`` (CSV UTF-8 con BOM).

    Crea el directorio de salida si no existe. Los archivos generados son
    los que consumen ``app.py`` y ``exportar_agregados_dashboard.py``.

    Args:
        df: DataFrame ya limpio y normalizado.
        name: Nombre del archivo destino (p. ej. ``"sfc_limpio.csv"``).

    Returns:
        Path: Ruta absoluta del archivo escrito.
    """
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / name
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out