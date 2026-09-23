"""Asesor de riesgo financiero con IA (Google Gemini) — v2.

Propósito
---------
Convierte los agregados de la cartera SFC en contexto para el modelo Gemini
y responde preguntas de negocio en lenguaje natural (pestaña "Asesor IA"
del dashboard Streamlit). Sin key configurada el asesor responde con un
aviso amigable y la app sigue funcionando con normalidad.

Configuración de la API key (cualquiera de las dos):
  1) Variable de entorno:  GEMINI_API_KEY
  2) Archivo .env en la raíz del proyecto con:  GEMINI_API_KEY=tu_key

La key se obtiene gratis en https://aistudio.google.com

Documentado: 2026-09-18.
"""
from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Modelos por orden de preferencia (Google retira versiones antiguas para
# usuarios nuevos; 404 => probar el siguiente).
MODELOS = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash"]


def _cargar_dotenv() -> None:
    """Carga ``GEMINI_API_KEY`` desde el ``.env`` del proyecto si no viene en el entorno.

    Implementación mínima de dotenv: recorre el archivo línea a línea,
    localiza la clave ``GEMINI_API_KEY`` y la vuelca en ``os.environ``
    (quitando comillas y espacios). No sobrescribe un valor ya existente
    en el entorno.
    """
    if os.getenv("GEMINI_API_KEY"):
        return
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8-sig").splitlines():
            linea = linea.strip()
            if linea.startswith("GEMINI_API_KEY") and "=" in linea:
                os.environ["GEMINI_API_KEY"] = linea.split("=", 1)[1].strip().strip('"').strip("'")


def consultar_asesor_gemini(pregunta: str, resumen: dict, top_entidades: str = "") -> str:
    """Consulta a Gemini con el contexto de la cartera; devuelve texto siempre.

    Construye un prompt de sistema (rol de analista senior de riesgo de
    crédito en Colombia) con los agregados del filtro activo del dashboard
    y prueba en orden los modelos de :data:`MODELOS` (si uno responde 404,
    pasa al siguiente).

    Args:
        pregunta: Pregunta del usuario en lenguaje natural.
        resumen: Agregados del filtro activo; claves esperadas
            ``total_monto``, ``pct_vencida``, ``registros``,
            ``cant_alto_riesgo`` y ``score_prom``.
        top_entidades: Texto opcional con las entidades de mayor %
            vencida para dar más contexto al modelo.

    Returns:
        str: Respuesta del modelo en Markdown, o un mensaje de aviso
        (key faltante, librería no instalada, o error del último intento).
        Nunca lanza excepciones hacia la capa de UI.
    """
    _cargar_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "tu_api_key_aqui":
        return (
            "⚠️ **Asesor IA no activo**: falta configurar `GEMINI_API_KEY`.\n\n"
            "1. Crea una key gratis en [aistudio.google.com](https://aistudio.google.com)\n"
            "2. Crea un archivo `.env` en la raíz del proyecto con: `GEMINI_API_KEY=tu_key`\n"
            "   (o ejecuta `setx GEMINI_API_KEY \"tu_key\"` y reinicia Streamlit)\n\n"
            "El resto del dashboard funciona normalmente sin la key."
        )

    try:
        from google import genai
    except ImportError:
        return "⚠️ Falta la librería. Instala con:\n\n```\n.venv\\Scripts\\pip install google-genai\n```"

    contexto = f"""Contexto de la cartera analizada (Superfinanciera, datos reales):
- Exposición total filtrada: ${resumen.get('total_monto', 0):,.0f} COP
- % cartera vencida del conjunto: {resumen.get('pct_vencida', 0):.2f}%
- Registros en el filtro: {resumen.get('registros', 0):,}
- Registros clasificados Alto riesgo: {resumen.get('cant_alto_riesgo', 0):,}
- Score proxy promedio (0-1000): {resumen.get('score_prom', 0)}
{top_entidades}"""

    prompt = f"""Eres un analista senior de riesgo de crédito en Colombia, pragmático y claro.
{contexto}

Pregunta del usuario: {pregunta}

Responde en español, ejecutivo y conciso (máx. 6 viñetas o 3 párrafos).
Usa cifras del contexto cuando aporten. Si la pregunta requiere datos que no
están en el contexto, dilo explícitamente y sugiere qué filtro aplicar en el
dashboard para obtenerlos."""

    client = genai.Client(api_key=api_key)
    ultimo_error: Exception | None = None
    for modelo in MODELOS:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            return response.text or "_(sin respuesta del modelo)_"
        except Exception as e:
            ultimo_error = e
            # 404/NOT_FOUND => modelo retirado, probar el siguiente; otros errores, salir
            if "404" not in str(e) and "NOT_FOUND" not in str(e):
                break
    return f"❌ Error al consultar Gemini: {ultimo_error}"


def sugerencias_rapidas() -> list[str]:
    """Devuelve 3 preguntas sugeridas para los botones preset del dashboard.

    Returns:
        list[str]: Preguntas de negocio listas para consultar al asesor.
    """
    return [
        "¿Qué acciones tomarías con los registros de alto riesgo?",
        "Resume la salud de la cartera en 3 conclusiones ejecutivas",
        "¿Qué productos o entidades merecen monitoreo intensivo y por qué?",
    ]
